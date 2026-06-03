import os
import sys
from unittest.mock import patch

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

os.environ["USE_MONGITA"] = "true"


SAMPLE = [
    {
        "id": "osm-node-99",
        "name": "Real OSM Cafe",
        "categories": ["cafe"],
        "description": "123 Main, Seattle",
        "location": {
            "address_line_1": "123 Main",
            "city": "Seattle",
            "state": "WA",
            "zip_code": "98101",
            "neighborhood": "Capitol Hill",
        },
        "contact": {},
        "tags": ["cafe"],
        "hours": {},
        "quality_flags": {"is_complete": True, "has_name": True},
    }
]


@patch("live_search.search_live", return_value=(SAMPLE, "openstreetmap", ["openstreetmap"]))
def test_search_live_uses_osm(mock_live):
    import runpy

    runpy.run_path(os.path.join(ROOT, "seed_db.py"))
    from app import app

    client = app.test_client()
    r = client.get(
        "/businesses/search",
        query_string={
            "term": "cafe",
            "location": "Seattle, WA",
            "source": "live",
            "refresh": "true",
        },
    )
    assert r.status_code == 200
    data = r.json
    assert data["businesses"][0]["name"] == "Real OSM Cafe"
    assert data["query_summary"]["data_source"] == "openstreetmap"
