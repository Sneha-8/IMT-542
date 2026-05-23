"""
kg_app.py — Optional Knowledge Graph variant for I8.

Models the same small-business dataset as a graph using NetworkX:
    Nodes : Business, Category, Neighborhood, Tag, Owner
    Edges : BELONGS_TO, LOCATED_IN, TAGGED_AS, OWNED_BY

Run:
    flask --app kg_app run -p 5003
"""
import json
import os
from flask import Flask, jsonify, request
import networkx as nx

app = Flask(__name__)
G = nx.MultiDiGraph()

DATA_FILE = os.path.join(os.path.dirname(__file__), "small_businesses.json")
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for b in data:
    biz_id = b["id"]
    G.add_node(biz_id, type="Business", name=b["name"], rating=b["communityRating"])
    G.add_node(b["category"], type="Category")
    G.add_edge(biz_id, b["category"], rel="BELONGS_TO")
    hood = b["location"]["neighborhood"]
    G.add_node(hood, type="Neighborhood")
    G.add_edge(biz_id, hood, rel="LOCATED_IN")
    G.add_node(b["ownerName"], type="Owner")
    G.add_edge(biz_id, b["ownerName"], rel="OWNED_BY")
    for tag in b.get("tags", []):
        G.add_node(tag, type="Tag")
        G.add_edge(biz_id, tag, rel="TAGGED_AS")


@app.route("/")
def index():
    return jsonify({
        "message": "Local Small Business Knowledge Graph API (I8 KG variant)",
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "endpoints": {
            "GET /graph/summary": "Counts per node type",
            "GET /graph/business/<id>": "Neighbors of a business node",
            "GET /graph/category/<cat>": "All businesses in a category",
            "GET /graph/neighborhood/<n>": "All businesses in a neighborhood",
            "GET /graph/related/<id>": "Businesses sharing tags / hood / category",
            "GET /graph/path?source=&target=": "Shortest path between two nodes"
        }
    })


@app.route("/graph/summary")
def summary():
    counts = {}
    for _, attrs in G.nodes(data=True):
        t = attrs.get("type", "Unknown")
        counts[t] = counts.get(t, 0) + 1
    return jsonify({"node_counts": counts, "edges": G.number_of_edges()})


@app.route("/graph/business/<biz_id>")
def biz_neighbors(biz_id):
    if biz_id not in G:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "business": biz_id,
        "neighbors": [
            {"node": n, "type": G.nodes[n].get("type"), "rel": d["rel"]}
            for _, n, d in G.out_edges(biz_id, data=True)
        ]
    })


@app.route("/graph/related/<biz_id>")
def related(biz_id):
    if biz_id not in G:
        return jsonify({"error": "not found"}), 404
    related_biz = set()
    for _, n in G.out_edges(biz_id):
        for src, _ in G.in_edges(n):
            if src != biz_id and G.nodes[src].get("type") == "Business":
                related_biz.add(src)
    return jsonify({"business": biz_id, "related": sorted(related_biz)})


@app.route("/graph/category/<cat>")
def by_cat(cat):
    biz = [src for src, _ in G.in_edges(cat) if G.nodes[src].get("type") == "Business"]
    return jsonify({"category": cat, "businesses": biz})


@app.route("/graph/neighborhood/<hood>")
def by_hood(hood):
    biz = [src for src, _ in G.in_edges(hood) if G.nodes[src].get("type") == "Business"]
    return jsonify({"neighborhood": hood, "businesses": biz})


@app.route("/graph/path")
def path():
    s = request.args.get("source")
    t = request.args.get("target")
    if not s or not t:
        return jsonify({"error": "provide ?source=&target="}), 400
    try:
        p = nx.shortest_path(G.to_undirected(), s, t)
        return jsonify({"source": s, "target": t, "path": p, "length": len(p) - 1})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5003)
