#!/usr/bin/env python3
"""Create the "NÉE Search - Name Change" Search campaign via the Google Ads API.

Reads the SAME assets the Google Ads Editor workflow uses, so the API build stays in
sync with campaign-plan.md:
  - keywords.csv           -> ad groups + keywords (+ per-keyword max CPC)
  - negative-keywords.csv  -> campaign-level negatives
  - RSA_ASSETS (below)     -> one responsive search ad per ad group (from plan §3)

Safety:
  - Builds everything **PAUSED**. Nothing spends until you enable it in the UI.
  - `--dry-run` prints the full plan and makes ZERO API calls (works with no creds).

Secrets (env or Infisical) — see api-setup.md:
  GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
  GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID  (the Akila MCC),
  GOOGLE_ADS_CUSTOMER_ID  (the NÉE child account campaigns land in; digits only)

Run:
  uv run python create_campaign.py --dry-run          # preview, no API calls
  uv add google-ads
  uv run python create_campaign.py                    # creates everything PAUSED
"""
import argparse
import csv
import os
import sys
import time

CAMPAIGN_NAME = "NÉE Search - Name Change"
DAILY_BUDGET_USD = 32.0           # plan §1: core campaign gets $32/day of the $40
MAX_CPC_CEILING_USD = 4.00        # plan §1: Maximize Clicks with a $4.00 CPC cap
US_GEO = "geoTargetConstants/2840"
EN_LANG = "languageConstants/1000"

LUXE_URL = "https://neenamechange.com/collections/frontpage/products/luxe-kit-mail-delivery"
GUIDE_URL = "https://neenamechange.com/blogs/name-change-guide"

# Final URL per ad group (plan §2). After Marriage skews informational -> pillar guide.
FINAL_URLS = {
    "Name Change Kit": LUXE_URL,
    "After Marriage": GUIDE_URL,
    "Name Change Service": LUXE_URL,
}

# Responsive Search Ad copy from campaign-plan.md §3. Headlines <=30 chars, descriptions <=90.
RSA_ASSETS = {
    "Name Change Kit": {
        "headlines": [
            "Luxe Name Change Kit", "Name Change Kit For Brides", "All Your Forms, Done For You",
            "Change Your Name In Minutes", "Mailed Right To Your Door", "Valid In All 50 States",
            "The Luxury Name Change Kit", "Step-By-Step Name Change", "Newlywed Name Change Kit",
            "Skip The Paperwork Stress", "Designed By Brides, For You", "Shop The NÉE Kit",
            "From $39 — Start Today", "SSA, Passport, DMV & More", "Happiness Guarantee",
        ],
        "descriptions": [
            "Every form to change your name after marriage—personalized & mailed to your door.",
            "Skip the research. NÉE walks you through SSA, passport, DMV & more, step by step.",
            "The elevated name change kit loved by newlyweds. Valid in all 50 states.",
            "Pop the champagne—we'll handle the paperwork. Shop the Luxe Kit from $39.",
        ],
    },
    "After Marriage": {
        "headlines": [
            "Name Change After Marriage", "Change Your Name, Made Easy", "All Your Forms, Done For You",
            "Married? Change Your Name", "Mailed Right To Your Door", "Valid In All 50 States",
            "Step-By-Step Name Change", "Newlywed Name Change Kit", "Skip The Paperwork Stress",
            "SSA, Passport, DMV & More", "The Luxury Name Change Kit", "Start Your Name Change Today",
            "Designed By Brides, For You", "From $39 — Get Started", "Happiness Guarantee",
        ],
        "descriptions": [
            "Changing your name after marriage? Get every form you need, personalized & mailed.",
            "The complete name change kit: SSA, passport, DMV, IRS & more. Step by step.",
            "Skip hours of government research. NÉE makes your name change simple & beautiful.",
            "Loved by newlyweds. Valid in all 50 states. Start today from $39.",
        ],
    },
    "Name Change Service": {
        "headlines": [
            "Name Change Service", "Name Change, Done For You", "The Easy Name Change Kit",
            "All Your Forms In One Kit", "Valid In All 50 States", "Mailed Right To Your Door",
            "SSA, Passport, DMV & More", "Step-By-Step Instructions", "Loved By Newlyweds",
            "From $39 — Start Today", "Skip The Research", "The Luxury Name Change Kit",
            "Designed By Brides", "Happiness Guarantee", "Shop NÉE Name Change",
        ],
        "descriptions": [
            "Your complete name change, done for you—every form personalized and mailed home.",
            "Not sure where to start? NÉE's kit covers SSA, passport, DMV, IRS & 4,000+ accounts.",
            "The simple, beautiful way to change your name after marriage. All 50 states.",
            "Skip the stress and the research. Start your name change today from $39.",
        ],
    },
}

MATCH = {"exact": "EXACT", "phrase": "PHRASE", "broad": "BROAD"}


def usd_to_micros(usd: float) -> int:
    return round(float(usd) * 1_000_000)


def read_keywords(path: str):
    """keywords.csv -> {ad_group: [(text, match_type, max_cpc_usd), ...]} for our campaign."""
    groups: dict[str, list] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["Campaign"].strip() != CAMPAIGN_NAME:
                continue
            groups.setdefault(row["Ad Group"].strip(), []).append(
                (row["Keyword"].strip(), MATCH[row["Criterion Type"].strip().lower()],
                 float(row["Max CPC"]))
            )
    return groups


def read_negatives(path: str):
    """negative-keywords.csv -> [(text, match_type), ...] for our campaign."""
    negs = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["Campaign"].strip() != CAMPAIGN_NAME:
                continue
            negs.append((row["Keyword"].strip(), MATCH[row["Match Type"].strip().lower()]))
    return negs


def validate_rsa():
    """Google rejects headlines >30 chars / descriptions >90. Catch it before the API does."""
    problems = []
    for ag, a in RSA_ASSETS.items():
        for h in a["headlines"]:
            if len(h) > 30:
                problems.append(f"  [{ag}] headline >30 chars ({len(h)}): {h}")
        for d in a["descriptions"]:
            if len(d) > 90:
                problems.append(f"  [{ag}] description >90 chars ({len(d)}): {d}")
    return problems


# ---------------------------------------------------------------------------
# Dry-run: print the plan, no API.
# ---------------------------------------------------------------------------
def dry_run(groups, negatives):
    print(f"\n=== DRY RUN — would create (all PAUSED) ===\n")
    print(f"Campaign: {CAMPAIGN_NAME}")
    print(f"  Type: Search only (Display/partners OFF)")
    print(f"  Budget: ${DAILY_BUDGET_USD:.0f}/day   Bidding: Maximize Clicks, CPC cap ${MAX_CPC_CEILING_USD:.2f}")
    print(f"  Geo: United States   Language: English")
    print(f"  Negative keywords: {len(negatives)}")
    for ag, kws in groups.items():
        rsa = RSA_ASSETS.get(ag, {})
        print(f"\n  Ad group: {ag}  ->  {FINAL_URLS.get(ag, LUXE_URL)}")
        print(f"    {len(kws)} keywords | RSA: {len(rsa.get('headlines', []))} headlines, "
              f"{len(rsa.get('descriptions', []))} descriptions")
        for text, mt, cpc in kws:
            print(f"      - [{mt:<6}] {text}  (max ${cpc:.2f})")
    print(f"\n(no API calls made)\n")


# ---------------------------------------------------------------------------
# Live: build everything via the API, sequentially, PAUSED.
# ---------------------------------------------------------------------------
def build_live(groups, negatives, customer_id):
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    client = GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
        "use_proto_plus": True,
    })

    def svc(name):
        return client.get_service(name)

    try:
        # 1) Budget
        print("[1/5] Creating shared budget...")
        bud_op = client.get_type("CampaignBudgetOperation")
        b = bud_op.create
        b.name = f"{CAMPAIGN_NAME} budget"
        b.amount_micros = usd_to_micros(DAILY_BUDGET_USD)
        b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        b.explicitly_shared = False
        bud_res = svc("CampaignBudgetService").mutate_campaign_budgets(
            customer_id=customer_id, operations=[bud_op]).results[0].resource_name
        print(f"      budget: {bud_res}")

        # 2) Campaign (PAUSED, Search only, Maximize Clicks + CPC ceiling)
        print("[2/5] Creating campaign (PAUSED)...")
        camp_op = client.get_type("CampaignOperation")
        c = camp_op.create
        c.name = CAMPAIGN_NAME
        c.status = client.enums.CampaignStatusEnum.PAUSED
        c.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        c.campaign_budget = bud_res
        c.target_spend.cpc_bid_ceiling_micros = usd_to_micros(MAX_CPC_CEILING_USD)  # Maximize Clicks
        c.network_settings.target_google_search = True
        c.network_settings.target_search_network = False
        c.network_settings.target_content_network = False
        c.network_settings.target_partner_search_network = False
        camp_res = svc("CampaignService").mutate_campaigns(
            customer_id=customer_id, operations=[camp_op]).results[0].resource_name
        print(f"      campaign: {camp_res}")

        # 3) Campaign criteria: geo, language, negatives
        print("[3/5] Adding geo, language, and negatives...")
        crit_ops = []
        for target, attr in ((US_GEO, "location"), (EN_LANG, "language")):
            op = client.get_type("CampaignCriterionOperation")
            op.create.campaign = camp_res
            if attr == "location":
                op.create.location.geo_target_constant = target
            else:
                op.create.language.language_constant = target
            crit_ops.append(op)
        for text, mt in negatives:
            op = client.get_type("CampaignCriterionOperation")
            op.create.campaign = camp_res
            op.create.negative = True
            op.create.keyword.text = text
            op.create.keyword.match_type = client.enums.KeywordMatchTypeEnum[mt]
            crit_ops.append(op)
        svc("CampaignCriterionService").mutate_campaign_criteria(
            customer_id=customer_id, operations=crit_ops)
        print(f"      added geo + language + {len(negatives)} negatives")

        # 4) Ad groups + keywords
        print("[4/5] Creating ad groups + keywords...")
        ag_res = {}
        for ag_name, kws in groups.items():
            ag_op = client.get_type("AdGroupOperation")
            ag = ag_op.create
            ag.name = ag_name
            ag.campaign = camp_res
            ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
            ag.status = client.enums.AdGroupStatusEnum.ENABLED
            ag.cpc_bid_micros = usd_to_micros(max(c for _, _, c in kws))
            res = svc("AdGroupService").mutate_ad_groups(
                customer_id=customer_id, operations=[ag_op]).results[0].resource_name
            ag_res[ag_name] = res

            kw_ops = []
            for text, mt, cpc in kws:
                op = client.get_type("AdGroupCriterionOperation")
                cr = op.create
                cr.ad_group = res
                cr.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
                cr.keyword.text = text
                cr.keyword.match_type = client.enums.KeywordMatchTypeEnum[mt]
                cr.cpc_bid_micros = usd_to_micros(cpc)
                kw_ops.append(op)
            svc("AdGroupCriterionService").mutate_ad_group_criteria(
                customer_id=customer_id, operations=kw_ops)
            print(f"      {ag_name}: {len(kws)} keywords")

        # 5) One RSA per ad group
        print("[5/5] Creating responsive search ads...")
        for ag_name, res in ag_res.items():
            assets = RSA_ASSETS.get(ag_name)
            if not assets:
                print(f"      {ag_name}: no RSA copy, skipped")
                continue
            ad_op = client.get_type("AdGroupAdOperation")
            aga = ad_op.create
            aga.ad_group = res
            aga.status = client.enums.AdGroupAdStatusEnum.PAUSED
            aga.ad.final_urls.append(FINAL_URLS.get(ag_name, LUXE_URL))
            rsa = aga.ad.responsive_search_ad
            for h in assets["headlines"]:
                a = client.get_type("AdTextAsset")
                a.text = h
                rsa.headlines.append(a)
            for d in assets["descriptions"]:
                a = client.get_type("AdTextAsset")
                a.text = d
                rsa.descriptions.append(a)
            svc("AdGroupAdService").mutate_ad_group_ads(
                customer_id=customer_id, operations=[ad_op])
            print(f"      {ag_name}: RSA created")

        print(f"\n✅ Campaign '{CAMPAIGN_NAME}' built PAUSED in account {customer_id}.")
        print("   Review in the Google Ads UI, add assets (sitelinks/callouts), then enable.")

    except GoogleAdsException as ex:
        print(f"\n❌ Google Ads API error (request_id={ex.request_id}):")
        for err in ex.failure.errors:
            print(f"   - {err.message}")
        raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print plan, no API calls")
    args = parser.parse_args()

    t0 = time.time()
    here = os.path.dirname(os.path.abspath(__file__))
    groups = read_keywords(os.path.join(here, "keywords.csv"))
    negatives = read_negatives(os.path.join(here, "negative-keywords.csv"))
    if not groups:
        sys.exit(f"No ad groups found for campaign '{CAMPAIGN_NAME}' in keywords.csv")

    rsa_problems = validate_rsa()
    if rsa_problems:
        print("RSA length problems (fix before live run):")
        print("\n".join(rsa_problems))
        if not args.dry_run:
            sys.exit("Aborting — Google would reject these assets.")

    if args.dry_run:
        dry_run(groups, negatives)
        print(f"Total elapsed: {time.time() - t0:.2f}s")
        return 0

    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")
    needed = ["GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET",
              "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_LOGIN_CUSTOMER_ID", "GOOGLE_ADS_CUSTOMER_ID"]
    missing = [k for k in needed if not os.environ.get(k)]
    if missing:
        sys.exit("Missing env vars: " + ", ".join(missing) + "\n(Use --dry-run to preview without creds.)")

    build_live(groups, negatives, customer_id)
    print(f"Total elapsed: {time.time() - t0:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
