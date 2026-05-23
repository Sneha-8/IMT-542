"""Load small_businesses.json into MongoDB / Mongita for the final API."""
import json
import os

USE_MONGITA = os.environ.get("USE_MONGITA", "false").lower() == "true"

if USE_MONGITA:
    from mongita import MongitaClientDisk

    client = MongitaClientDisk()
else:
    from pymongo import MongoClient

    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))

db = client["sbp_final"]
collection = db["businesses"]

DATA_FILE = os.path.join(os.path.dirname(__file__), "small_businesses.json")
with open(DATA_FILE, encoding="utf-8") as f:
    rows = json.load(f)

collection.delete_many({})
collection.insert_many(rows)

if not USE_MONGITA:
    collection.create_index("id", unique=True)
    collection.create_index("category")
    collection.create_index("location.zip")
    collection.create_index("location.neighborhood")
    collection.create_index("tags")
    collection.create_index([("communityRating", -1)])

print(f"Seeded {collection.count_documents({})} businesses into sbp_final.businesses")
