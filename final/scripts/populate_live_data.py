#!/usr/bin/env python3
"""
Pull real small-business data from external APIs into MongoDB.

Usage:
  python scripts/populate_live_data.py              # keyword + neighborhood sweeps
  python scripts/populate_live_data.py --keywords-only
  python scripts/populate_live_data.py --neighborhoods-only
  LIMIT=30 python scripts/populate_live_data.py   # more results per query
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yelp_client
from live_search import persist_records, search_live, search_neighborhood, search_yelp

QUERIES_PATH = os.path.join(os.path.dirname(__file__), "populate_queries.json")


def load_queries() -> tuple[list[tuple[str, str]], list[str]]:
    with open(QUERIES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    keywords = [tuple(pair) for pair in data.get("keyword_searches", [])]
    neighborhoods = list(data.get("neighborhood_sweeps", []))
    return keywords, neighborhoods


def main():
    parser = argparse.ArgumentParser(description="Cache live OSM/Yelp businesses in MongoDB")
    parser.add_argument("--keywords-only", action="store_true")
    parser.add_argument("--neighborhoods-only", action="store_true")
    args = parser.parse_args()

    per_query_limit = int(os.environ.get("LIMIT", "15"))
    max_keywords = int(os.environ.get("MAX_KEYWORDS", "0"))  # 0 = all
    os.environ.setdefault("USE_MONGITA", "true")

    from mongita import MongitaClientDisk

    db = MongitaClientDisk()["sbp_final"]
    live = db["live_businesses"]
    before = live.count_documents({})

    keyword_queries, neighborhoods = load_queries()
    run_keywords = not args.neighborhoods_only
    run_neighborhoods = not args.keywords_only

    if run_keywords:
        queries = keyword_queries[:max_keywords] if max_keywords > 0 else keyword_queries
        print(f"Keyword searches ({len(queries)} queries, limit={per_query_limit})...")
        for term, loc in queries:
            records = []
            src = "none"
            if yelp_client.is_configured():
                try:
                    records = search_yelp(term, loc, 8000, limit=per_query_limit)
                    src = "yelp"
                except Exception as e:
                    print(f"  {term}: yelp skip ({e})")
            if len(records) < 5:
                try:
                    records, src, _ = search_live(
                        term, loc, limit=per_query_limit, fast=True
                    )
                except Exception as e:
                    print(f"  {term}: live skip ({e})")
            n = persist_records(live, records)
            print(f"  {term} @ {loc}: {len(records)} ({src}), saved {n}")
            time.sleep(0.5)

    if run_neighborhoods:
        print(f"\nNeighborhood sweeps ({len(neighborhoods)} areas, limit={per_query_limit})...")
        for loc in neighborhoods:
            records = search_neighborhood(loc, limit=per_query_limit)
            n = persist_records(live, records)
            print(f"  [all shops] @ {loc}: {len(records)}, saved {n}")
            time.sleep(1.0)

    after = live.count_documents({})
    print(f"\nDone. {after} live records in database (+{after - before} net new upserts).")


if __name__ == "__main__":
    main()
