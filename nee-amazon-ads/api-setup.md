# Amazon Ads API — Setup Runbook

Goal: get **write access** to your live Amazon Advertising account from code
(Sponsored Products / Brands), so DataForSEO research can feed keywords and bids.

You end up with **4 secrets**: `client_id`, `client_secret`, `refresh_token`,
`profile_id`. Store them in Infisical, never in chat or git.

> ⏱ The gating step is **API access approval** (Step 2), reviewed by Amazon.
> First-party (managing your own account) is the easier path but still gated —
> start it FIRST, do everything else while you wait.

---

## Step 1 — Create a Login with Amazon (LwA) security profile  (~10 min)

1. Go to <https://developer.amazon.com> → sign in with the Amazon account that owns
   (or is admin on) your Advertising account.
2. **Apps & Services → Login with Amazon → Create a New Security Profile**.
3. Fill:
   - **Name**: "NÉE Ads Automation"
   - **Description**: internal campaign management for neenamechange.com
   - **Consent Privacy Notice URL**: `https://neenamechange.com/policies/privacy-policy`
4. Save → open the profile → **Web Settings** tab:
   - **Allowed Return URLs** → add `https://localhost:8443` (used by the OAuth helper).
   - Copy the **Client ID** and **Client Secret**.

---

## Step 2 — Request Amazon Ads API access  (START THIS FIRST)

1. Open the onboarding guide: <https://advertising.amazon.com/API/docs/en-us/guides/onboarding/overview>
2. Submit the **API access request** form, associating the LwA app from Step 1.
   - **Use case**: "First-party advertiser. We manage our own Sponsored Products /
     Sponsored Brands campaigns for our brand (NÉE / neenamechange.com). Not a
     third-party tool or reseller."
   - Provide brand, marketplace (**US / North America**), contact email.
3. Submit and wait for the approval email. (If you also need the **Amazon Marketing
   Stream** or **Brand Metrics**, request those later — not needed to start.)

---

## Step 3 — Generate the refresh token  (one command)

Once the LwA app exists (you don't strictly need Step 2 approved to mint the token,
but API *calls* will 403 until approval lands):

```bash
cd nee-amazon-ads
uv add requests
export AMZN_ADS_CLIENT_ID="amzn1.application-oa2-client.xxxx"
export AMZN_ADS_CLIENT_SECRET="xxxx"
uv run python amazon_oauth.py
```

The script prints an authorization URL → open it, sign in, click **Allow** → you're
redirected to `https://localhost:8443/?code=...` (the page won't load, that's fine) →
paste the full redirected URL back into the script → it prints your **refresh_token**.

Scope used: `cpc_advertising:campaign_management`.

---

## Step 4 — Get your profile ID + smoke test  (~5 min)

```bash
export AMZN_ADS_REFRESH_TOKEN="Atzr|xxxx"
uv run python amazon_profiles.py     # lists profiles → pick the US one's profileId
```

Each marketplace/account is a **profile**. Copy the `profileId` for the US
marketplace (`countryCode: "US"`) → store as `AMZN_ADS_PROFILE_ID`. Every campaign
call must send it in the `Amazon-Advertising-API-Scope` header.

If `amazon_profiles.py` returns a profile: ✅ connected. A `401/403` means Step 2
approval hasn't landed yet.

---

## What each secret is for

| Secret | Where it came from | Role |
|---|---|---|
| `client_id` / `client_secret` | LwA security profile (Step 1) | Identifies the app in OAuth |
| `refresh_token` | `amazon_oauth.py` (Step 3) | Long-lived grant → mints access tokens |
| `profile_id` | `amazon_profiles.py` (Step 4) | The advertiser account+marketplace you act on |

---

## Endpoints (North America)

- **Token**: `https://api.amazon.com/auth/o2/token`
- **API base**: `https://advertising-api.amazon.com`
- Required headers on every call: `Amazon-Advertising-API-ClientId: <client_id>`,
  `Authorization: Bearer <access_token>`, and (after Step 4)
  `Amazon-Advertising-API-Scope: <profile_id>`.

## Gotchas

- Access tokens last ~1 hour — always refresh from the `refresh_token` (the helpers do this).
- The OAuth redirect to `https://localhost:8443` will show a browser error page —
  that's expected; only the `?code=...` in the URL bar matters.
- Region matters: NA / EU / FE have different base URLs. We use NA (US marketplace).
