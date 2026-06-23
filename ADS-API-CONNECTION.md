# Ads API Connection — Overview & Checklist

How DataForSEO drives Google + Amazon ads. **DataForSEO does not connect to your ad
accounts** — it's the research layer. You build the bridge between research and activation.

```
RESEARCH (have it)        BRIDGE (build it)            ACTIVATION (connect it)
DataForSEO MCP       →    scripts: insight → ops   →   Google Ads API  (nee-google-ads/)
 keyword volume                                        Amazon Ads API  (nee-amazon-ads/)
 SERP / competitors
 trends / gaps
```

- **Research** is live today (DataForSEO MCP).
- **Activation** needs API access on top of your existing live ad accounts → the two runbooks.
- **Bridge** is the payoff: e.g. DataForSEO finds each state's keywords → script generates
  one Google Ads ad group per state → mapped to the 51 state articles already built.

---

## Do-today checklist (kick off the approvals — they have lead time)

### Google Ads  → `nee-google-ads/api-setup.md`
- [ ] Step 1: Create/confirm a **Manager (MCC)** account, link the live ad account
- [ ] Step 2: **Apply for Basic access** in MCC → API Center  ⏱ *gating, 1–3 days*
- [ ] Step 3: Cloud project → enable Google Ads API → Desktop OAuth client → `client_secret.json`
- [ ] Step 4: `uv run python google_oauth.py` → refresh token
- [ ] Step 5: secrets → Infisical → `uv run python smoke_test.py`

### Amazon Ads  → `nee-amazon-ads/api-setup.md`
- [ ] Step 1: Create **Login with Amazon** security profile → client id/secret
- [ ] Step 2: **Request Amazon Ads API access**  ⏱ *gating*
- [ ] Step 3: `uv run python amazon_oauth.py` → refresh token
- [ ] Step 4: `uv run python amazon_profiles.py` → profile id (US)

The two **gating** items (Google Basic access, Amazon API access) are the only things
with real wait time. Start both first; everything else is done while you wait.

---

## Secrets (all into Infisical — project `akila-primary-ab-kk`)

| Google Ads | Amazon Ads |
|---|---|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | `AMZN_ADS_CLIENT_ID` |
| `GOOGLE_ADS_CLIENT_ID` | `AMZN_ADS_CLIENT_SECRET` |
| `GOOGLE_ADS_CLIENT_SECRET` | `AMZN_ADS_REFRESH_TOKEN` |
| `GOOGLE_ADS_REFRESH_TOKEN` | `AMZN_ADS_PROFILE_ID` |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | |

---

## After both are connected — the bridge to build

1. **Search-term mining loop**: pull Google Ads search-term reports → feed losers to
   DataForSEO for intent/volume → auto-add negatives, promote winners to exact match.
2. **Programmatic state campaigns**: DataForSEO state keywords → one ad group per state →
   landing page = the matching `/blogs/drivers-license-name-change/...` or product page.
3. **Competitor gap → ads**: DataForSEO shows NewlyNamed's ranked terms you don't bid on →
   stand up campaigns for the high-intent, winnable ones.
4. **Amazon keyword harvesting**: Sponsored Products search-term report → DataForSEO volume
   check → graduate converters to exact, negate the rest.

> Per the growth plan: install conversion tracking (GA4 + Google Ads "Purchase",
> Meta CAPI) **before** scaling spend, or none of this is measurable.
