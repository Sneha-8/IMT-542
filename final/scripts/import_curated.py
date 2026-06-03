#!/usr/bin/env python3
"""
Merge extra curated businesses from a JSON file into sbp_final.businesses.

Edit small_businesses.json or pass a file:
  python scripts/import_curated.py
  python scripts/import_curated.py my_new_shops.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "..", "small_businesses.json")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    os.environ.setdefault("USE_MONGITA", "true")

    with open(path, encoding="utf-8") as f:
        rows = json.load(f)

    from mongita import MongitaClientDisk

    coll = MongitaClientDisk()["sbp_final"]["businesses"]
    n = 0
    for doc in rows:
        if not doc.get("id"):
            continue
        coll.replace_one({"id": doc["id"]}, doc, upsert=True)
        n += 1
    print(f"Upserted {n} curated records from {path}")


if __name__ == "__main__":
    main()
