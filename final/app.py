"""
IMT 542 Final Project — Small Business Platform API (SBP v1.0)

Uses LIVE external APIs by default:
  - Yelp Fusion (optional YELP_API_KEY in .env)
  - OpenStreetMap Nominatim + Overpass (no key required)

Run:
    cp .env.example .env
    flask --app app run -p 5002
"""
import json
import os
import re
import time

import requests
from flask import Flask, jsonify, request

from env_loader import load_dotenv

load_dotenv()

from normalizer import (
    LICENSE_CURATED,
    LICENSE_OSM,
    LICENSE_YELP,
    SCHEMA_VERSION,
    SOURCE_CURATED,
    SOURCE_OSM,
    SOURCE_YELP,
    apply_auth_policy,
    build_envelope,
    build_provenance,
    osm_to_sbp,
    to_sbp_record,
    yelp_to_sbp,
)
import live_search
import osm_client
import yelp_client
from yelp_client import YelpRateLimitError

USE_MONGITA = os.environ.get("USE_MONGITA", "false").lower() == "true"
API_TOKEN = os.environ.get("SBP_API_TOKEN", "dev-class-token")
CACHE_TTL = int(os.environ.get("SBP_CACHE_TTL", "300"))
DEFAULT_LOCATION = os.environ.get("SBP_DEFAULT_LOCATION", "Seattle, WA")
_cache: dict = {}

if USE_MONGITA:
    from mongita import MongitaClientDisk

    client = MongitaClientDisk()
else:
    from pymongo import MongoClient

    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))

db = client["sbp_final"]
businesses = db["businesses"]
live_businesses = db["live_businesses"]

app = Flask(__name__)


@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return resp


def token_ok() -> bool:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1] == API_TOKEN
    return False


def cached(key: str, fn):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit["ts"] < CACHE_TTL:
        resp = hit["data"]
        if hasattr(resp, "headers"):
            resp.headers["X-Cache"] = "HIT"
        return resp
    resp = fn()
    if hasattr(resp, "headers"):
        _cache[key] = {"ts": now, "data": resp}
        resp.headers["X-Cache"] = "MISS"
    return resp


def _normalize_zip(value: str) -> str:
    m = re.search(r"\b(\d{5})\b", str(value or ""))
    return m.group(1) if m else ""


def _filter_by_zip(records: list[dict], zip_code: str) -> list[dict]:
    want = _normalize_zip(zip_code)
    if not want:
        return records
    matched = []
    for rec in records:
        loc = rec.get("location") or {}
        if _normalize_zip(str(loc.get("zip_code") or "")) == want:
            matched.append(rec)
    return matched


def _matches(doc: dict, term: str, location: str) -> bool:
    if term:
        t = term.lower()
        hay = " ".join(
            [
                doc.get("name", ""),
                doc.get("description", ""),
                doc.get("category", ""),
                " ".join(doc.get("tags") or []),
            ]
        ).lower()
        if t not in hay:
            return False
    if location:
        loc = location.lower()
        loc_obj = doc.get("location") or {}
        loc_hay = " ".join(
            [
                str(loc_obj.get("neighborhood", "")),
                str(loc_obj.get("city", "")),
                str(loc_obj.get("zip", "")),
            ]
        ).lower()
        if loc not in loc_hay:
            return False
    return True


def find_local_businesses(term: str, location: str) -> list:
    return [d for d in businesses.find({}) if _matches(d, term, location)]


def resolve_source() -> str:
    src = request.args.get("source", "auto").lower()
    if src in ("local", "yelp", "osm", "live"):
        return src
    return "live"


def _provenance_for_live(primary: str, sources: list[str], params: dict) -> dict:
    if primary == "yelp" or (sources == ["yelp"]):
        return build_provenance(
            params,
            source=SOURCE_YELP,
            license_text=LICENSE_YELP,
            endpoint="GET /v3/businesses/search",
        )
    if primary == "openstreetmap" or sources == ["openstreetmap"]:
        return build_provenance(
            params,
            source=SOURCE_OSM,
            license_text=LICENSE_OSM,
            endpoint="Nominatim search + Overpass API",
        )
    prov = build_provenance(params, source="Live merged feed", license_text=LICENSE_OSM)
    prov["upstream_sources"] = sources
    if "yelp" in sources:
        prov["license"] = f"{LICENSE_OSM}; Yelp: {LICENSE_YELP}"
    return prov


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "schema_version": SCHEMA_VERSION,
        "yelp_configured": yelp_client.is_configured(),
        "openstreetmap": True,
        "default_mode": "live external APIs (not demo-only)",
    })


@app.route("/config")
def config():
    sources = ["openstreetmap"]
    if yelp_client.is_configured():
        sources.insert(0, "yelp")
    sources.append("local")
    return jsonify({
        "schema_version": SCHEMA_VERSION,
        "yelp_configured": yelp_client.is_configured(),
        "openstreetmap_enabled": True,
        "default_location": DEFAULT_LOCATION,
        "default_source": "auto (live: Yelp if keyed + always OSM)",
        "data_sources": sources,
    })


@app.route("/schema")
def schema_doc():
    path = os.path.join(os.path.dirname(__file__), "sbp_schema_v1.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return jsonify({"schema_version": SCHEMA_VERSION, "json_schema": doc})


@app.route("/")
def index():
    return jsonify({
        "message": "Small Business Platform — live API-backed",
        "schema_version": SCHEMA_VERSION,
        "yelp_configured": yelp_client.is_configured(),
        "openstreetmap": True,
        "cached_live_records": live_businesses.count_documents({}),
        "endpoints": {
            "GET /businesses/search": "?term=coffee&location=Seattle, WA&zip=98102 (optional ZIP filter)",
            "GET /businesses/<id>": "Yelp id, osm-node-*, or sb-*",
            "GET /config": "Active data sources",
        },
    })


@app.route("/businesses/search")
def search():
    term = request.args.get("term", "").strip()
    location = request.args.get("location", "").strip()
    zip_filter = request.args.get("zip", "").strip()
    radius = int(request.args.get("radius", 5000))
    limit = int(request.args.get("limit", 25))
    lat = request.args.get("lat", "").strip()
    lon = request.args.get("lon", "").strip()

    if lat and lon:
        try:
            resolved = osm_client.reverse_geocode(float(lat), float(lon))
            if resolved:
                location = resolved
        except (ValueError, requests.RequestException):
            pass

    if not term and not location and not (lat and lon):
        return jsonify({"error": "Provide term and/or location (or lat/lon) query params"}), 400

    if not location:
        location = DEFAULT_LOCATION
    if zip_filter and not _normalize_zip(location):
        location = f"{_normalize_zip(zip_filter)}, Seattle, WA"

    params = {
        "term": term,
        "location": location,
        "radius": radius,
        "limit": limit,
        "zip": zip_filter or None,
    }
    fetch_limit = max(limit, 50) if zip_filter else limit
    source = resolve_source()

    def build_response():
        records = []
        primary = "none"
        sources_used = []

        if source == "local":
            raw = find_local_businesses(term, location)
            for r in raw:
                r.pop("_id", None)
            records = [to_sbp_record(r) for r in raw]
            prov = build_provenance(params, source=SOURCE_CURATED, license_text=LICENSE_CURATED)
            primary = "local"
        elif source == "yelp":
            if not yelp_client.is_configured():
                return jsonify({
                    "error": "Yelp not configured",
                    "hint": "Add YELP_API_KEY to final/.env from yelp.com/developers",
                }), 503
            try:
                records = live_search.search_yelp(term, location, radius, limit=fetch_limit)
                sources_used = ["yelp"]
                primary = "yelp"
                prov = _provenance_for_live(primary, sources_used, params)
            except YelpRateLimitError:
                return jsonify({"error": "Yelp rate limit", "retry_after": 60}), 503
            except requests.HTTPError as e:
                return jsonify({"error": "Yelp upstream error", "detail": str(e)}), 502
        elif source == "osm":
            records = live_search.search_osm(term, location, limit=fetch_limit)
            sources_used = ["openstreetmap"]
            primary = "openstreetmap"
            prov = _provenance_for_live(primary, sources_used, params)
        else:
            refresh = request.args.get("refresh", "false").lower() in ("1", "true", "yes")
            fast = request.args.get("fast", "true").lower() in ("1", "true", "yes")
            min_cached = int(request.args.get("min_cached", "1"))
            cached = (
                live_search.find_cached_records(
                    live_businesses, term, location, fetch_limit, zip_code=zip_filter
                )
                if not refresh
                else []
            )
            if not cached and not term and not refresh:
                cached = live_search.find_cached_records(
                    live_businesses, "", location, max(fetch_limit, 30), zip_code=zip_filter
                )
            if cached and not refresh and len(cached) >= min_cached:
                records = cached
                primary = "cached_live"
                sources_used = ["mongodb_cache"]
                prov = build_provenance(params, source="Live cache (prior OSM/Yelp fetch)")
                prov["license"] = LICENSE_OSM
                if yelp_client.is_configured():
                    prov["license"] = f"{LICENSE_OSM}; Yelp: {LICENSE_YELP}"
            else:
                records, primary, sources_used = live_search.search_live(
                    term,
                    location,
                    radius,
                    prefer_yelp=True,
                    limit=fetch_limit,
                    fast=fast,
                )
                if not records:
                    return jsonify({
                        "error": "No results from live APIs",
                        "hint": "Try term=coffee and location=Seattle, WA. Add YELP_API_KEY for richer data.",
                        "sources_tried": (
                            (["yelp"] if yelp_client.is_configured() else [])
                            + ["openstreetmap"]
                        ),
                    }), 404
                prov = _provenance_for_live(primary, sources_used, params)

        if zip_filter:
            records = _filter_by_zip(records, zip_filter)[:limit]
        live_search.persist_records(live_businesses, records)
        envelope = build_envelope(records, query_params=params, provenance=prov)
        if zip_filter:
            envelope["query_summary"]["zip_filter"] = _normalize_zip(zip_filter)
        envelope["query_summary"]["data_source"] = primary
        envelope["query_summary"]["sources_used"] = sources_used
        envelope = apply_auth_policy(envelope, token_ok())
        return jsonify(envelope)

    auth = "1" if token_ok() else "0"
    refresh_flag = request.args.get("refresh", "false")
    fast_flag = request.args.get("fast", "true")
    return cached(
        f"search:{source}:{term}:{location}:{zip_filter}:{radius}:{limit}:{auth}:{refresh_flag}:{fast_flag}",
        build_response,
    )


@app.route("/businesses/<business_id>")
def get_one(business_id):
    def build():
        if business_id.startswith("sb-"):
            raw = businesses.find_one({"id": business_id})
            if raw:
                raw.pop("_id", None)
                record = to_sbp_record(raw)
                envelope = build_envelope([record], query_params={"id": business_id})
                envelope = apply_auth_policy(envelope, token_ok())
                return jsonify(envelope)

        cached_doc = live_businesses.find_one({"id": business_id})
        if cached_doc:
            cached_doc.pop("_id", None)
            record = to_sbp_record(cached_doc)
            if request.args.get("full", "").lower() in ("1", "true", "yes"):
                record = live_search.enrich_record_details(record)
            envelope = build_envelope([record], query_params={"id": business_id})
            envelope = apply_auth_policy(envelope, token_ok())
            return jsonify(envelope)

        raw = businesses.find_one({"id": business_id})
        if raw:
            raw.pop("_id", None)
            record = to_sbp_record(raw)
            envelope = build_envelope([record], query_params={"id": business_id})
            envelope = apply_auth_policy(envelope, token_ok())
            return jsonify(envelope)

        if business_id.startswith("osm-"):
            parts = business_id.split("-")
            if len(parts) >= 3:
                osm_type, osm_id = parts[1], int(parts[2])
                place = osm_client.lookup_osm_id(osm_type, osm_id)
                if place:
                    record = live_search.enrich_record_details(osm_to_sbp(place))
                    prov = build_provenance(
                        {"id": business_id},
                        source=SOURCE_OSM,
                        license_text=LICENSE_OSM,
                        endpoint="Nominatim lookup",
                    )
                    envelope = build_envelope([record], provenance=prov)
                    envelope = apply_auth_policy(envelope, token_ok())
                    return jsonify(envelope)

        if yelp_client.is_configured() and not business_id.startswith("sb-"):
            try:
                detail = yelp_client.get_business(business_id)
            except YelpRateLimitError:
                return jsonify({"error": "Yelp rate limit"}), 503
            if detail:
                record = yelp_to_sbp(detail, include_hours=True)
                prov = build_provenance(
                    {"id": business_id},
                    source=SOURCE_YELP,
                    license_text=LICENSE_YELP,
                    endpoint=f"GET /v3/businesses/{business_id}",
                )
                envelope = build_envelope([record], provenance=prov)
                envelope = apply_auth_policy(envelope, token_ok())
                return jsonify(envelope)

        return jsonify({"error": f"No business with id '{business_id}'"}), 404

    auth = "1" if token_ok() else "0"
    return cached(f"id:{business_id}:{auth}", build)


@app.route("/businesses")
def list_all():
    def build():
        raw = list(live_businesses.find({}).limit(50))
        if not raw:
            raw = list(businesses.find({}))
        records = [to_sbp_record(r) for r in raw]
        envelope = build_envelope(records, query_params={})
        envelope = apply_auth_policy(envelope, token_ok())
        return jsonify(envelope)

    auth = "1" if token_ok() else "0"
    return cached(f"list:all:{auth}", build)


@app.route("/top-rated")
def top_rated():
    limit = int(request.args.get("limit", 10))
    cursor = live_businesses.find({"communityRating": {"$ne": None}}).sort(
        "communityRating", -1
    ).limit(limit)
    records = [to_sbp_record(r) for r in cursor]
    if not records:
        cursor = businesses.find({}).sort("communityRating", -1).limit(limit)
        records = [to_sbp_record(r) for r in cursor]
    envelope = build_envelope(records, query_params={"limit": limit})
    return jsonify(apply_auth_policy(envelope, token_ok()))


@app.route("/stats")
def stats():
    term = request.args.get("term", "coffee")
    location = request.args.get("location", DEFAULT_LOCATION)
    try:
        records, primary, _ = live_search.search_live(term, location, limit=30)
        by_cat = {}
        for r in records:
            cat = (r.get("categories") or ["other"])[0]
            by_cat.setdefault(cat, {"count": 0, "ratings": []})
            by_cat[cat]["count"] += 1
            if r.get("rating"):
                by_cat[cat]["ratings"].append(r["rating"])
        rows = [
            {
                "category": c,
                "count": d["count"],
                "avg_rating": round(sum(d["ratings"]) / len(d["ratings"]), 2)
                if d["ratings"]
                else None,
            }
            for c, d in sorted(by_cat.items(), key=lambda x: -x[1]["count"])
        ]
        return jsonify({
            "schema_version": SCHEMA_VERSION,
            "data_source": primary,
            "total_businesses": len(records),
            "by_category": rows,
        })
    except Exception:
        pass
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_rating": {"$avg": "$communityRating"}}},
        {"$sort": {"count": -1}},
    ]
    by_cat = [
        {"category": r["_id"], "count": r["count"], "avg_rating": round(r["avg_rating"], 2)}
        for r in businesses.aggregate(pipeline)
    ]
    return jsonify({
        "schema_version": SCHEMA_VERSION,
        "data_source": "local",
        "total_businesses": businesses.count_documents({}),
        "by_category": by_cat,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5002)
