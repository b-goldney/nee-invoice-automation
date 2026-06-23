# Google Ads API — Setup Runbook

Goal: get **write access** to your live Google Ads account from code, so the
DataForSEO research layer can feed campaigns/keywords/negatives programmatically.

You end up with **5 secrets**: `developer_token`, `client_id`, `client_secret`,
`refresh_token`, `login_customer_id`. Store them in Infisical, never in chat or git.

> ⏱ The gating step is **Basic access approval** (Step 2), reviewed by Google —
> usually 1–3 business days. Start it FIRST, do everything else while you wait.

---

## Step 1 — Use your EXISTING manager account  (~5 min)

You already have a Manager (MCC) account — **reuse it, don't create a new one.**
The developer token lives in the manager account (not a regular Ads account), and one
token covers every ad account linked under that MCC. Nothing to migrate.

1. Sign into the **manager account** at <https://ads.google.com> (the MCC, not the child
   ad account). Confirm your live NÉE ad account is listed under **Accounts → Sub-account list**.
   - If it isn't linked yet: **Accounts → +  → Link existing account** → enter the live
     account's **Customer ID** → approve the request from inside that account.
2. Note two IDs from the top bar (digits only, drop the dashes):
   - **MCC Customer ID** → becomes `login_customer_id` (you authenticate *through* this)
   - **Live ad account Customer ID** → the account campaigns are actually created in

> The CSV/Google Ads Editor workflow in `campaign-plan.md` already posts to this same
> account through this same MCC — the API just does it programmatically with the same hierarchy.

---

## Step 2 — Get the developer token + apply for Basic access  (START THIS FIRST)

1. Sign into the **Manager (MCC)** account (API Center only appears in MCC accounts).
2. Top-right wrench **Tools and settings → Setup → API Center**.
3. Accept the terms → a **developer token** is generated. Copy it.
   - ⚠️ A brand-new token has **Test account access only** — it can't touch real campaigns.
4. On the same API Center page, click **Apply for Basic access** and fill the form:
   - **API use case**: "First-party advertiser managing our own Google Ads campaigns —
     bulk keyword/campaign management and reporting. Not resold to third parties."
   - **Tool type**: internal / in-house tool, single company (NÉE / neenamechange.com).
   - Provide the website, contact email (brandon@akilaanalytics.com).
   - Answer compliance questions truthfully — you're not building a public tool.
5. Submit. Approval email typically arrives in **1–3 business days**.

While it's pending you can already authenticate against a **test account**, so do Steps 3–5 now.

---

## Step 3 — Google Cloud project + OAuth client  (~10 min)

1. <https://console.cloud.google.com> → create/select a project (e.g. "nee-ads-api").
2. **APIs & Services → Library** → search **Google Ads API** → **Enable**.
3. **APIs & Services → OAuth consent screen**:
   - User type **External** → fill app name, your email.
   - Under **Test users**, add `brandon@akilaanalytics.com` (and whoever runs the script).
   - You do NOT need to publish/verify the app — test mode is fine for an internal refresh token.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**:
   - Application type **Desktop app** → name it → **Create**.
   - **Download JSON** → save it as `client_secret.json` in this folder (it's gitignored below).

---

## Step 4 — Generate the refresh token  (one command)

```bash
cd nee-google-ads
uv add google-auth-oauthlib            # one-time dep
uv run python google_oauth.py          # opens a browser, you click "Allow"
```

The script prints your **refresh_token**. Copy it. (Scope: `https://www.googleapis.com/auth/adwords`.)

---

## Step 5 — Store secrets + smoke test  (~10 min)

1. Put all five values in Infisical (project `akila-primary-ab-kk`), e.g. keys:
   `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`,
   `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`.
2. Install the client + run the smoke test:
   ```bash
   uv add google-ads
   uv run python smoke_test.py          # lists accessible customers — proves the chain works
   ```
3. If it returns your customer ID(s): ✅ you're connected. If it says
   *"developer token is not approved"*, Basic access (Step 2) hasn't landed yet —
   the test account still works for building/validating code meanwhile.

---

## What each secret is for

| Secret | Where it came from | Role |
|---|---|---|
| `developer_token` | MCC → API Center (Step 2) | Authorizes your app to use the API at all |
| `client_id` / `client_secret` | Cloud OAuth client (Step 3) | Identifies the app in the OAuth handshake |
| `refresh_token` | `google_oauth.py` (Step 4) | Long-lived user grant → mints access tokens |
| `login_customer_id` | MCC Customer ID (Step 1) | The manager account you call "through" |

---

## Gotchas

- **`login_customer_id` must be the MCC**, not the ad account. Operations target the
  ad account's customer ID; you authenticate *through* the manager.
- Digits only — strip the dashes from all customer IDs.
- Don't commit `client_secret.json` or `google-ads.yaml` (see `.gitignore`).
- Basic access caps at ~15k operations/day — plenty for campaign building; apply for
  Standard later only if you automate high-frequency reporting.
