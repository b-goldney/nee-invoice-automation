#!/usr/bin/env python3
"""One-shot: turn an LwA app (client id/secret) into an Amazon Ads refresh token.

Prereqs (see api-setup.md):
  - LwA security profile created, with https://localhost:8443 as an Allowed Return URL
  - export AMZN_ADS_CLIENT_ID / AMZN_ADS_CLIENT_SECRET
  - `uv add requests`

Run:
  uv run python amazon_oauth.py

Manual flow (no local server needed): the script prints an auth URL, you authorize,
then paste the redirected localhost URL back in. Refresh token is printed.
"""
import os
import sys
import time
import urllib.parse as up

REDIRECT_URI = "https://localhost:8443"
SCOPE = "cpc_advertising:campaign_management"
AUTH_URL = "https://www.amazon.com/ap/oa"
TOKEN_URL = "https://api.amazon.com/auth/o2/token"


def main() -> int:
    t0 = time.time()
    client_id = os.environ.get("AMZN_ADS_CLIENT_ID")
    client_secret = os.environ.get("AMZN_ADS_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit("Set AMZN_ADS_CLIENT_ID and AMZN_ADS_CLIENT_SECRET first.")
    try:
        import requests
    except ImportError:
        sys.exit("Missing dep. Run: uv add requests")

    # Step A: build + show the consent URL.
    params = {
        "client_id": client_id,
        "scope": SCOPE,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
    }
    print("[1/2] Open this URL, sign in, click Allow:\n")
    print(AUTH_URL + "?" + up.urlencode(params))
    print("\nYou'll be redirected to https://localhost:8443/?code=...  (page won't load — that's fine).")
    pasted = input("\nPaste the FULL redirected URL here:\n> ").strip()

    # Pull ?code= out of whatever they pasted.
    qs = up.parse_qs(up.urlparse(pasted).query)
    code = (qs.get("code") or [None])[0]
    if not code:
        sys.exit("No ?code= found in that URL. Re-run and paste the full redirected URL.")

    # Step B: exchange the auth code for tokens.
    print("\n[2/2] Exchanging code for tokens...")
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"Token exchange failed ({resp.status_code}): {resp.text}")
    tok = resp.json()

    print("\n" + "=" * 60)
    print("AMZN_ADS_REFRESH_TOKEN:")
    print(tok["refresh_token"])
    print("=" * 60)
    print("\nNext: store it in Infisical, then run amazon_profiles.py")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
