import os
import sys
from unittest.mock import patch

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

os.environ["USE_MONGITA"] = "true"
os.environ["SBP_API_TOKEN"] = "dev-class-token"

SAMPLE_YELP_SEARCH = {
    "businesses": [
        {
            "id": "test-yelp-id",
            "name": "Test Coffee",
            "rating": 4.5,
            "review_count": 10,
            "price": "$$",
            "phone": "+12065551234",
            "url": "https://www.yelp.com/biz/test",
            "image_url": "https://example.com/img.jpg",
            "is_closed": False,
            "categories": [{"alias": "coffee", "title": "Coffee"}],
            "location": {
                "address1": "123 Main St",
                "city": "Seattle",
                "state": "WA",
                "zip_code": "98101",
            },
            "coordinates": {"latitude": 47.6, "longitude": -122.3},
            "distance": 500,
            "transactions": ["pickup"],
        }
    ]
}


@pytest.fixture
def client():
    import runpy

    runpy.run_path(os.path.join(ROOT, "seed_db.py"))
    from app import app

    return app.test_client()


@patch.dict(os.environ, {"YELP_API_KEY": "fake-key"})
@patch("yelp_client.search_businesses", return_value=SAMPLE_YELP_SEARCH)
def test_search_uses_yelp_when_configured(mock_search, client):
    r = client.get(
        "/businesses/search",
        query_string={"term": "coffee", "location": "Seattle, WA", "source": "yelp"},
    )
    assert r.status_code == 200
    data = r.json
    assert data["provenance"]["source"] == "Yelp Fusion API"
    assert len(data["businesses"]) == 1
    assert data["businesses"][0]["id"] == "test-yelp-id"
    assert data["businesses"][0]["yelp_url"]


def test_search_local_source(client):
    r = client.get(
        "/businesses/search",
        query_string={"term": "coffee", "location": "Seattle", "source": "local"},
    )
    assert r.status_code == 200
    assert "curated" in r.json["provenance"]["source"].lower()
