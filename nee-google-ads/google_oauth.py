#!/usr/bin/env python3
"""One-shot: turn an OAuth client (client_secret.json) into a Google Ads refresh token.

Prereqs (see api-setup.md):
  - client_secret.json (Desktop OAuth client) downloaded into this folder
  - `uv add google-auth-oauthlib`

Run:
  uv run python google_oauth.py

Opens a browser, you click "Allow", and the refresh token is printed. Copy it into
Infisical as GOOGLE_ADS_REFRESH_TOKEN. Nothing is written to disk.
"""
import sys
import time

# Scope grants Google Ads API access on behalf of the authorizing user.
SCOPES = ["https://www.googleapis.com/auth/adwords"]
CLIENT_SECRET_FILE = "client_secret.json"


def main() -> int:
    t0 = time.time()
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        sys.exit("Missing dep. Run: uv add google-auth-oauthlib")

    print("[1/3] Loading OAuth client...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
    except FileNotFoundError:
        sys.exit(f"{CLIENT_SECRET_FILE} not found. Download it from Cloud Console "
                 f"(Credentials → your OAuth client → Download JSON) into this folder.")

    print("[2/3] Opening browser for consent (a local server will catch the redirect)...")
    # run_local_server spins a localhost listener and auto-captures the auth code.
    creds = flow.run_local_server(port=0, prompt="consent")

    print("[3/3] Done.\n")
    if not creds.refresh_token:
        sys.exit("No refresh token returned. Re-run — make sure you pass prompt='consent' "
                 "and that this is the first grant (revoke prior grants at "
                 "https://myaccount.google.com/permissions if needed).")

    print("=" * 60)
    print("GOOGLE_ADS_REFRESH_TOKEN:")
    print(creds.refresh_token)
    print("=" * 60)
    print("\nNext: store it in Infisical, then run smoke_test.py")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
