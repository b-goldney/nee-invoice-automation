# NÉE — Google Ads Search Campaign Blueprint

> Built from live DataForSEO keyword data (US, June 2026). DataForSEO is data-only;
> this is imported/launched in Google Ads Editor + the Google Ads UI.

## 0. Pre-launch checklist (do FIRST — do not skip conversion tracking)

- [ ] Install the **Google Ads conversion tag** OR import the **GA4 "purchase" event** as a conversion. Without this you're flying blind and Smart Bidding can't work.
- [ ] Set the conversion to **"Purchase"**, count = **One**, value = **use transaction-specific value** (Shopify passes order value).
- [ ] Confirm Shopify → Google channel: install the **Google & YouTube** Shopify app (free) — it deploys the tag + product feed automatically.
- [ ] Verify the tag fires on the order-confirmation page (Tag Assistant).

## 1. Campaign settings

| Setting | Value |
|---|---|
| Campaign type | **Search** only |
| Networks | Google Search **only** — turn OFF Display & Search Partners for the test |
| Locations | **United States**; target = "Presence: people in your targeted locations" |
| Language | English |
| Budget | **$40/day** (~$1,200/mo) to start the test |
| Bidding | Start **Maximize Clicks** with a **max CPC cap of $4.00** → switch to **Maximize Conversions / Target CPA** after ~15–30 conversions |
| Ad schedule | All day (optimize after 2–3 weeks of data) |
| Ad rotation | Optimize |

Two campaigns total so brand/competitor budgets don't get eaten by the core terms:
- **NÉE Search - Name Change** ($32/day) — ad groups: Name Change Kit, After Marriage, Name Change Service
- **NÉE Search - Brand** + **Competitor** ($8/day combined) — cheap defensive + conquesting

## 2. Ad group structure & the data behind it

| Ad group | Core keyword | Vol/mo | CPC | Intent | Landing page |
|---|---|---|---|---|---|
| **Name Change Kit** | name change kit | 2,900 | $4.06 | transactional | Luxe Kit product page |
| **After Marriage** | name change after marriage | 5,400 | $4.05 | informational→buyer | Pillar guide w/ strong CTA *or* Luxe Kit |
| **Name Change Service** | name change service | 2,400 | $5.27 | commercial | Luxe Kit / How-It-Works |
| **Brand** | nee name change kit | 90+ | $3.65 | transactional | Homepage |
| **Competitor** | newlynamed / hitchswitch | — | low | conquesting | Comparison page |

**Notes that matter:**
- *After Marriage* terms skew **informational** — searchers are researching the process. Best CVR comes from sending them to the **pillar "Name Change After Marriage Checklist" page (Lever 1)** with a sticky "Get the Kit" CTA, not cold to a product page. This is where Lever 1 and Lever 3 reinforce each other.
- *Name Change Service* searchers may expect full done-for-you concierge (HitchSwitch model). NÉE sells a guided kit — **ad copy must set that expectation** ("All your forms, done for you — mailed to your door") or CVR/refunds suffer. Bid here but watch it.
- *Competitor*: you may bid on their brand terms, but **do NOT use their trademark in your ad text** (policy + quality). Lead with your differentiation ("The luxury name change kit").

## 3. Responsive Search Ads (paste into each ad group)

### Ad group: Name Change Kit
**Headlines (15):** Luxe Name Change Kit · Name Change Kit For Brides · All Your Forms, Done For You · Change Your Name In Minutes · Mailed Right To Your Door · Valid In All 50 States · The Luxury Name Change Kit · Step-By-Step Name Change · Newlywed Name Change Kit · Skip The Paperwork Stress · Designed By Brides, For You · Shop The NÉE Kit · From $39 — Start Today · SSA, Passport, DMV & More · Happiness Guarantee
**Descriptions (4):**
1. Every form to change your name after marriage—personalized & mailed to your door.
2. Skip the research. NÉE walks you through SSA, passport, DMV & more, step by step.
3. The elevated name change kit loved by newlyweds. Valid in all 50 states.
4. Pop the champagne—we'll handle the paperwork. Shop the Luxe Kit from $39.
*Pin "Luxe Name Change Kit" / "Name Change Kit For Brides" to Headline position 1.*

### Ad group: After Marriage
**Headlines (15):** Name Change After Marriage · Change Your Name, Made Easy · All Your Forms, Done For You · Married? Change Your Name · Mailed Right To Your Door · Valid In All 50 States · Step-By-Step Name Change · Newlywed Name Change Kit · Skip The Paperwork Stress · SSA, Passport, DMV & More · The Luxury Name Change Kit · Start Your Name Change Today · Designed By Brides, For You · From $39 — Get Started · Happiness Guarantee
**Descriptions (4):**
1. Changing your name after marriage? Get every form you need, personalized & mailed.
2. The complete name change kit: SSA, passport, DMV, IRS & more. Step by step.
3. Skip hours of government research. NÉE makes your name change simple & beautiful.
4. Loved by newlyweds. Valid in all 50 states. Start today from $39.

### Ad group: Name Change Service
**Headlines (15):** Name Change Service · Name Change, Done For You · The Easy Name Change Kit · All Your Forms In One Kit · Valid In All 50 States · Mailed Right To Your Door · SSA, Passport, DMV & More · Step-By-Step Instructions · Loved By Newlyweds · From $39 — Start Today · Skip The Research · The Luxury Name Change Kit · Designed By Brides · Happiness Guarantee · Shop NÉE Name Change
**Descriptions (4):**
1. Your complete name change, done for you—every form personalized and mailed home.
2. Not sure where to start? NÉE's kit covers SSA, passport, DMV, IRS & 4,000+ accounts.
3. The simple, beautiful way to change your name after marriage. All 50 states.
4. Skip the stress and the research. Start your name change today from $39.

### Ad group: Brand
**Headlines (10):** NÉE Name Change · Official NÉE Name Change Kit · The Luxury Name Change Kit · Shop NÉE Kits From $39 · Name Change Kit For Brides · Loved By Newlyweds · Mailed Right To Your Door · Valid In All 50 States · Designed By Brides · Happiness Guarantee
**Descriptions (4):** standard brand copy + "Shop the official NÉE Luxe & Bare kits."

## 4. Ad assets (set at campaign level)

- **Sitelinks:** How It Works · What's Included · Reviews · Keepsake Boxes · Bare Kit $39 · FAQ
- **Callouts:** All 50 States · Mailed To Your Door · Designed By Brides · Step-By-Step Guide · Happiness Guarantee · 4,000+ Accounts Covered
- **Structured snippet** (Services): Social Security, Passport, Driver's License, IRS, Voter Registration, USPS
- **Price asset:** Bare Kit $39 · Luxe Kit $89 · Keepsake Box from $75
- **Image assets:** your branded kit/lifestyle photography (your visual edge over both competitors)

## 5. Negative keywords
See `negative-keywords.csv`. Key filters: free, template, pdf, deed poll, UK/AU/CA, divorce*, court order, meaning/define, social security office, gender/transgender*.
\* Reconsider `divorce` and `gender` based on whether you want to serve those audiences — both are real markets, just different messaging.

## 6. Budget allocation (at $40/day)

| Ad group | Daily | Why |
|---|---|---|
| Name Change Kit | ~$14 | highest purchase intent |
| After Marriage | ~$12 | biggest volume |
| Name Change Service | ~$6 | commercial, watch CVR |
| Brand | ~$3 | cheap, near-100% ROAS, defends against competitor bids |
| Competitor | ~$5 | optional/aggressive — pause if CPA too high |

## 7. Targets & optimization cadence

- **Math:** $40/day ÷ ~$4 CPC ≈ 10 clicks/day. At a 2–4% CVR on the kit → ~6–12 sales/mo to start. Target **CPA < ~$25–30** (kit AOV $39–$89 + keepsake upsell).
- **Week 1–2:** Maximize Clicks, watch the **Search Terms report daily**, add negatives aggressively.
- **Week 3–4:** prune wasted spend; pause keywords with spend > 2× target CPA and 0 conversions.
- **~30 conversions in:** switch to **Maximize Conversions** then **Target CPA**.
- **Ongoing:** raise budget on the winning ad group; the *After Marriage* informational traffic compounds best once the Lever 1 pillar page exists as the landing page.

## 8. How to launch from these files

1. Set up conversion tracking (Section 0).
2. In **Google Ads Editor**: Account → Import → `keywords.csv`. It creates the campaigns/ad groups/keywords.
3. Add the RSAs (Section 3) and assets (Section 4) in Editor or the UI.
4. Import `negative-keywords.csv` (or add as a shared negative list).
5. Set campaign settings (Section 1), then **Post** from Editor.
6. Start at $40/day; review in 2 weeks.
