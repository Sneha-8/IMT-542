"""
Normalize curated local business documents (I7/I8 shape) to SBP schema v1.0.
"""
import re
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"
LICENSE_CURATED = "CC-BY-4.0 — curated demo dataset for IMT 542"
LICENSE_YELP = "Yelp Fusion API Terms of Use — display only, no redistribution"
SOURCE_CURATED = "curated_local_v1"
SOURCE_YELP = "Yelp Fusion API"
SOURCE_OSM = "OpenStreetMap (Nominatim + Overpass)"
LICENSE_OSM = "ODbL 1.0 — OpenStreetMap contributors (https://www.openstreetmap.org/copyright)"


def to_e164(phone: str) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None


def price_tier_from_products(products: list) -> int | None:
    if not products:
        return None
    prices = [p.get("price") for p in products if isinstance(p.get("price"), (int, float))]
    if not prices:
        return None
    avg = sum(prices) / len(prices)
    if avg < 15:
        return 1
    if avg < 40:
        return 2
    if avg < 100:
        return 3
    return 4


def quality_flags(record: dict, *, from_yelp: bool = False) -> dict:
    loc = record.get("location") or {}
    contact = record.get("contact") or {}
    has_addr = bool(loc.get("address") or loc.get("address_line_1"))
    has_phone = bool(contact.get("phone") or contact.get("phone_e164"))
    flags = {
        "has_name": bool(record.get("name")),
        "has_rating": (record.get("communityRating") is not None)
        or (record.get("rating") is not None),
        "has_category": bool(record.get("category") or record.get("categories")),
        "has_address": has_addr,
        "has_phone": has_phone,
        "has_tags": bool(record.get("tags")),
        "has_hours": bool(record.get("hours")),
        "is_complete": False,
    }
    if from_yelp:
        flags["has_price_tier"] = record.get("price_tier") is not None
        flags["address_line_2_missing"] = not loc.get("address_line_2")
    flags["is_complete"] = all(
        flags[k]
        for k in (
            "has_name",
            "has_rating",
            "has_category",
            "has_address",
            "has_phone",
        )
    )
    return flags


def yelp_price_tier(price: str | None) -> tuple[int | None, str | None]:
    if not price:
        return None, None
    tier = len(price)
    return tier, price


def _yelp_time_label(raw: str) -> str:
    """Turn Yelp HHMM into short 12h label (e.g. 9am)."""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) < 3:
        return raw or ""
    h = int(digits[:2])
    m = int(digits[2:4]) if len(digits) >= 4 else 0
    h12 = h % 12 or 12
    suffix = "am" if h < 12 else "pm"
    return f"{h12}:{m:02d}{suffix}" if m else f"{h12}{suffix}"


def yelp_hours_to_dict(hours: list | None) -> dict:
    """Convert Yelp hours[] to day-name -> compact hours string."""
    if not hours:
        return {}
    day_names = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    out = {}
    for block in hours:
        day_idx = block.get("day", 0)
        if day_idx >= len(day_names):
            continue
        day = day_names[day_idx]
        if block.get("is_closed"):
            out[day] = "Closed"
            continue
        spans = []
        for slot in block.get("open") or []:
            start = slot.get("start", "")
            end = slot.get("end", "")
            if start and end:
                spans.append(f"{_yelp_time_label(start)}–{_yelp_time_label(end)}")
        out[day] = ", ".join(spans) if spans else "Open"
    return out


def yelp_to_sbp(yelp: dict, *, include_hours: bool = False) -> dict:
    """Map Yelp Fusion business object to SBP v1.0 record."""
    loc = yelp.get("location") or {}
    cats = [c.get("alias", c.get("title", "")) for c in yelp.get("categories") or []]
    cats = [c for c in cats if c]
    tier, symbol = yelp_price_tier(yelp.get("price"))
    phone = yelp.get("phone") or yelp.get("display_phone") or ""
    coords = yelp.get("coordinates") or {}
    transactions = list(yelp.get("transactions") or [])
    hours = yelp_hours_to_dict(yelp.get("hours")) if include_hours else {}

    record = {
        "id": yelp["id"],
        "name": yelp.get("name", ""),
        "categories": cats or ["other"],
        "rating": yelp.get("rating"),
        "review_count": yelp.get("review_count"),
        "price_tier": tier,
        "price_symbol": symbol,
        "transactions": transactions,
        "description": ", ".join(c.get("title", "") for c in yelp.get("categories") or []),
        "yelp_url": yelp.get("url"),
        "image_url": yelp.get("image_url"),
        "is_closed": yelp.get("is_closed", False),
        "location": {
            "address_line_1": loc.get("address1"),
            "address_line_2": loc.get("address2"),
            "city": loc.get("city"),
            "state": loc.get("state"),
            "zip_code": loc.get("zip_code"),
            "neighborhood": loc.get("city"),
            "country_code": loc.get("country", "US"),
            "coordinates": {
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
            }
            if coords
            else None,
        },
        "contact": {
            "phone_e164": to_e164(phone),
            "website": None,
            "data_classification": "restricted",
        },
        "tags": cats,
        "hours": hours,
        "products": [],
    }
    if yelp.get("distance") is not None:
        record["distance_from_query"] = {
            "value": round(yelp["distance"], 1),
            "unit": "meters",
        }
    record["quality_flags"] = quality_flags(
        {
            "name": record["name"],
            "rating": record["rating"],
            "categories": record["categories"],
            "location": record["location"],
            "contact": {"phone": phone},
            "tags": record["tags"],
            "hours": record["hours"],
            "price_tier": tier,
        },
        from_yelp=True,
    )
    return record


def _hours_from_osm_tags(tags: dict, place: dict | None = None) -> dict:
    """Map OSM opening_hours tag to SBP hours (note + optional today hint)."""
    oh = (
        tags.get("opening_hours")
        or tags.get("opening_hours:covid19")
        or (place or {}).get("opening_hours")
    )
    if not oh:
        return {}
    return {"note": str(oh)}


def osm_to_sbp(place: dict) -> dict:
    """Map Nominatim or Overpass place to SBP v1.0."""
    osm_type = place.get("osm_type", "node")
    osm_id = place.get("osm_id", 0)
    biz_id = f"osm-{osm_type}-{osm_id}"
    addr = place.get("address") or {}
    tags = dict(place.get("tags") or {})
    extra = place.get("extratags") or {}
    for key in ("opening_hours", "phone", "website", "contact:phone", "contact:website"):
        if key not in tags and extra.get(key):
            tags[key] = extra[key]

    line1 = addr.get("house_number", "")
    if addr.get("road"):
        line1 = f"{line1} {addr['road']}".strip()
    if not line1 and tags.get("addr:street"):
        line1 = f"{tags.get('addr:housenumber', '')} {tags['addr:street']}".strip()

    cat = place.get("type") or tags.get("amenity") or tags.get("shop") or "local_business"
    cats = [c for c in [cat, tags.get("cuisine"), tags.get("shop")] if c]

    hours = _hours_from_osm_tags(tags, place)

    lat = place.get("lat")
    lon = place.get("lon")
    coords = None
    if lat and lon:
        try:
            coords = {"latitude": float(lat), "longitude": float(lon)}
        except (TypeError, ValueError):
            pass

    website = tags.get("website") or tags.get("contact:website")
    phone = tags.get("phone") or tags.get("contact:phone")

    record = {
        "id": biz_id,
        "name": place.get("name") or "Unnamed business",
        "categories": cats or ["local_business"],
        "rating": None,
        "review_count": None,
        "price_tier": None,
        "price_symbol": None,
        "transactions": ["pickup"],
        "description": place.get("display_name", ""),
        "osm_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
        "location": {
            "address_line_1": line1 or None,
            "address_line_2": None,
            "city": addr.get("city") or tags.get("addr:city") or "Seattle",
            "state": addr.get("state") or tags.get("addr:state") or "WA",
            "zip_code": addr.get("postcode") or tags.get("addr:postcode"),
            "neighborhood": addr.get("neighbourhood") or addr.get("suburb"),
            "country_code": "US",
            "coordinates": coords,
        },
        "contact": {
            "phone_e164": to_e164(phone or ""),
            "website": website,
            "data_classification": "restricted",
        },
        "tags": cats,
        "hours": hours,
        "products": [],
    }
    record["quality_flags"] = quality_flags(
        {
            "name": record["name"],
            "categories": record["categories"],
            "location": record["location"],
            "contact": record["contact"],
            "tags": record["tags"],
            "hours": record["hours"],
        }
    )
    return record


def merge_yelp_details_into(record: dict, yelp_detail: dict) -> dict:
    """Add Yelp hours, rating, and links onto an existing SBP record."""
    yrec = yelp_to_sbp(yelp_detail, include_hours=True)
    out = dict(record)
    for key in (
        "rating",
        "review_count",
        "price_tier",
        "price_symbol",
        "image_url",
        "yelp_url",
        "transactions",
    ):
        if yrec.get(key) is not None and out.get(key) is None:
            out[key] = yrec[key]
    if yrec.get("hours"):
        out["hours"] = yrec["hours"]
    out["yelp_id"] = yelp_detail.get("id")
    return out


def to_sbp_record(raw: dict) -> dict:
    loc = raw.get("location") or {}
    contact = raw.get("contact") or {}
    flags = quality_flags(raw)
    tier = price_tier_from_products(raw.get("products") or [])
    transactions = []
    if raw.get("acceptsOnlineOrders"):
        transactions.append("online")
    transactions.append("pickup")

    return {
        "id": raw["id"],
        "name": raw["name"],
        "categories": [raw.get("category", "other")],
        "rating": raw.get("communityRating"),
        "review_count": raw.get("review_count"),
        "price_tier": tier,
        "price_symbol": "$" * tier if tier else None,
        "transactions": transactions,
        "description": raw.get("description"),
        "location": {
            "address_line_1": loc.get("address"),
            "address_line_2": None,
            "city": loc.get("city"),
            "state": loc.get("state"),
            "zip_code": loc.get("zip"),
            "neighborhood": loc.get("neighborhood"),
            "country_code": "US",
            "coordinates": loc.get("coordinates"),
        },
        "contact": {
            "phone_e164": to_e164(contact.get("phone", "")),
            "email": contact.get("email"),
            "website": contact.get("website"),
            "instagram": contact.get("instagram"),
            "data_classification": "restricted",
        },
        "tags": raw.get("tags") or [],
        "hours": raw.get("hours") or {},
        "products": raw.get("products") or [],
        "year_established": raw.get("yearEstablished"),
        "owner_name": raw.get("ownerName"),
        "quality_flags": flags,
        "yelp_url": raw.get("yelp_url"),
        "osm_url": raw.get("osm_url"),
        "image_url": raw.get("image_url"),
        "is_closed": raw.get("is_closed", False),
        "distance_from_query": raw.get("distance_from_query"),
    }


def completeness_score(records: list[dict]) -> float:
    if not records:
        return 0.0
    complete = sum(1 for r in records if r.get("quality_flags", {}).get("is_complete"))
    return round(complete / len(records), 2)


def build_provenance(
    query_params: dict | None = None,
    *,
    source: str = SOURCE_CURATED,
    license_text: str = LICENSE_CURATED,
    endpoint: str = "GET /businesses/search",
) -> dict:
    return {
        "source": source,
        "endpoint": endpoint,
        "repository": "https://github.com/Sneha-8/IMT-542/tree/main/final",
        "query_params": query_params or {},
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "license": license_text,
        "api_key_owner": "team-sbp-project" if source == SOURCE_YELP else "n/a-demo-dataset",
    }


def build_envelope(
    businesses: list[dict],
    query_params: dict | None = None,
    data_classification: str = "public",
    provenance: dict | None = None,
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "data_classification": data_classification,
        "provenance": provenance or build_provenance(query_params),
        "query_summary": {
            "records_in_this_batch": len(businesses),
            "quality_summary": {
                "records_complete": sum(
                    1 for b in businesses if b.get("quality_flags", {}).get("is_complete")
                ),
                "completeness_score": completeness_score(businesses),
                "last_validated": datetime.now(timezone.utc).isoformat(),
            },
        },
        "businesses": businesses,
    }


def apply_auth_policy(envelope: dict, token_ok: bool) -> dict:
    """Strip restricted contact fields unless bearer token is valid."""
    out = dict(envelope)
    businesses = []
    for b in envelope.get("businesses", []):
        rec = dict(b)
        contact = dict(rec.get("contact") or {})
        if not token_ok:
            contact.pop("email", None)
            contact.pop("phone_e164", None)
            contact["data_classification"] = "public"
        else:
            contact["data_classification"] = "restricted"
        rec["contact"] = contact
        businesses.append(rec)
    out["businesses"] = businesses
    if not token_ok:
        out["data_classification"] = "public"
    return out
