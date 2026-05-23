# Portable Structure Design — From Existing to SBP v1.0

## 1. What changed (rubric: ≥2 of information, structure, format, access)

| Dimension | Before (Yelp / HTML / I7 JSON) | After (SBP v1.0) |
|-----------|-------------------------------|------------------|
| **Information** | Mixed public + vendor fields; no quality booleans | Explicit `quality_flags`, `completeness_score` |
| **Structure** | Nested vendor-specific trees | Flattened `LocalBusiness`-aligned record + envelope |
| **Format** | HTML tables or Yelp JSON | Versioned JSON (`schema_version`) + JSON Schema |
| **Access** | Browser or proprietary SDK | REST `GET /businesses/search`, `GET /businesses/{id}`, `GET /schema` |

## 2. Envelope shape (every list response)

```json
{
  "schema_version": "1.0",
  "data_classification": "public",
  "provenance": { "...": "..." },
  "query_summary": {
    "records_in_this_batch": 3,
    "quality_summary": {
      "completeness_score": 0.92,
      "last_validated": "2026-05-23T12:00:00Z"
    }
  },
  "businesses": [ /* SBP records */ ]
}
```

## 3. Business record (core fields)

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Stable SBP id (e.g. `sb-001`) |
| `name` | string | Display name |
| `categories` | string[] | Normalized slugs (`cafe`, `retail`, …) |
| `rating` | number | Maps from `communityRating` |
| `review_count` | integer | Optional; null in demo |
| `price_tier` | int 1–4 | Derived from product prices when present |
| `location` | object | Split address + optional coordinates |
| `contact` | object | `phone_e164`, email, website; classification |
| `tags` | string[] | Portable facet for search |
| `hours` | object | Day → hours string |
| `products` | array | `{name, price}` |
| `quality_flags` | object | Completeness booleans |
| `transactions` | string[] | e.g. `pickup` if `acceptsOnlineOrders` |

## 4. Transformation pipeline

```
small_businesses.json  -->  seed_db.py  -->  MongoDB collection
                                |
                                v
                         normalizer.to_sbp_record()
                                |
                                v
                         Flask app (search / by id)
                                |
                                v
                    apply_auth_policy()  -->  HTTP JSON response
```

Implementation: `final/normalizer.py`, `final/app.py`.

## 5. New query capabilities (portability outcomes)

- **Tag array queries** — `GET /businesses/tag/{tag}`  
- **Aggregation** — `GET /stats` (count + avg rating by category)  
- **Temporal** — `GET /open-now` from `hours`  
- **Graph** (optional I8) — related businesses via shared tags/neighborhood  

## 6. Requirements traceability

| Req | Implementation |
|-----|----------------|
| R1 envelope | `app.search()` / `app.get_one()` |
| R2 search | `/businesses/search` query params |
| R3 by id | `/businesses/<id>` |
| R4 quality | `normalizer.quality_flags()` |
| R5 auth | `apply_auth_policy()` + env `SBP_API_TOKEN` |
| R6 REST | Flask on port 5002 |
| R7 NoSQL | `seed_db.py` + pymongo/Mongita |
| R8 FAIR doc | this file + `02_FAIR_Assessment.md` |
