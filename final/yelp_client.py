"""
Yelp Fusion API client (v3).
Set YELP_API_KEY in environment or final/.env (not committed).
"""
import os

import requests

from env_loader import load_dotenv

YELP_BASE = "https://api.yelp.com/v3"
TIMEOUT = 12

load_dotenv()


def api_key() -> str | None:
    key = os.environ.get("YELP_API_KEY", "").strip()
    return key or None


def is_configured() -> bool:
    return bool(api_key())


def _headers() -> dict:
    key = api_key()
    if not key:
        raise RuntimeError("YELP_API_KEY is not set")
    return {"Authorization": f"Bearer {key}"}


def search_businesses(
    term: str = "",
    location: str = "Seattle, WA",
    radius: int = 5000,
    limit: int = 20,
) -> dict:
    """GET /v3/businesses/search — returns raw Yelp JSON."""
    params = {
        "location": location or "Seattle, WA",
        "radius": min(max(int(radius), 500), 40000),
        "limit": min(max(int(limit), 1), 50),
        "sort_by": "best_match",
    }
    if term:
        params["term"] = term
    r = requests.get(
        f"{YELP_BASE}/businesses/search",
        headers=_headers(),
        params=params,
        timeout=TIMEOUT,
    )
    if r.status_code == 429:
        raise YelpRateLimitError("Yelp rate limit exceeded")
    r.raise_for_status()
    return r.json()


def get_business(business_id: str) -> dict:
    """GET /v3/businesses/{id} — full details including hours."""
    r = requests.get(
        f"{YELP_BASE}/businesses/{business_id}",
        headers=_headers(),
        timeout=TIMEOUT,
    )
    if r.status_code == 404:
        return None
    if r.status_code == 429:
        raise YelpRateLimitError("Yelp rate limit exceeded")
    r.raise_for_status()
    return r.json()


class YelpRateLimitError(Exception):
    pass

class YelpNotConfiguredError(Exception):
    pass
