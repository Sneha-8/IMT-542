# Quality, Performance, and Security — Final System

**Project:** LocalFind (SBP v1.0) | **Author:** Sneha Reddy  
Builds on **G9 Test Plan** with measured results from the `final/` build (June 2026).

---

## 1. Desired quality (from requirements)

| Metric | Target | Measurement method |
|--------|--------|-------------------|
| Schema contract | 100% responses validate | `pytest` + `jsonschema` |
| `completeness_score` | Document per source | `query_summary.quality_summary` |
| Valid E.164 when phone present | ≥ 95% | Regex on `contact.phone_e164` |
| Provenance present | 100% | Field presence on all endpoints |
| Live data correctness | Names/addresses match upstream | Manual spot-check + Yelp/OSM links |
| Functional tests | All pass | `pytest -q` (12 tests) |

---

## 2. Observed quality

### Curated dataset (n=6, `source=local`)

| Metric | Result |
|--------|--------|
| Schema validation | **Pass** |
| Average `completeness_score` | **~0.92** |
| E.164 valid (phones present) | **100%** |
| `provenance.license` | **CC-BY-4.0** |

### Live cache (n≈500, Yelp + OSM)

| Metric | Result | Notes |
|--------|--------|-------|
| Records with `name` + address | **>95%** | OSM gaps on hours |
| Records with Yelp `rating` | **~70%** of Yelp-sourced rows | OSM-only rows lack rating |
| `provenance` on live search | **100%** | Source + license in envelope |
| Category coverage | Food, fashion, fitness, retail, services, beauty, pets, books, home | Via `populate_queries.json` |

**Gaps:** OSM `opening_hours` inconsistent; some businesses lack photos.  
**Remediation:** Yelp enrichment on detail (`?full=1`); merge by business name in `live_search.py`.

---

## 3. Desired vs actual performance

| Scenario | Target | Measured (local) |
|----------|--------|-------------------|
| `GET /health` | < 50 ms | **~15 ms** |
| `GET /businesses/search` (cached, `fast=true`) | < 500 ms | **~20–100 ms** |
| `GET /businesses/search` (live `refresh=true`) | < 45 s | **~15–40 s** (Yelp+OSM parallel) |
| `GET /businesses/{id}` (cached) | < 300 ms | **~50–200 ms** |
| `GET /businesses/{id}?full=1` | < 5 s | **~1–3 s** (Yelp detail) |

Measurements: `curl -w '%{time_total}\n'`, Flask debug off, `USE_MONGITA=true`, 500+ cached records.

### Performance design choices

| Choice | Benefit | Tradeoff |
|--------|---------|----------|
| MongoDB/Mongita cache | Sub-second repeat searches | Stale until `refresh=true` |
| `fast=true` default in UI | Good UX | May miss brand-new listings |
| Parallel Yelp + OSM | Shorter live fetch | Still network-bound |
| Single Overpass call (fast OSM) | Faster than triple Nominatim+Overpass | Fewer OSM hits per query |
| In-memory response cache (TTL 5 min) | Repeated identical API calls fast | Memory only |

**Remediation (production):** Redis cache; CDN for static UI; background `populate_live_data.py` cron.

---

## 4. Security controls

| Control | Status | Implementation |
|---------|--------|----------------|
| Public vs restricted contact | **Implemented** | `apply_auth_policy()` strips phone/email without Bearer |
| Invalid token on protected use | **401** | `token_ok()` in `app.py` |
| API keys not in repo/responses | **Pass** | `YELP_API_KEY` in `.env` only (gitignored) |
| TLS for public demo | **Via ngrok** | HTTPS tunnel to Flask |
| Upstream license compliance | **Documented** | Yelp display-only; OSM ODbL attribution in `provenance` |
| Rate limiting | **Planned** | G9 S3; not enabled in class demo |

**Demo token:** `export SBP_API_TOKEN=dev-class-token`

---

## 5. Remediation roadmap

| Priority | Item | Status |
|----------|------|--------|
| P1 | Yelp Fusion adapter | **Done** — `yelp_client.py` |
| P2 | OpenStreetMap adapter | **Done** — `osm_client.py` |
| P3 | Bulk cache populate | **Done** — `scripts/populate_live_data.py` |
| P4 | Automated tests | **Done** — 12 tests passing |
| P5 | GitHub Actions CI | Recommended |
| P6 | Locust load test | Before production scale |

---

## 6. Test execution

```bash
cd final
source .venv/bin/activate
export USE_MONGITA=true
pytest -q
```

Expected: **12 passed** — covers health, search, schema, auth, local source, live/OSM mock, Yelp when configured.
