import json
import os
import sys

import jsonschema
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

os.environ["USE_MONGITA"] = "true"
os.environ["SBP_API_TOKEN"] = "dev-class-token"


@pytest.fixture(scope="module", autouse=True)
def seed_database():
    import runpy

    runpy.run_path(os.path.join(ROOT, "seed_db.py"))


@pytest.fixture(scope="module")
def flask_client(seed_database):
    from app import app

    return app.test_client()


SCHEMA_PATH = os.path.join(ROOT, "sbp_schema_v1.json")
with open(SCHEMA_PATH, encoding="utf-8") as f:
    LIST_SCHEMA = json.load(f)


def test_health(flask_client):
    r = flask_client.get("/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"


def test_search_validates_schema(flask_client):
    r = flask_client.get(
        "/businesses/search", query_string={"term": "coffee", "location": "Seattle"}
    )
    assert r.status_code == 200
    jsonschema.validate(r.json, LIST_SCHEMA)
    assert r.json["query_summary"]["quality_summary"]["completeness_score"] >= 0.85


def test_search_400_without_params(flask_client):
    r = flask_client.get("/businesses/search")
    assert r.status_code == 400


def test_get_one(flask_client):
    r = flask_client.get("/businesses/sb-001")
    assert r.status_code == 200
    assert r.json["businesses"][0]["id"] == "sb-001"


def test_contact_gated(flask_client):
    r = flask_client.get("/businesses/sb-001")
    assert "email" not in r.json["businesses"][0]["contact"]

    r2 = flask_client.get(
        "/businesses/sb-001",
        headers={"Authorization": "Bearer dev-class-token"},
    )
    assert r2.json["businesses"][0]["contact"].get("email")
