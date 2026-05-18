from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "small_businesses.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    businesses = json.load(f)


def find_by_id(business_id):
    for biz in businesses:
        if biz["id"] == business_id:
            return biz
    return None


@app.route("/")
def index():
    return jsonify({
        "message": "Local Small Business Discovery API",
        "description": "Find and support small businesses near you.",
        "total_businesses": len(businesses),
        "endpoints": {
            "GET /businesses": "List all businesses",
            "GET /businesses/<id>": "Get one business by ID",
            "GET /businesses/category/<cat>": "Filter by category",
            "GET /businesses/zip/<zip>": "Filter by ZIP code",
            "GET /businesses/neighborhood/<n>": "Filter by neighborhood",
            "GET /search?q=<keyword>": "Search by keyword",
            "GET /categories": "List all categories"
        }
    })


@app.route("/businesses", methods=["GET"])
def list_businesses():
    summary = [
        {
            "id": biz["id"],
            "name": biz["name"],
            "category": biz["category"],
            "neighborhood": biz["location"]["neighborhood"],
            "zip": biz["location"]["zip"],
            "rating": biz["communityRating"],
            "description": biz["description"]
        }
        for biz in businesses
    ]
    return jsonify({"total": len(summary), "businesses": summary})


@app.route("/businesses/<business_id>", methods=["GET"])
def get_business(business_id):
    biz = find_by_id(business_id)
    if not biz:
        return jsonify({"error": f"No business found with id '{business_id}'"}), 404
    return jsonify(biz)


@app.route("/businesses/category/<category>", methods=["GET"])
def get_by_category(category):
    matches = [b for b in businesses if b["category"].lower() == category.lower()]
    if not matches:
        return jsonify({"error": f"No businesses found in category '{category}'"}), 404
    return jsonify({"category": category, "total": len(matches), "businesses": matches})


@app.route("/businesses/zip/<zipcode>", methods=["GET"])
def get_by_zip(zipcode):
    matches = [b for b in businesses if b["location"]["zip"] == zipcode]
    if not matches:
        return jsonify({"error": f"No businesses found in ZIP '{zipcode}'"}), 404
    return jsonify({"zip": zipcode, "total": len(matches), "businesses": matches})


@app.route("/businesses/neighborhood/<neighborhood>", methods=["GET"])
def get_by_neighborhood(neighborhood):
    matches = [b for b in businesses if b["location"]["neighborhood"].lower() == neighborhood.lower()]
    if not matches:
        return jsonify({"error": f"No businesses found in '{neighborhood}'"}), 404
    return jsonify({"neighborhood": neighborhood, "total": len(matches), "businesses": matches})


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"error": "Provide a search term with ?q=<keyword>"}), 400
    matches = [b for b in businesses if query in json.dumps(b).lower()]
    return jsonify({"query": query, "total": len(matches), "businesses": matches})


@app.route("/categories", methods=["GET"])
def list_categories():
    cats = sorted(set(biz["category"] for biz in businesses))
    return jsonify({"categories": cats})


if __name__ == "__main__":
    app.run(debug=True, port=5002)
