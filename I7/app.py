"""
I7 API Access - Flask API Server
Course: IMT 542 A Sp 26 - Portable Information Structures
Author: Sneha

Description:
    A Flask REST API that hosts a local small business discovery information
        structure. Users can browse, filter, and search small businesses in their
            area to find and support local owners.

                Data is loaded from small_businesses.json into memory at server startup.

                How to Run:
                    1. Install Flask:      pip install flask
                        2. Run the server:     flask --app app run -p 5002
                            3. Expose via ngrok:   ngrok http http://localhost:5002
                            """

from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# -- Load data into memory at startup -----------------------------------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "small_businesses.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
      businesses = json.load(f)


# -- Helper -------------------------------------------------------------------
def find_by_id(business_id):
      for biz in businesses:
                if biz["id"] == business_id:
                              return biz
                      return None


# -- Routes -------------------------------------------------------------------

@app.route("/")
def index():
      """Health check - describes the API and lists endpoints."""
      return jsonify({
          "message": "Local Small Business Discovery API",
          "description": "Find and support small businesses near you.",
          "total_businesses": len(businesses),
          "endpoints": {
              "GET /businesses":                  "List all businesses",
              "GET /businesses/<id>":             "Get one business by ID",
              "GET /businesses/category/<cat>":   "Filter by category (e.g. cafe, retail)",
              "GET /businesses/zip/<zip>":        "Filter by ZIP code",
              "GET /businesses/neighborhood/<n>": "Filter by neighborhood name",
              "GET /search?q=<keyword>":          "Search by keyword across all fields",
              "GET /categories":                  "List all available categories"
          }
      })


@app.route("/businesses", methods=["GET"])
def list_businesses():
      """Return all businesses with a short summary of each."""
      summary = [
          {
              "id":           biz["id"],
              "name":         biz["name"],
              "category":     biz["category"],
              "neighborhood": biz["location"]["neighborhood"],
              "zip":          biz["location"]["zip"],
              "rating":       biz["communityRating"],
              "description":  biz["description"]
          }
          for biz in businesses
      ]
      return jsonify({"total": len(summary), "businesses": summary})


@app.route("/businesses/<business_id>", methods=["GET"])
def get_business(business_id):
      """Return the full record for a single business by its ID."""
      biz = find_by_id(business_id)
      if not biz:
                return jsonify({"error": f"No business found with id '{business_id}'"}), 404
            return jsonify(biz)


@app.route("/businesses/category/<category>", methods=["GET"])
def get_by_category(category):
      """Return all businesses in a given category."""
    matches = [
              biz for biz in businesses
              if biz["category"].lower() == category.lower()
    ]
    if not matches:
              return jsonify({"error": f"No businesses found in category '{category}'"}), 404
          return jsonify({"category": category, "total": len(matches), "businesses": matches})


@app.route("/businesses/zip/<zipcode>", methods=["GET"])
def get_by_zip(zipcode):
      """Return all businesses in a given ZIP code."""
    matches = [
              biz for biz in businesses
              if biz["location"]["zip"] == zipcode
    ]
    if not matches:
              return jsonify({"error": f"No businesses found in ZIP '{zipcode}'"}), 404
          return jsonify({"zip": zipcode, "total": len(matches), "businesses": matches})


@app.route("/businesses/neighborhood/<neighborhood>", methods=["GET"])
def get_by_neighborhood(neighborhood):
      """Return all businesses in a given neighborhood (case-insensitive)."""
    matches = [
              biz for biz in businesses
              if biz["location"]["neighborhood"].lower() == neighborhood.lower()
    ]
    if not matches:
              return jsonify({"error": f"No businesses found in '{neighborhood}'"}), 404
          return jsonify({
                    "neighborhood": neighborhood,
                    "total": len(matches),
                    "businesses": matches
          })


@app.route("/search", methods=["GET"])
def search():
      """Search across all fields for a keyword. Example: GET /search?q=coffee"""
      query = request.args.get("q", "").lower()
      if not query:
                return jsonify({"error": "Provide a search term with ?q=<keyword>"}), 400
            matches = [
                      biz for biz in businesses
                      if query in json.dumps(biz).lower()
            ]
    return jsonify({
              "query": query,
              "total": len(matches),
              "businesses": matches
    })


@app.route("/categories", methods=["GET"])
def list_categories():
      """Return all unique business categories present in the data."""
    cats = sorted(set(biz["category"] for biz in businesses))
    return jsonify({"categories": cats})


# -- Entry point --------------------------------------------------------------
if __name__ == "__main__":
      app.run(debug=True, port=5002)
