# FAIR Assessment — Existing Information vs. SBP Information Story

**Project:** LocalFind / Neighborhood Small Business Platform (SBP)  
**Author:** Sneha Reddy | **Course:** IMT 542 A Sp 26

We assess **Findable, Accessible, Interoperable, Reusable** properties of information sources used *before* our portable structure, then contrast with the **new SBP v1.0** structure and **live integrations** in the final build.

---

## Sources analyzed

| Source | Format | Typical access | Original use case |
|--------|--------|----------------|-------------------|
| **Yelp Fusion API** | Nested JSON | HTTPS + API key | Consumer search, ratings, ads |
| **OpenStreetMap** (Nominatim + Overpass) | GeoJSON / tags | HTTPS, no key (usage policy) | Community map data |
| **Google Maps / Places** | JSON (limited export) | Web UI + partial API | Navigation |
| **Chamber / neighborhood HTML directories** | HTML tables | Browser | Static listings |
| **Owner social (Instagram)** | Unstructured posts | App | Marketing |
| **I7 `small_businesses.json`** | Flat JSON | File at startup | Class API prototype |

---

## FAIR matrix (existing sources)

### Yelp Fusion API

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Partial | Business IDs exist; search is query-dependent; no DOI |
| **Accessible** | Partial | HTTPS + API key; rate limits; terms limit redistribution |
| **Interoperable** | Low | Nested schema; Yelp category aliases; no quality metadata |
| **Reusable** | Low | Display-only license; no provenance in payload |

**Gaps for our story:** Cannot ethically republish raw Yelp dumps for civic tools; must normalize, attribute, and cache under license terms.

### OpenStreetMap

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Partial | OSM node/way IDs; geographic indexing |
| **Accessible** | Partial | Free API; usage policy (throttle, attribution) |
| **Interoperable** | Partial | Tag-based schema; uneven hours/contact coverage |
| **Reusable** | **High** | ODbL 1.0 with attribution — strong for civic reuse |

**Role in LocalFind:** Baseline real business names, addresses, coordinates without API key cost.

### HTML neighborhood directories

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Low | No stable IDs |
| **Accessible** | Partial | Public HTTP, human layout |
| **Interoperable** | Low | No schema; scraping fragile |
| **Reusable** | Low | Unclear license |

### I7 static JSON (class prototype)

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Partial | GitHub path + `id` |
| **Accessible** | Partial | File on disk until API deployed |
| **Interoperable** | Partial | Consistent keys, non-standard vocabulary |
| **Reusable** | Partial | No version or provenance block |

---

## Transformations required (summary)

| From (existing) | To (SBP v1.0) | Why |
|-----------------|---------------|-----|
| Yelp `location.display_address[]` | `location.address_line_1`, `city`, `state`, `zip_code`, `coordinates` | Portable address |
| OSM tags (`opening_hours`, `shop`) | SBP `hours`, `categories` | Machine-readable listing |
| Raw phone strings | `contact.phone_e164` | Interoperability |
| Implicit completeness | `quality_flags` + `query_summary.quality_summary` | Trust without re-validation |
| Missing lineage | `provenance` on every response | Reuse + license compliance |
| Mixed contact fields | `data_classification` + Bearer auth | Privacy (FAIR Accessible) |
| I7 in-memory list | NoSQL + `live_businesses` cache | Performance at scale |
| Vendor-specific JSON | `schema_version: "1.0"` + `GET /schema` | Contract for partners |

---

## FAIR assessment — **new** SBP structure

| Principle | How SBP addresses it |
|-----------|----------------------|
| **Findable** | Stable `id` (`yelp-id`, `osm-node-*`, `sb-*`); `schema_version`; repo URL in `provenance.repository` |
| **Accessible** | REST over HTTPS; `/health`, `/config`; public vs restricted fields; HTTP error codes |
| **Interoperable** | JSON Schema; E.164 phones; normalized category slugs; envelope pattern |
| **Reusable** | `provenance.source`, `retrieved_at`, `license` (OSM ODbL + Yelp terms); documented transforms in `normalizer.py` |

---

## Deficiencies remediated in final build

1. **No provenance** → every API response includes `provenance` and `query_summary`  
2. **No quality metrics** → `quality_flags` per record + `completeness_score`  
3. **No access control** → Bearer `SBP_API_TOKEN` unlocks restricted `contact`  
4. **Slow repeat queries** → MongoDB/Mongita cache (`live_businesses`); `fast=true` serves cache in &lt;100 ms  
5. **Single-source bias** → Yelp + OSM merged in `live_search.py` with name-based enrichment  
6. **No contract testing** → 12 `pytest` tests + `jsonschema` validation  

---

## Data used in the running system

| Layer | Description | FAIR note |
|-------|-------------|-----------|
| **Live cache** | 500+ businesses from Yelp Fusion + OpenStreetMap across 60+ category queries and 15 neighborhood sweeps | Provenance per request; Yelp terms respected |
| **Curated demo** | 6 Seattle businesses in `small_businesses.json` | CC-BY-4.0; used for `source=local` tests |
| **Categories** | Food, fashion, fitness, retail, services, beauty, pets, books, home, and more | Demonstrates portability beyond restaurants |

Implementation: `yelp_client.py`, `osm_client.py`, `live_search.py`, `scripts/populate_live_data.py`.
