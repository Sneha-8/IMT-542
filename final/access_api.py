"""Demo client for final SBP API — use with ngrok URL for Canvas submission."""
import json
import os

import requests

BASE_URL = os.environ.get("SBP_BASE_URL", "http://localhost:5002")
TOKEN = os.environ.get("SBP_API_TOKEN", "dev-class-token")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def show(label, resp):
    print(f"\n=== {label} ===")
    print("Status:", resp.status_code, resp.headers.get("X-Cache", ""))
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    show("Health", requests.get(f"{BASE_URL}/health"))
    show("Schema", requests.get(f"{BASE_URL}/schema"))
    show("Search coffee + Capitol Hill", requests.get(
        f"{BASE_URL}/businesses/search",
        params={"term": "coffee", "location": "Capitol Hill"},
    ))
    show("Single sb-001 (public)", requests.get(f"{BASE_URL}/businesses/sb-001"))
    show("Single sb-001 (auth contact)", requests.get(
        f"{BASE_URL}/businesses/sb-001", headers=HEADERS
    ))
    show("Stats", requests.get(f"{BASE_URL}/stats"))
    show("Open now", requests.get(f"{BASE_URL}/open-now"))
