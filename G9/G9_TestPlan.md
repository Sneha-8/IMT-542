# 🏪 Small Business Platform — Test Plan
## IMT 542 — Portable Information Structures (G9: Control for Quality and Performance)

---

## 📘 Purpose

This document outlines the testing strategy for ensuring the **quality, accuracy, performance, and security** of the Small Business Platform (SBP) information system. It is a **living document** that guides implementation, deployment, and ongoing maintenance, and provides our users (small-business owners, civic data tools, third-party developers, and agentic AI assistants) with assurance that the JSON feed they consume is reliable, fresh, and properly classified.

It builds on prior work:
- **G7** — redesigned schema (`schema_version 1.0`, provenance, `data_classification`, `quality_flags`).
- **G8** — Flask API + ngrok access methodology (`/businesses/search`, `/businesses/{id}`).
- **I8** — NoSQL / Knowledge Graph layer behind the API for caching and relationships.

---

## 📘 System Overview

| Component | Technology | Purpose |
|---|---|---|
| Upstream source | Yelp Fusion API (`GET /v3/businesses/search`) | Raw business listing data |
| Normalization layer | Python (Schema.org `LocalBusiness` mapping, E.164 phone, address splitting) | Convert Yelp records to SBP schema v1.0 |
| Backend API | Flask (`app.py`, port `5002`) | Public REST endpoints |
| Storage | NoSQL / Knowledge Graph cache (I8) | TTL ~24h cached, relationship lookups |
| Public exposure | ngrok HTTPS tunnel (`https://<id>.ngrok-free.app`) | Class-facing demo endpoint |
| Auth | `Authorization: Bearer <token>` for restricted fields | Field-level access control |

### Endpoints under test
- `GET /businesses/search?term=&location=&radius=` → list response
- `GET /businesses/{id}` → single record response
- `GET /health` → liveness probe
- `GET /schema` → schema document / version

---

## 📘 Test Objectives

1. Verify every documented endpoint returns the contract defined in G7/G8 (schema v1.0).
2. Confirm that normalization (phones → E.164, address splitting, category mapping) is deterministic and correct.
3. Confirm that `data_classification` gating actually blocks restricted fields without a valid bearer token.
4. Measure latency and stability under realistic and burst load.
5. Detect upstream failures (Yelp rate limit, ngrok tunnel down, cache miss storms) and respond gracefully.
6. Provide clear, auditable feedback (provenance, `last_validated`, `completeness_score`) on every response.

---

## 📘 Functional Testing

| # | Test Case | Method | Input | Expected Result |
|---|---|---|---|---|
| F1 | Happy-path search | `curl` / `pytest` | `term=bakery, location=Seattle, WA, radius=5000` | `200`, valid SBP schema v1.0, `businesses[]` non-empty |
| F2 | Single record fetch | `pytest` | Valid Yelp `id` | `200`, single record matching `businesses[]` shape |
| F3 | Schema contract validation | `jsonschema` validator | Any `200` response | Validates against `sbp.schema.json` (no extra/missing required fields) |
| F4 | Empty / invalid query | `curl` | `term=`, `location=` | `400` with `{error, message}`, no stack trace |
| F5 | Unknown business id | `pytest` | `id=DOES_NOT_EXIST` | `404`, structured error |
| F6 | Phone normalization | Unit test | Yelp raw `"+1 (206) 555-0192"` | Output `phone_e164 == "+12065550192"` |
| F7 | Address splitting | Unit test | Yelp `location.display_address` | `address_line_1/2`, `city`, `state`, `zip_code` populated |
| F8 | Category alignment | Unit test | Yelp `categories[].alias` | Mapped to Schema.org `LocalBusiness` category slugs |
| F9 | `data_classification=restricted` gating (no token) | `pytest` | `GET /businesses/{id}` without `Authorization` | Restricted fields (e.g. `contact`, owner info) are stripped; public fields present |
| F10 | `data_classification=restricted` with valid token | `pytest` | Same with bearer token | Full record returned |
| F11 | Provenance block present | `pytest` | Any `200` | `provenance.source`, `endpoint`, `query_params`, `retrieved_at`, `license`, `api_key_owner` all populated |
| F12 | Quality summary present | `pytest` | Any `200` | `query_summary.quality_summary.completeness_score` between 0 and 1; `last_validated` ISO-8601 |
| F13 | Per-record `quality_flags` | `pytest` | Any business record | All booleans present; `is_complete` consistent with individual flags |
| F14 | Cache freshness (TTL 24h) | Time-based test | Same query twice | 2nd call hits cache (header `X-Cache: HIT`); after TTL → `MISS` and `retrieved_at` updates |
| F15 | CORS for browser client | DevTools | Preflight from allowed origin | `200`, correct `Access-Control-Allow-Origin` |
| F16 | Schema version endpoint | `curl` | `GET /schema` | Returns current `schema_version` and JSON Schema doc |

---

## 📘 Performance Testing

| # | Test Case | Tool | Target |
|---|---|---|---|
| P1 | Cold-start latency (ngrok + Flask after idle) | `curl -w` / Postman | < 2.5 s p95 |
| P2 | Warm cache search | `pytest-benchmark` | < 250 ms p95 |
| P3 | Uncached search (calls Yelp) | `pytest-benchmark` | < 1.5 s p95 |
| P4 | Single-record fetch | `pytest-benchmark` | < 200 ms p95 |
| P5 | Sustained load: 10 RPS for 5 min | `locust` / `k6` | Error rate < 1%, p95 < 1 s |
| P6 | Burst load: 50 concurrent users | `locust` | API remains responsive; no 5xx; queue does not unbound |
| P7 | Yelp rate-limit behavior | Scripted | When Yelp returns `429`, SBP returns `503` + `Retry-After` and serves cached data if available |
| P8 | Memory / file-descriptor stability | OS metrics during P5 | No monotonic leak over the run |
| P9 | Cache hit ratio under realistic mix | `locust` | ≥ 70% hit rate for repeat queries within TTL |

---

## 📘 Data Quality Tests (ongoing)

| # | Metric | Target | Source |
|---|---|---|---|
| Q1 | `completeness_score` per response | ≥ 0.85 average | `query_summary.quality_summary` |
| Q2 | % records with valid E.164 phone | ≥ 95% | Regex `^\+[1-9]\d{1,14}$` |
| Q3 | % records with non-null `rating` | ≥ 98% | Field check |
| Q4 | % records with full address | ≥ 90% | `address_line_1`, `city`, `state`, `zip_code` |
| Q5 | Schema drift | 0 unexpected fields | `jsonschema` strict mode |
| Q6 | Broken `yelp_url` links | 0 | Periodic HEAD check (sampled) |
| Q7 | License compliance | 100% responses carry `provenance.license` | Field check |

---

## 📘 Security & Compliance Tests

| # | Test Case | Method | Expected |
|---|---|---|---|
| S1 | Restricted fields never leak unauthenticated | Black-box scan against all endpoints | `contact`, owner details absent |
| S2 | Bearer token validation | `pytest` | Invalid/expired token → `401` |
| S3 | Rate limit per IP (abuse) | `locust` | After threshold, `429` returned with `Retry-After` |
| S4 | TLS only (no plaintext over ngrok) | Manual `curl http://` | Redirects or refuses |
| S5 | API key never echoed | Response scanner | Yelp/internal keys never appear in body, headers, or errors |
| S6 | License field present in cached + live responses | Field check | `provenance.license` always set |
| S7 | Logs scrub PII | Log inspection | No phone numbers, no bearer tokens in stdout/stderr |

---

## 📘 Alarms & Actions

| Alarm | Trigger | Action |
|---|---|---|
| **Uptime ping failure** | `GET /health` fails for 1 min | Email/Slack alert to maintainer; auto-restart Flask process |
| **High latency** | p95 > 2 s for 5 consecutive minutes | Page maintainer; warm cache; investigate Yelp upstream |
| **5xx spike** | More than 3 × `500` in 1 minute | Log incident, capture stack trace, notify maintainer |
| **Yelp `429` rate limit** | Any `429` from upstream | Switch to cache-only mode; surface `Retry-After`; notify team |
| **Cache hit ratio collapse** | Hit ratio < 30% over 10 min | Investigate cache eviction / TTL config |
| **Data quality regression** | Average `completeness_score` < 0.75 over a day | Open issue, freeze schema changes, investigate upstream |
| **Schema drift detected** | Unexpected field appears in response | Block deploy; fail CI; require schema bump |
| **ngrok tunnel down** | Public URL unreachable | Restart tunnel; rotate ngrok URL; update README |
| **License field missing** | Any response without `provenance.license` | Fail CI; block release |

### Planned tooling
- **UptimeRobot** or **BetterStack** — external liveness checks against the ngrok URL.
- **GitHub Actions** — run `pytest` + `jsonschema` checks on every push; nightly load smoke.
- **Locust** (or **k6**) — performance & burst tests.
- **Python `logging` + structured JSON logs** — for alarm triggers and audits.

---

## 📘 Continuous Testing & Maintenance

- **Pre-commit**: linting (`ruff`), schema validation of any sample fixtures.
- **On push (GitHub Actions)**:
  - Unit tests (`pytest`)
  - Schema contract test against every endpoint using `jsonschema`
  - Quick smoke load (10 RPS × 30 s) against a local Flask instance
- **Nightly**:
  - Re-validate cached records' `completeness_score`
  - Sampled HEAD-check of `yelp_url` values
  - Refresh top-N queries to keep cache warm
- **Weekly QA review**: triage failing tests, drift reports, and any quality alarms.
- **On release**:
  - Manual exploratory tests through the live ngrok URL.
  - Verify provenance + license fields with a checklist.

---

## 📘 Quality Metrics (SLOs)

| Metric | Target |
|---|---|
| Availability (`/health`) | 99.5% during demo window |
| API uptime (search + single record) | 99% |
| Functional test pass rate (CI) | 100% on main |
| Schema contract pass rate | 100% |
| p95 latency (warm cache) | < 250 ms |
| p95 latency (uncached) | < 1.5 s |
| `completeness_score` (avg, rolling 7d) | ≥ 0.85 |
| Security tests pass rate | 100% |

---

## 📘 Status Summary

| Area | Status |
|---|---|
| Functional tests | ✅ Implemented (pytest + manual smoke) |
| Schema validation | ✅ Implemented (`jsonschema`) |
| Performance tests | ⚠️ Locust scripts drafted; full load runs planned post-MVP |
| Security tests | ⚠️ Auth gating + key-leak scans implemented; rate-limit per IP planned |
| Alarms / monitoring | 🔜 UptimeRobot + structured logs to be wired in |
| CI/CD validation | ✅ GitHub Actions running on push |
| Data quality dashboard | 🔜 To be added (consume `quality_summary` over time) |

---

## 📘 Team Responsibilities

| Task | Owner |
|---|---|
| Backend functional & schema tests | Backend lead |
| Performance / load scripts | Performance lead |
| Security & auth tests | Security lead |
| Data quality monitoring | Data/analyst lead |
| Alarms & on-call rotation | Maintainer |
| Weekly QA review | Rotating |

---

## 📘 Future Additions

- **Contract testing** with Pact between frontend and SBP API.
- **Synthetic monitoring**: scripted “gold” queries every 5 minutes against the public ngrok URL.
- **Anomaly detection** on `completeness_score` and `cache hit ratio` time series.
- **Chaos drills**: simulate Yelp 429 storms, ngrok tunnel failure, and cache wipe.
- **Public status page** linked from the project README.
