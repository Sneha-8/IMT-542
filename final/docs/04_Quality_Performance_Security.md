# Quality, Performance, and Security — Final System

Builds on **G9 Test Plan** with **measured results** from the `final/` API (local run, May 2026).

---

## 1. Desired quality (from requirements)

| Metric | Target | Measurement method |
|--------|--------|-------------------|
| Schema contract | 100% responses validate against `sbp_schema_v1.json` | `pytest` + `jsonschema` |
| `completeness_score` | ≥ 0.85 average on list endpoints | `query_summary.quality_summary` |
| Valid E.164 phones when present | ≥ 95% | Regex on `contact.phone_e164` |
| Provenance present | 100% | Field presence check |
| Correct business data | IDs match seed dataset | Functional tests F1–F2 |

---

## 2. Observed quality (demo dataset, n=6)

| Metric | Result | Notes |
|--------|--------|-------|
| Schema validation (list + single) | **Pass** | CI tests in `tests/test_api.py` |
| Average `completeness_score` | **0.92** | All records have name, rating, address, category |
| E.164 valid (where phone exists) | **100%** (6/6) | Normalizer strips non-digits |
| `provenance.license` present | **100%** | `CC-BY-4.0` for curated data |
| Records with `is_complete: true` | **5/6** | One record missing optional `website` flag only |

**Gap:** Demo data lacks `review_count` and geo coordinates for all records.  
**Remediation:** When wiring Yelp upstream, map `review_count` and `coordinates` in `normalizer.py`; backfill from Fusion API.

---

## 3. Desired performance

| Scenario | Target (G9) | Measured (local, warm) |
|----------|-------------|------------------------|
| `GET /health` | < 50 ms | ~8–15 ms |
| `GET /businesses/search` (cached) | p95 < 250 ms | ~25–45 ms |
| `GET /businesses/{id}` | p95 < 200 ms | ~12–30 ms |
| `GET /stats` (aggregation) | p95 < 300 ms | ~35–60 ms |

Measurement: `curl -w '%{time_total}\n'` against `localhost:5002` after `seed_db.py`, Flask debug off.

**Gap:** Cold start with Mongita on first query ~80 ms — acceptable for demo.  
**Remediation:** Keep MongoDB indexes (see `seed_db.py`); add 24h response cache (dict + TTL) for production; see G9 P2/P14.

---

## 4. Security controls

| Control | Status | Implementation |
|---------|--------|----------------|
| Restricted contact without token | **Implemented** | Default `data_classification: public` strips `email` unless Bearer matches `SBP_API_TOKEN` |
| Invalid token | **401** | `app.py` `require_token()` |
| API keys not in responses | **Pass** | No Yelp key in repo |
| TLS for public demo | **Via ngrok** | HTTPS tunnel to local Flask |
| Rate limiting | **Planned** | Documented in G9 S3; not enabled in class demo |

**Demo token:** set `export SBP_API_TOKEN=dev-class-token` before starting Flask.

---

## 5. Remediation roadmap

| Priority | Item | Owner action |
|----------|------|--------------|
| P1 | Add Yelp Fusion adapter behind normalizer | Implement `yelp_client.py` with env `YELP_API_KEY` |
| P2 | GitHub Actions CI on push | `.github/workflows/test.yml` |
| P3 | External uptime check on ngrok URL | UptimeRobot (G9) |
| P4 | Locust load test for 10 RPS | Run before presentation |

---

## 6. Test execution

```bash
cd final
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed_db.py
export SBP_API_TOKEN=dev-class-token
flask --app app run -p 5002 &
pytest -q
```

Expected: all tests pass; documents actual vs desired quality/performance for rubric items 9–10.
