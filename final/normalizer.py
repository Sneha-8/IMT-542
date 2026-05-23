"""
Normalize curated local business documents (I7/I8 shape) to SBP schema v1.0.
"""
import re
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"
LICENSE = "CC-BY-4.0 — curated demo dataset for IMT 542"
SOURCE = "curated_local_v1"


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


def quality_flags(record: dict) -> dict:
    loc = record.get("location") or {}
    contact = record.get("contact") or {}
    flags = {
        "has_name": bool(record.get("name")),
        "has_rating": record.get("communityRating") is not None,
        "has_category": bool(record.get("category")),
        "has_address": bool(loc.get("address")),
        "has_phone": bool(contact.get("phone")),
        "has_tags": bool(record.get("tags")),
        "has_hours": bool(record.get("hours")),
        "is_complete": False,
    }
    flags["is_complete"] = all(
        flags[k]
        for k in (
            "has_name",
            "has_rating",
            "has_category",
            "has_address",
            "has_phone",
            "has_tags",
        )
    )
    return flags


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
    }


def completeness_score(records: list[dict]) -> float:
    if not records:
        return 0.0
    complete = sum(1 for r in records if r.get("quality_flags", {}).get("is_complete"))
    return round(complete / len(records), 2)


def build_provenance(query_params: dict | None = None) -> dict:
    return {
        "source": SOURCE,
        "endpoint": "GET /businesses/search",
        "repository": "https://github.com/Sneha-8/IMT-542/tree/main/final",
        "query_params": query_params or {},
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "license": LICENSE,
        "api_key_owner": "n/a-demo-dataset",
    }


def build_envelope(
    businesses: list[dict],
    query_params: dict | None = None,
    data_classification: str = "public",
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "data_classification": data_classification,
        "provenance": build_provenance(query_params),
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
