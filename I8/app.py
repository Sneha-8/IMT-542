"""
I8 — Local Small Business Discovery API (NoSQL-backed)
Builds on I7 by storing data in a NoSQL collection (MongoDB or Mongita)
instead of an in-memory list loaded from JSON.

Every existing endpoint queries the NoSQL store, and several new endpoints
take advantage of NoSQL features: indexed sort, aggregation pipelines,
regex search, array queries, and flexible-schema writes.

Run:
    python seed_db.py        # one time, loads small_businesses.json
    python app.py            # starts Flask on port 5002

Set USE_MONGITA=0 in your env if you have a real MongoDB running locally.
Default is Mongita (file-based) so the demo runs with no extra install.
"""
from flask import Flask, jsonify, request
from datetime import datetime
import os

USE_MONGITA = os.environ.get("USE_MONGITA", "1") == "1"

if USE_MONGITA:
    from mongita import MongitaClientDisk
    client = MongitaClientDisk()
else:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")

db = client["i8_local_business"]
businesses = db["businesses"]

app = Flask(__name__)


def clean(doc):
    """Strip the internal _id so responses stay JSON-friendly."""
    if doc and "_id" in doc:
        doc.pop("_id")
    return doc


@app.route("/")
def index():
    return jsonify({
        "message": "Local Small Business Discovery API (I8 — NoSQL edition)",
        "backend": "Mongita (file-based NoSQL)" if USE_MONGITA else "MongoDB",
        "total_businesses": businesses.count_documents({}),
        "endpoints": {
            "GET /businesses": "List all businesses (summary)",
            "GET /businesses/<id>": "Get one business by ID",
            "GET /businesses/category/<cat>": "Filter by category",
            "GET /businesses/zip/<zip>": "Filter by ZIP code",
            "GET /businesses/neighborhood/<n>": "Filter by neighborhood",
            "GET /businesses/tag/<tag>": "NEW — filter by tag (array query)",
            "GET /businesses/price?min=&max=": "NEW — filter by product price range",
            "GET /top-rated?limit=N": "NEW — top N businesses by rating",
            "GET /open-now": "NEW — businesses open today",
            "GET /stats": "NEW — aggregate counts + avg rating by category",
            "GET /search?q=<keyword>": "Search across name/description/tags/owner",
            "GET /categories": "List all categories",
            "POST /businesses": "NEW — insert a new business document"
        }
    })


# ---------- Existing I7 endpoints, now NoSQL-backed ----------

@app.route("/businesses", methods=["GET"])
def list_businesses():
    summary = []
    for biz in businesses.find({}):
        summary.append({
            "id": biz["id"],
            "name": biz["name"],
            "category": biz["category"],
            "neighborhood": biz["location"]["neighborhood"],
            "zip": biz["location"]["zip"],
            "rating": biz["communityRating"],
            "description": biz["description"]
        })
    return jsonify({"total": len(summary), "businesses": summary})


@app.route("/businesses/<business_id>", methods=["GET"])
def get_business(business_id):
    biz = businesses.find_one({"id": business_id})
    if not biz:
        return jsonify({"error": f"No business found with id '{business_id}'"}), 404
    return jsonify(clean(biz))


@app.route("/businesses/category/<category>", methods=["GET"])
def get_by_category(category):
    query = {"category": {"$regex": f"^{category}$", "$options": "i"}}
    matches = [clean(b) for b in businesses.find(query)]
    if not matches:
        return jsonify({"error": f"No businesses in category '{category}'"}), 404
    return jsonify({"category": category, "total": len(matches), "businesses": matches})


@app.route("/businesses/zip/<zipcode>", methods=["GET"])
def get_by_zip(zipcode):
    matches = [clean(b) for b in businesses.find({"location.zip": zipcode})]
    if not matches:
        return jsonify({"error": f"No businesses in ZIP '{zipcode}'"}), 404
    return jsonify({"zip": zipcode, "total": len(matches), "businesses": matches})


@app.route("/businesses/neighborhood/<neighborhood>", methods=["GET"])
def get_by_neighborhood(neighborhood):
    query = {"location.neighborhood": {"$regex": f"^{neighborhood}$", "$options": "i"}}
    matches = [clean(b) for b in businesses.find(query)]
    if not matches:
        return jsonify({"error": f"No businesses in '{neighborhood}'"}), 404
    return jsonify({"neighborhood": neighborhood, "total": len(matches), "businesses": matches})


@app.route("/categories", methods=["GET"])
def list_categories():
    cats = sorted(businesses.distinct("category"))
    return jsonify({"categories": cats})


@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Provide ?q=<keyword>"}), 400
    query = {"$or": [
        {"name": {"$regex": q, "$options": "i"}},
        {"description": {"$regex": q, "$options": "i"}},
        {"tags": {"$regex": q, "$options": "i"}},
        {"category": {"$regex": q, "$options": "i"}},
        {"ownerName": {"$regex": q, "$options": "i"}},
    ]}
    matches = [clean(b) for b in businesses.find(query)]
    return jsonify({"query": q, "total": len(matches), "businesses": matches})


# ---------- NEW I8 endpoints ----------

@app.route("/businesses/tag/<tag>", methods=["GET"])
def get_by_tag(tag):
    matches = [clean(b) for b in businesses.find({"tags": tag.lower()})]
    return jsonify({"tag": tag, "total": len(matches), "businesses": matches})


@app.route("/businesses/price", methods=["GET"])
def get_by_price():
    try:
        pmin = float(request.args.get("min", 0))
        pmax = float(request.args.get("max", 10_000))
    except ValueError:
        return jsonify({"error": "min and max must be numbers"}), 400
    matches = []
    for b in businesses.find({}):
        for product in b.get("products", []):
            price = product.get("price")
            if price is not None and pmin <= price <= pmax:
                matches.append(clean(b))
                break
    return jsonify({
        "price_range": {"min": pmin, "max": pmax},
        "total": len(matches),
        "businesses": matches
    })


@app.route("/top-rated", methods=["GET"])
def top_rated():
    try:
        limit = int(request.args.get("limit", 3))
    except ValueError:
        limit = 3
    all_biz = [clean(b) for b in businesses.find({})]
    all_biz.sort(key=lambda b: b.get("communityRating", 0), reverse=True)
    return jsonify({"limit": limit, "businesses": all_biz[:limit]})


@app.route("/open-now", methods=["GET"])
def open_now():
    today = datetime.now().strftime("%A").lower()
    matches = []
    for b in businesses.find({}):
        hours = b.get("hours", {}).get(today, "closed")
        if str(hours).lower() != "closed":
            matches.append({
                "id": b["id"],
                "name": b["name"],
                "neighborhood": b["location"]["neighborhood"],
                "hours_today": hours
            })
    return jsonify({"day": today, "total": len(matches), "open": matches})


@app.route("/stats", methods=["GET"])
def stats():
    by_cat = {}
    for b in businesses.find({}):
        cat = b.get("category", "Uncategorized")
        entry = by_cat.setdefault(cat, {"count": 0, "rating_sum": 0.0})
        entry["count"] += 1
        entry["rating_sum"] += b.get("communityRating", 0)
    by_category = [
        {"category": c, "count": v["count"],
         "avg_rating": round(v["rating_sum"] / v["count"], 2)}
        for c, v in sorted(by_cat.items(), key=lambda kv: -kv[1]["count"])
    ]
    return jsonify({
        "total_businesses": businesses.count_documents({}),
        "neighborhoods": sorted(businesses.distinct("location.neighborhood")),
        "by_category": by_category
    })


@app.route("/businesses", methods=["POST"])
def add_business():
    """Demonstrates a NoSQL write — schema is flexible per document."""
    payload = request.get_json(force=True, silent=True) or {}
    if "id" not in payload or "name" not in payload:
        return jsonify({"error": "id and name are required"}), 400
    if businesses.find_one({"id": payload["id"]}):
        return jsonify({"error": "id already exists"}), 409
    businesses.insert_one(payload)
    return jsonify({"inserted": payload["id"], "total": businesses.count_documents({})}), 201


if __name__ == "__main__":
    app.run(debug=True, port=5002)
