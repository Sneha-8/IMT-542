from normalizer import apply_auth_policy, build_envelope, quality_flags, to_e164, to_sbp_record

SAMPLE = {
    "id": "sb-001",
    "name": "Test Cafe",
    "category": "cafe",
    "description": "A test shop",
    "location": {
        "address": "1 Main St",
        "city": "Seattle",
        "state": "WA",
        "zip": "98101",
        "neighborhood": "Capitol Hill",
    },
    "contact": {"phone": "206-555-0101", "email": "a@b.com"},
    "tags": ["wifi"],
    "communityRating": 4.5,
}


def test_e164():
    assert to_e164("206-555-0101") == "+12065550101"


def test_quality_flags_complete():
    flags = quality_flags(SAMPLE)
    assert flags["has_name"]
    assert flags["is_complete"]


def test_auth_strips_email():
    rec = to_sbp_record(SAMPLE)
    env = build_envelope([rec])
    public = apply_auth_policy(env, token_ok=False)
    assert "email" not in public["businesses"][0]["contact"]


def test_auth_keeps_email():
    rec = to_sbp_record(SAMPLE)
    env = build_envelope([rec])
    private = apply_auth_policy(env, token_ok=True)
    assert private["businesses"][0]["contact"].get("email") == "a@b.com"
