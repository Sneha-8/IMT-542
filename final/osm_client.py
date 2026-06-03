"""
OpenStreetMap live data via Nominatim + Overpass (no API key required).
Respect usage policy: https://operations.osmfoundation.org/policies/nominatim/
"""
import re
import time

import requests

USER_AGENT = "LocalFind-IMT542/1.0 (UW course project; contact via GitHub Sneha-8/IMT-542)"
NOMINATIM = "https://nominatim.openstreetmap.org"
OVERPASS = "https://overpass.kumi.systems/api/interpreter"
TIMEOUT = 20
_last_call = 0.0


def _throttle(seconds: float = 1.1):
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < seconds:
        time.sleep(seconds - elapsed)
    _last_call = time.time()


def _headers() -> dict:
    return {"User-Agent": USER_AGENT}


def reverse_geocode(lat: float, lon: float) -> str | None:
    """Turn coordinates into a location label for search."""
    _throttle()
    r = requests.get(
        f"{NOMINATIM}/reverse",
        params={"lat": lat, "lon": lon, "format": "json", "addressdetails": 1},
        headers=_headers(),
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    addr = data.get("address") or {}
    city = addr.get("city") or addr.get("town") or addr.get("village") or "Seattle"
    state = addr.get("state", "WA")
    return f"{city}, {state}"


def geocode(location: str) -> dict | None:
    """Resolve a place name to lat/lon for bounding queries."""
    _throttle()
    r = requests.get(
        f"{NOMINATIM}/search",
        params={"q": location, "format": "json", "limit": 1},
        headers=_headers(),
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def search_places(term: str, location: str, limit: int = 25) -> list[dict]:
    """
    Search OSM for businesses near a location.
    Uses Nominatim structured search biased to Seattle area.
    """
    q_parts = []
    if term:
        q_parts.append(term)
    q_parts.append(location or "Seattle, Washington")
    query = ", ".join(q_parts)

    _throttle()
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": min(limit, 50),
        "countrycodes": "us",
    }
    # Seattle metro viewbox (left, top, right, bottom)
    params["viewbox"] = "-122.55,47.80,-122.05,47.45"
    params["bounded"] = 1

    r = requests.get(f"{NOMINATIM}/search", params=params, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    rows = r.json()

    business_classes = {"amenity", "shop", "office", "craft", "tourism"}
    business_types = {
        "cafe",
        "restaurant",
        "coffee_shop",
        "bakery",
        "books",
        "clothes",
        "hairdresser",
        "beauty",
        "pharmacy",
        "convenience",
        "yes",
        "retail",
        "food",
        "bar",
        "fast_food",
        "ice_cream",
        "boutique",
        "gift",
        "jewelry",
        "florist",
        "bicycle",
        "repair",
    }
    filtered = []
    for row in rows:
        if row.get("class") in business_classes or row.get("type") in business_types:
            if row.get("name"):
                filtered.append(_normalize_nominatim_row(row))
        elif term and row.get("name") and "seattle" in row.get("display_name", "").lower():
            filtered.append(_normalize_nominatim_row(row))
    return filtered[:limit]


def _normalize_nominatim_row(row: dict) -> dict:
    """Ensure osm_to_sbp has address + osm ids from Nominatim payloads."""
    out = dict(row)
    if "address" not in out and out.get("addressdetails"):
        out["address"] = out["addressdetails"]
    return out


def overpass_near(lat: float, lon: float, term: str = "", radius_m: int = 2500, limit: int = 30) -> list[dict]:
    """Query Overpass for amenities and shops within radius of a point."""
    term_filter = ""
    if term:
        safe = re.sub(r'["\\]', "", term.lower())
        term_filter = f'["name"~"{safe}",i]'
    amenities = (
        "cafe|restaurant|coffee_shop|bakery|bar|fast_food|ice_cream|"
        "pharmacy|library|marketplace|food_court|deli|"
        "bank|post_office|veterinary|doctors|dentist|laundry|dry_cleaning|"
        "car_rental|bicycle_rental|fuel|charging_station"
    )
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"{amenities}"]{term_filter}(around:{radius_m},{lat},{lon});
      node["shop"]{term_filter}(around:{radius_m},{lat},{lon});
      node["craft"]{term_filter}(around:{radius_m},{lat},{lon});
      node["office"]{term_filter}(around:{radius_m},{lat},{lon});
      node["healthcare"]{term_filter}(around:{radius_m},{lat},{lon});
    );
    out body {limit};
    """
    _throttle(0.5)
    r = requests.post(OVERPASS, data={"data": query}, timeout=35)
    r.raise_for_status()
    data = r.json()
    results = []
    for el in data.get("elements", []):
        tags = el.get("tags") or {}
        name = tags.get("name")
        if not name:
            continue
        results.append(
            {
                "osm_type": el["type"],
                "osm_id": el["id"],
                "lat": str(el.get("lat", "")),
                "lon": str(el.get("lon", "")),
                "name": name,
                "class": "amenity" if tags.get("amenity") else "shop",
                "type": tags.get("amenity") or tags.get("shop") or "business",
                "display_name": _display_from_tags(tags, el),
                "address": _address_from_tags(tags),
                "tags": tags,
            }
        )
    return results


def _address_from_tags(tags: dict) -> dict:
    return {
        "house_number": tags.get("addr:housenumber"),
        "road": tags.get("addr:street"),
        "city": tags.get("addr:city", "Seattle"),
        "state": tags.get("addr:state", "Washington"),
        "postcode": tags.get("addr:postcode"),
        "neighbourhood": tags.get("addr:suburb") or tags.get("neighbourhood"),
    }


def _display_from_tags(tags: dict, el: dict) -> str:
    parts = [tags.get("name"), tags.get("addr:street"), tags.get("addr:city", "Seattle")]
    return ", ".join(p for p in parts if p)


def discover_neighborhood(
    location: str,
    *,
    radius_m: int = 2500,
    limit: int = 50,
) -> list[dict]:
    """
    Pull all named shops/amenities near a neighborhood (no search keyword).
    Best way to bulk-add small businesses from OpenStreetMap.
    """
    geo = geocode(location)
    if not geo:
        return []
    lat, lon = float(geo["lat"]), float(geo["lon"])
    return overpass_near(lat, lon, term="", radius_m=radius_m, limit=limit)


def lookup_osm_id(osm_type: str, osm_id: int) -> dict | None:
    """Fetch one element via Nominatim lookup."""
    _throttle()
    r = requests.get(
        f"{NOMINATIM}/lookup",
        params={"osm_ids": f"{osm_type[0].upper()}{osm_id}", "format": "json", "addressdetails": 1},
        headers=_headers(),
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None
