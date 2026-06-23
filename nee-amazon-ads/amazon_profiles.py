#!/usr/bin/env python3
"""Smoke test + profile lookup for the Amazon Ads API (North America).

Refreshes an access token from your refresh token, then lists advertising
profiles. Pick the US one's profileId -> store as AMZN_ADS_PROFILE_ID.

Reads from env:
  AMZN_ADS_CLIENT_ID, AMZN_ADS_CLIENT_SECRET, AMZN_ADS_REFRESH_TOKEN

Run:
  uv add requests
  uv run python amazon_profiles.py
"""
import os
import sys
import time

TOKEN_URL = "https://api.amazon.com/auth/o2/token"
API_BASE = "https://advertising-api.amazon.com"   # North America


def access_token(requests, client_id, client_secret, refresh_token) -> str:
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"Token refresh failed ({resp.status_code}): {resp.text}")
    return resp.json()["access_token"]


def main() -> int:
    t0 = time.time()
    cid = os.environ.get("AMZN_ADS_CLIENT_ID")
    secret = os.environ.get("AMZN_ADS_CLIENT_SECRET")
    refresh = os.environ.get("AMZN_ADS_REFRESH_TOKEN")
    if not all([cid, secret, refresh]):
        sys.exit("Set AMZN_ADS_CLIENT_ID, AMZN_ADS_CLIENT_SECRET, AMZN_ADS_REFRESH_TOKEN.")
    try:
        import requests
    except ImportError:
        sys.exit("Missing dep. Run: uv add requests")

    print("[1/2] Refreshing access token...")
    token = access_token(requests, cid, secret, refresh)

    print("[2/2] Fetching profiles...")
    resp = requests.get(f"{API_BASE}/v2/profiles", headers={
        "Amazon-Advertising-API-ClientId": cid,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"Profiles call failed ({resp.status_code}): {resp.text}\n"
                 f"A 401/403 usually means API access (Step 2) isn't approved yet.")

    profiles = resp.json()
    print(f"\n✅ Connected. {len(profiles)} profile(s):\n")
    for p in profiles:
        cc = p.get("countryCode")
        acct = p.get("accountInfo", {})
        star = "  <-- US, use this" if cc == "US" else ""
        print(f"  profileId={p.get('profileId')}  country={cc}  "
              f"type={acct.get('type')}  name={acct.get('name')}{star}")
    print(f"\nTotal elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
