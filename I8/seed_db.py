"""
seed_db.py — Loads small_businesses.json into the NoSQL store.
Run once before starting the API:  python seed_db.py
Works with either real MongoDB (pymongo) or local file-based Mongita.
Set env var USE_MONGITA=1 to use file-based store (no install needed).
Default is now Mongita so the demo runs without installing MongoDB.
"""
import json
import os

USE_MONGITA = os.environ.get("USE_MONGITA", "1") == "1"

if USE_MONGITA:
    from mongita import MongitaClientDisk
    client = MongitaClientDisk()
else:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")

db = client["i8_local_business"]
collection = db["businesses"]

DATA_FILE = os.path.join(os.path.dirname(__file__), "small_businesses.json")
with open(DATA_FILE, "r", encoding="utf-8") as f:
    businesses = json.load(f)

collection.delete_many({})
collection.insert_many(businesses)

if not USE_MONGITA:
    collection.create_index("id", unique=True)
    collection.create_index("category")
    collection.create_index("location.zip")
    collection.create_index("location.neighborhood")
    collection.create_index("tags")
    collection.create_index([("communityRating", -1)])

backend = "Mongita (file-based)" if USE_MONGITA else "MongoDB"
print(f"Seeded {collection.count_documents({})} businesses into NoSQL store.")
print(f"Backend: {backend}")
print("Database: i8_local_business  Collection: businesses")
