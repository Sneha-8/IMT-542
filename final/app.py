"""
IMT 542 Final Project — Small Business Platform API (SBP v1.0)

Run:
    python seed_db.py
    export SBP_API_TOKEN=dev-class-token   # optional, for full contact fields
    flask --app app run -p 5002
    ngrok http 5002
"""
import json
import os
import time
from flask import Flask, jsonify, request

from normalizer import (
    SCHEMA_VERSION,
    apply_auth_policy,
    build_envelope,
    to_sbp_record,
)

USE_MONGITA = os.environ.get("USE_MONGITA", "false").lower() == "true"
API_TOKEN = os.environ.get("SBP_API_TOKEN", "dev-class-token")
CACHE_TTL = 300
_cache: dict = {}

if USE_MONGITA:
    from mongita import MongitaClientDisk

    client = MongitaClientDisk()
else:
    from pymongo import MongoClient

    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))

db = client["sbp_final"]
businesses = db["businesses"]

app = Flask(__name__)


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
        resp.headers["X-Cache"] = "HIT"
        return resp
    resp = fn()
    _cache[key] = {"ts": now, "data": resp}
    resp.headers["X-Cache"] = "MISS"
    return resp


def _matches(doc: dict, term: str, location: str) -> bool:
    """Python-side filter — reliable for small datasets and Mongita."""
    term_ok = True
    loc_ok = True
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
        term_ok = t in hay
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
        loc_ok = loc in loc_hay
    return term_ok and loc_ok


def find_businesses(term: str, location: str) -> list:
    return [d for d in businesses.find({}) if _matches(d, term, location)]


@app.route("/health")
def health():
    return jsonify({"status": "ok", "schema_version": SCHEMA_VERSION})


@app.route("/schema")
def schema_doc():
    path = os.path.join(os.path.dirname(__file__), "sbp_schema_v1.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return jsonify({"schema_version": SCHEMA_VERSION, "json_schema": doc})


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Small Business Platform — Final Project API",
            "schema_version": SCHEMA_VERSION,
            "total_businesses": businesses.count_documents({}),
            "endpoints": {
                "GET /health": "Liveness",
                "GET /schema": "JSON Schema contract",
                "GET /businesses/search": "?term=&location=&radius=",
                "GET /businesses/<id>": "Single SBP record",
                "GET /businesses": "Alias list (no filters)",
                "GET /top-rated": "Top N by rating",
                "GET /stats": "Aggregates by category",
                "GET /open-now": "Open today",
            },
            "auth": "Bearer token for restricted contact fields",
        }
    )


@app.route("/businesses/search")
def search():
    term = request.args.get("term", "")
    location = request.args.get("location", "")
    if not term and not location:
        return jsonify({"error": "Provide term and/or location query params"}), 400

    params = {"term": term, "location": location, "radius": request.args.get("radius")}

    def build():
        raw = find_businesses(term, location)
        for r in raw:
            r.pop("_id", None)
        records = [to_sbp_record(r) for r in raw]
        envelope = build_envelope(records, query_params=params)
        envelope = apply_auth_policy(envelope, token_ok())
        return jsonify(envelope)

    auth = "1" if token_ok() else "0"
    return cached(f"search:{term}:{location}:{auth}", build)


@app.route("/businesses")
def list_all():
    def build():
        raw = list(businesses.find({}))
        records = [to_sbp_record(r) for r in raw]
        envelope = build_envelope(records, query_params={})
        envelope = apply_auth_policy(envelope, token_ok())
        return jsonify(envelope)

    auth = "1" if token_ok() else "0"
    return cached(f"list:all:{auth}", build)


@app.route("/businesses/<business_id>")
def get_one(business_id):
    def build():
        raw = businesses.find_one({"id": business_id})
        if not raw:
            return jsonify({"error": f"No business with id '{business_id}'"}), 404
        if "_id" in raw:
            raw.pop("_id")
        record = to_sbp_record(raw)
        envelope = build_envelope([record], query_params={"id": business_id})
        envelope = apply_auth_policy(envelope, token_ok())
        return jsonify(envelope)

    auth = "1" if token_ok() else "0"
    return cached(f"id:{business_id}:{auth}", build)


@app.route("/top-rated")
def top_rated():
    limit = int(request.args.get("limit", 3))
    cursor = businesses.find({}).sort("communityRating", -1).limit(limit)
    records = [to_sbp_record(r) for r in cursor]
    envelope = build_envelope(records, query_params={"limit": limit})
    return jsonify(apply_auth_policy(envelope, token_ok()))


@app.route("/stats")
def stats():
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "avg_rating": {"$avg": "$communityRating"},
            }
        },
        {"$sort": {"count": -1}},
    ]
    by_cat = [
        {
            "category": r["_id"],
            "count": r["count"],
            "avg_rating": round(r["avg_rating"], 2),
        }
        for r in businesses.aggregate(pipeline)
    ]
    return jsonify(
        {
            "schema_version": SCHEMA_VERSION,
            "total_businesses": businesses.count_documents({}),
            "by_category": by_cat,
        }
    )


@app.route("/open-now")
def open_now():
    from datetime import datetime

    today = datetime.now().strftime("%A").lower()
    open_list = []
    for b in businesses.find({}):
        hours = (b.get("hours") or {}).get(today, "closed")
        if str(hours).lower() != "closed":
            open_list.append(
                {
                    "id": b["id"],
                    "name": b["name"],
                    "neighborhood": b.get("location", {}).get("neighborhood"),
                    "hours_today": hours,
                }
            )
    return jsonify({"day": today, "total": len(open_list), "open": open_list})


if __name__ == "__main__":
    app.run(debug=True, port=5002)
