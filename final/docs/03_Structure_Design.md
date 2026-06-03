# Portable Structure Design — From Existing to SBP v1.0

**Project:** LocalFind | **Author:** Sneha Reddy

## 1. What changed (rubric: ≥2 of information, structure, format, access)

| Dimension | Before (Yelp / OSM / HTML / I7) | After (SBP v1.0) |
|-----------|--------------------------------|------------------|
| **Information** | Mixed vendor fields; no quality booleans | `quality_flags`, `completeness_score`, `data_classification` |
| **Structure** | Nested vendor trees; OSM tags | Flattened business record + response **envelope** |
| **Format** | HTML or vendor JSON | Versioned JSON + published JSON Schema |
| **Access** | Browser / SDK only | REST + LocalFind web UI |

## 2. Envelope shape (every list response)

```json
{
  "schema_version": "1.0",
  "data_classification": "public",
  "provenance": {
    "source": "Live merged feed",
    "endpoint": "GET /businesses/search",
    "retrieved_at": "2026-06-03T12:00:00Z",
    "license": "ODbL 1.0 (OSM); Yelp Fusion Terms",
    "repository": "https://github.com/Sneha-8/IMT-542/tree/main/final"
  },
  "query_summary": {
    "records_in_this_batch": 15,
    "data_source": "cached_live",
    "sources_used": ["mongodb_cache"],
    "quality_summary": {
      "completeness_score": 0.72,
      "records_complete": 8
    }
  },
  "businesses": []
}
```

## 3. Business record (core fields)

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | `yelp-*`, `osm-node-*`, or `sb-*` |
| `name` | string | Display name |
| `categories` | string[] | Normalized slugs |
| `rating`, `review_count` | number | From Yelp when available |
| `price_tier`, `price_symbol` | | Yelp price |
| `location` | object | Address + `coordinates` |
| `contact` | object | `phone_e164`, `website`; auth-gated |
| `hours` | object | Day keys or OSM `note` |
| `tags` | string[] | Search facets |
| `yelp_url`, `osm_url`, `image_url` | | Source links |
| `quality_flags` | object | Completeness booleans |
| `distance_from_query` | object | Meters from search center |

Full contract: [sbp_schema_v1.json](../sbp_schema_v1.json) — `GET /schema`

## 4. Transformation pipeline

```
┌─────────────────┐     ┌─────────────────┐
│ Yelp Fusion API │     │ OpenStreetMap   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         v                       v
    yelp_to_sbp()            osm_to_sbp()
         │                       │
         └───────────┬───────────┘
                     v
              live_search.py (merge, dedupe, enrich)
                     v
              persist_records → live_businesses (MongoDB)
                     v
              Flask app.py → apply_auth_policy()
                     v
         LocalFind UI  /  API consumers
```

**Curated path:** `small_businesses.json` → `seed_db.py` → `businesses` collection → `to_sbp_record()`

Implementation: `normalizer.py`, `live_search.py`, `app.py`, `web/platform.html`

## 5. New query capabilities

| Capability | Endpoint / UI |
|------------|----------------|
| Keyword + location search | `GET /businesses/search` |
| Fast cache | `?fast=true` (default in UI) |
| Force live refresh | `?refresh=true` |
| Near me | `?lat=&lon=` (reverse geocode) |
| By id + full hours | `GET /businesses/{id}?full=1` |
| Category stats | `GET /stats` |
| Schema contract | `GET /schema` |

## 6. Requirements traceability

| Req | Implementation |
|-----|----------------|
| R1 | `build_envelope()` in `normalizer.py` |
| R2 | `/businesses/search`, category chips in UI |
| R3 | `/businesses/<id>`, detail modal |
| R4 | `quality_flags()`, `completeness_score()` |
| R5 | `apply_auth_policy()` |
| R6 | Flask port 5002 + ngrok |
| R7 | Mongita/MongoDB `live_businesses` |
| R8 | `02_FAIR_Assessment.md` |
| R9 | `web/platform.html` |
