"""
access_api.py — client demo for the I8 video.

Usage:
    1. Start the API:        flask --app app run -p 5002
    2. Start ngrok:          ngrok http 5002
    3. Paste the HTTPS URL into BASE_URL below (or leave localhost for local-only demo)
    4. python access_api.py
"""
import json
import requests

# Paste your ngrok HTTPS URL here when recording the video, e.g.:
# BASE_URL = "https://abcd-1234.ngrok-free.app"
BASE_URL = "http://localhost:5002"


def show(label, resp):
    print(f"\n=== {label} ===")
    print("Status:", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    show("Index / endpoint catalog", requests.get(f"{BASE_URL}/"))
    show("All businesses (summary)", requests.get(f"{BASE_URL}/businesses"))
    show("By ID sb-001", requests.get(f"{BASE_URL}/businesses/sb-001"))
    show("By category=cafe", requests.get(f"{BASE_URL}/businesses/category/cafe"))
    show("By ZIP=98122", requests.get(f"{BASE_URL}/businesses/zip/98122"))
    show("By neighborhood=Capitol Hill", requests.get(f"{BASE_URL}/businesses/neighborhood/Capitol Hill"))

    # NEW I8 endpoints
    show("NEW: tag=wifi", requests.get(f"{BASE_URL}/businesses/tag/wifi"))
    show("NEW: price 20-40", requests.get(f"{BASE_URL}/businesses/price?min=20&max=40"))
    show("NEW: top-rated limit=3", requests.get(f"{BASE_URL}/top-rated?limit=3"))
    show("NEW: open-now", requests.get(f"{BASE_URL}/open-now"))
    show("NEW: aggregate /stats", requests.get(f"{BASE_URL}/stats"))

    show("Search 'sustainable'", requests.get(f"{BASE_URL}/search?q=sustainable"))
    show("Categories list", requests.get(f"{BASE_URL}/categories"))

    # NEW: POST to insert a new business document
    new_biz = {
        "id": "sb-999",
        "name": "Demo Bakery",
        "category": "cafe",
        "description": "Demo bakery inserted live during the video.",
        "location": {"address": "1 Demo Way", "city": "Seattle", "state": "WA",
                     "zip": "98101", "neighborhood": "Capitol Hill"},
        "contact": {"phone": "206-555-9999", "email": "demo@bakery.com"},
        "products": [{"name": "Demo Croissant", "price": 3.25}],
        "hours": {"monday": "7am-3pm"},
        "tags": ["demo", "bakery"],
        "yearEstablished": 2026,
        "ownerName": "Demo Owner",
        "acceptsOnlineOrders": True,
        "communityRating": 5.0
    }
    show("NEW: POST /businesses (insert)", requests.post(f"{BASE_URL}/businesses", json=new_biz))
    show("Re-list to confirm insert", requests.get(f"{BASE_URL}/businesses"))
