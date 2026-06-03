"""
Fetch real small-business data from external APIs and merge into SBP records.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import osm_client
import yelp_client
from normalizer import osm_to_sbp, yelp_to_sbp
from yelp_client import YelpRateLimitError


def _norm_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").lower().strip())


def _enrich_osm_from_yelp(records: list[dict], yelp_records: list[dict]) -> list[dict]:
    """Attach Yelp ratings/photos to OSM rows when names match."""
    if not yelp_records:
        return records
    by_name = {_norm_name(r.get("name", "")): r for r in yelp_records if r.get("name")}
    out = []
    for rec in records:
        if not str(rec.get("id", "")).startswith("osm-"):
            out.append(rec)
            continue
        y = by_name.get(_norm_name(rec.get("name", "")))
        if not y:
            out.append(rec)
            continue
        merged = dict(rec)
        for key in (
            "rating",
            "review_count",
            "price_tier",
            "price_symbol",
            "image_url",
            "yelp_url",
            "transactions",
        ):
            if merged.get(key) is None and y.get(key) is not None:
                merged[key] = y[key]
        if not merged.get("hours") and y.get("hours"):
            merged["hours"] = y["hours"]
        out.append(merged)
    return out


def find_cached_records(
    collection,
    term: str,
    location: str,
    limit: int = 25,
    *,
    zip_code: str = "",
) -> list[dict]:
    """Return previously fetched live API rows from MongoDB."""
    from normalizer import to_sbp_record

    term_l = (term or "").lower()
    loc_l = (location or "").lower()
    loc_parts = [
        p.strip().lower()
        for p in loc_l.replace(",", " ").split()
        if len(p.strip()) > 2
    ]
    zip_want = ""
    if zip_code:
        m = re.search(r"\b(\d{5})\b", str(zip_code))
        zip_want = m.group(1) if m else ""
    if not zip_want:
        for p in loc_parts:
            if re.fullmatch(r"\d{5}", p):
                zip_want = p
                break
    non_zip_parts = [p for p in loc_parts if not re.fullmatch(r"\d{5}", p)]

    def matches(doc: dict) -> bool:
        if term_l:
            hay = " ".join(
                [
                    doc.get("name", ""),
                    doc.get("description", ""),
                    doc.get("category", ""),
                    " ".join(doc.get("tags") or []),
                ]
            ).lower()
            words = [w for w in re.split(r"\W+", term_l) if len(w) > 2]
            synonyms = {
                "fashion": ["clothing", "boutique", "apparel", "vintage", "jewelry", "shoes"],
                "fitness": ["gym", "yoga", "pilates", "crossfit", "training"],
                "food": ["cafe", "restaurant", "coffee", "bakery", "bar"],
                "beauty": ["salon", "spa", "barber", "nails", "hair"],
                "retail": ["shop", "store", "gift", "retail"],
                "services": ["repair", "cleaners", "laundry", "automotive"],
            }
            extra = []
            for w in words:
                extra.extend(synonyms.get(w, []))
            check = words + extra
            if check:
                if not any(w in hay for w in check):
                    return False
            elif term_l not in hay:
                return False
        loc_obj = doc.get("location") or {}
        if zip_want:
            doc_zip = str(loc_obj.get("zip") or "")
            m = re.search(r"\b(\d{5})\b", doc_zip)
            if not m or m.group(1) != zip_want:
                return False
        if non_zip_parts:
            loc_hay = " ".join(
                [
                    str(loc_obj.get("neighborhood", "")),
                    str(loc_obj.get("city", "")),
                    str(loc_obj.get("state", "")),
                    str(loc_obj.get("zip", "")),
                    str(loc_obj.get("address", "")),
                    doc.get("description", ""),
                ]
            ).lower()
            if not any(part in loc_hay for part in non_zip_parts):
                return False
        return True

    docs = [
        d
        for d in collection.find({})
        if matches(d) and not str(d.get("id", "")).startswith("sb-")
    ]
    docs.sort(key=lambda d: d.get("communityRating") or 0, reverse=True)
    return [to_sbp_record(d) for d in docs[:limit]]


def _dedupe(records: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in records:
        key = _norm_name(r.get("name", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def search_osm(term: str, location: str, limit: int = 25, *, fast: bool = False) -> list[dict]:
    """OSM search — fast mode uses one Overpass call only."""
    loc = location or "Seattle, WA"
    records = []

    try:
        geo = osm_client.geocode(loc)
        if geo:
            lat, lon = float(geo["lat"]), float(geo["lon"])
            cap = limit if fast else max(limit, 35)
            for place in osm_client.overpass_near(lat, lon, term=term, limit=cap):
                records.append(osm_to_sbp(place))
            if records:
                return _dedupe(records)[:limit]
    except requests.RequestException:
        pass

    if fast:
        return _dedupe(records)[:limit]

    try:
        for place in osm_client.search_places(term, loc, limit=min(limit, 15)):
            records.append(osm_to_sbp(place))
    except requests.RequestException:
        pass

    if not term.strip():
        try:
            for place in osm_client.discover_neighborhood(loc, limit=limit):
                records.append(osm_to_sbp(place))
        except requests.RequestException:
            pass

    return _dedupe(records)[:limit]


def search_neighborhood(location: str, limit: int = 50) -> list[dict]:
    """Bulk OSM discovery for one neighborhood (no keyword)."""
    records = []
    try:
        for place in osm_client.discover_neighborhood(location, limit=limit):
            records.append(osm_to_sbp(place))
    except requests.RequestException:
        pass
    return _dedupe(records)[:limit]


def search_yelp(term: str, location: str, radius: int, limit: int = 20) -> list[dict]:
    if not yelp_client.is_configured():
        return []
    loc = location or "Seattle, WA"
    data = yelp_client.search_businesses(term=term, location=loc, radius=radius, limit=limit)
    return [yelp_to_sbp(b) for b in data.get("businesses", [])]


def search_live(
    term: str,
    location: str,
    radius: int = 5000,
    *,
    prefer_yelp: bool = True,
    limit: int = 25,
    fast: bool = False,
) -> tuple[list[dict], str, list[str]]:
    """
    Returns (records, primary_source, sources_used).
    fast=True: parallel Yelp+OSM, minimal OSM calls.
    """
    sources_used = []
    yelp_records: list[dict] = []
    osm_records: list[dict] = []

    yelp_term = term.strip() or "local"
    if prefer_yelp and yelp_client.is_configured():

        def _yelp():
            return search_yelp(yelp_term, location, radius, limit=limit)

        def _osm():
            return search_osm(term, location, limit=limit, fast=fast or True)

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(_yelp): "yelp", pool.submit(_osm): "osm"}
            try:
                for fut in as_completed(futures, timeout=22):
                    kind = futures[fut]
                    try:
                        result = fut.result(timeout=1)
                        if kind == "yelp" and result:
                            yelp_records = result
                            sources_used.append("yelp")
                        elif kind == "osm" and result:
                            osm_records = result
                            sources_used.append("openstreetmap")
                    except Exception:
                        pass
            except TimeoutError:
                pass
    else:
        try:
            osm_records = search_osm(term, location, limit=limit, fast=True)
            if osm_records:
                sources_used.append("openstreetmap")
        except requests.RequestException:
            pass

    merged = _enrich_osm_from_yelp(_dedupe(yelp_records + osm_records), yelp_records)[:limit]

    if yelp_records and osm_records:
        primary = "yelp+openstreetmap"
    elif yelp_records:
        primary = "yelp"
    elif osm_records:
        primary = "openstreetmap"
    else:
        primary = "none"

    return merged, primary, sources_used


def enrich_record_details(record: dict) -> dict:
    """
    Refresh hours for detail view: OSM lookup + optional Yelp match by name/location.
    """
    import osm_client
    import yelp_client
    from normalizer import merge_yelp_details_into, osm_to_sbp

    rec = dict(record)
    biz_id = str(rec.get("id", ""))

    if biz_id.startswith("osm-"):
        parts = biz_id.split("-")
        if len(parts) >= 3:
            try:
                place = osm_client.lookup_osm_id(parts[1], int(parts[2]))
                if place:
                    fresh = osm_to_sbp(place)
                    if fresh.get("hours"):
                        rec["hours"] = fresh["hours"]
            except Exception:
                pass

    hours = rec.get("hours") or {}
    day_keys = {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }
    has_yelp_hours = any(
        k in day_keys and hours.get(k) and hours.get(k) != hours.get("note")
        for k in day_keys
    )
    if has_yelp_hours:
        return rec

    if not yelp_client.is_configured():
        return rec

    loc = rec.get("location") or {}
    loc_str = ", ".join(
        p
        for p in [
            loc.get("address_line_1"),
            loc.get("city"),
            loc.get("state"),
            loc.get("zip_code"),
        ]
        if p
    ) or "Seattle, WA"
    try:
        data = yelp_client.search_businesses(term=rec.get("name", ""), location=loc_str, limit=3)
        for hit in data.get("businesses", []):
            if _norm_name(hit.get("name", "")) != _norm_name(rec.get("name", "")):
                continue
            detail = yelp_client.get_business(hit["id"])
            if detail:
                return merge_yelp_details_into(rec, detail)
    except Exception:
        pass
    return rec


def persist_records(collection, records: list[dict]) -> int:
    """Upsert live API results into MongoDB for later lookup."""
    n = 0
    for rec in records:
        doc = {
            "id": rec["id"],
            "name": rec["name"],
            "category": (rec.get("categories") or ["other"])[0],
            "description": rec.get("description", ""),
            "location": {
                "address": rec.get("location", {}).get("address_line_1"),
                "city": rec.get("location", {}).get("city"),
                "state": rec.get("location", {}).get("state"),
                "zip": rec.get("location", {}).get("zip_code"),
                "neighborhood": rec.get("location", {}).get("neighborhood"),
                "coordinates": rec.get("location", {}).get("coordinates"),
            },
            "contact": {
                "phone": rec.get("contact", {}).get("phone_e164"),
                "website": rec.get("contact", {}).get("website"),
            },
            "tags": rec.get("tags") or [],
            "hours": rec.get("hours") or {},
            "communityRating": rec.get("rating"),
            "review_count": rec.get("review_count"),
            "yelp_url": rec.get("yelp_url"),
            "image_url": rec.get("image_url"),
            "osm_url": rec.get("osm_url"),
            "source": "live_api",
        }
        collection.replace_one({"id": doc["id"]}, doc, upsert=True)
        n += 1
    return n
