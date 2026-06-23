#!/usr/bin/env python3
"""Smoke test: prove the Google Ads API credential chain works end-to-end.

Lists the customer accounts your authenticated user can reach. If this returns
your customer ID(s), every secret is correct and you're connected.

Reads secrets from env (export them, or source from Infisical):
  GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
  GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID

Run:
  uv add google-ads
  uv run python smoke_test.py
"""
import os
import sys
import time

REQUIRED = [
    "GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
]


def main() -> int:
    t0 = time.time()
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        sys.exit("Missing env vars: " + ", ".join(missing))

    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        sys.exit("Missing dep. Run: uv add google-ads")

    print("[1/2] Building client from env...")
    client = GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
        "use_proto_plus": True,
    })

    print("[2/2] Listing accessible customers...")
    svc = client.get_service("CustomerService")
    res = svc.list_accessible_customers()
    print("\nAccessible customer resource names:")
    for name in res.resource_names:
        print(f"  - {name}")
    print(f"\n✅ Connected. Found {len(res.resource_names)} account(s).")
    print(f"Total elapsed: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
