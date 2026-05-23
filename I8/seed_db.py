"""
seed_db.py — Loads small_businesses.json into the NoSQL store.
Run once before starting the API:  python seed_db.py

Works with either real MongoDB (pymongo) or local file-based Mongita.
Flip USE_MONGITA = True if you don't have MongoDB installed.
"""
import json
import os

USE_MONGITA = False  # set True for a no-install file-based NoSQL store

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

# Clean slate, then bulk-insert
collection.delete_many({})
collection.insert_many(businesses)

# Helpful indexes for the new query endpoints (skip for Mongita)
if not USE_MONGITA:
      collection.create_index("id", unique=True)
      collection.create_index("category")
      collection.create_index("location.zip")
      collection.create_index("location.neighborhood")
      collection.create_index("tags")
      collection.create_index([("communityRating", -1)])

print(f"Seeded {collection.count_documents({})} businesses into NoSQL store.")
print("Database: i8_local_business   Collection: businesses")
