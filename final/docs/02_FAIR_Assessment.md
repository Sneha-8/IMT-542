# FAIR Assessment — Existing Information vs. SBP Information Story

**Project:** Neighborhood Small Business Discovery Platform (SBP)  
**Author:** Sneha | **Course:** IMT 542

We assess **Findable, Accessible, Interoperable, Reusable** properties of information sources used *before* our portable structure, then contrast with the **new SBP v1.0** structure.

---

## Sources analyzed

| Source | Format | Typical access | Original use case |
|--------|--------|----------------|-------------------|
| **Yelp Fusion API** | Nested JSON | HTTPS + API key | Consumer search & ads |
| **Google Maps / Places** | JSON (limited export) | Web UI + partial API | Navigation |
| **Chamber / neighborhood HTML directories** | HTML tables | Browser | Static listings |
| **Owner social (Instagram)** | Unstructured posts | App / scrape | Marketing |
| **Our I7 `small_businesses.json`** | Flat JSON file | File read at startup | Class API prototype |

---

## FAIR matrix (existing sources)

### Yelp Fusion API

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Partial | IDs exist; no persistent DOI; search is query-dependent |
| **Accessible** | Partial | HTTPS + key; rate limits; display-only license blocks redistribution |
| **Interoperable** | Low | Custom nested schema; categories as Yelp aliases not Schema.org |
| **Reusable** | Low | Terms restrict storage/redistribution; provenance not in payload |

**Gaps for our story:** Cannot freely republish for civic tools; phone/address shapes vary; no `quality_flags` or `completeness_score`; contact mixed with public fields.

### HTML neighborhood directories

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Low | No stable IDs; SEO URLs only |
| **Accessible** | Partial | Public HTTP but human-oriented layout |
| **Interoperable** | Low | No schema; scraping breaks on redesign |
| **Reusable** | Low | Unclear license; no machine metadata |

### I7 static JSON (in-repo prototype)

| Principle | Rating | Evidence |
|-----------|--------|----------|
| **Findable** | Partial | GitHub path + `id` field |
| **Accessible** | Partial | File on disk; API only after manual deploy |
| **Interoperable** | Partial | Consistent keys but non-standard vocabulary |
| **Reusable** | Partial | No license block; no versioning or provenance |

---

## Transformations required (summary)

| From (existing) | To (SBP v1.0) | Why |
|-----------------|---------------|-----|
| Yelp nested `location.display_address[]` | `location.address_line_1`, `city`, `state`, `zip_code`, `coordinates` | Portable address parsing |
| Raw phone strings | `contact.phone_e164` | International interoperability |
| Implicit completeness | `quality_flags` + `query_summary.quality_summary` | Consumers filter without re-validation |
| Missing lineage | `provenance` block on every response | Reusability & license compliance |
| Monolithic contact object | `data_classification` + auth-gated fields | Security / privacy (FAIR Accessible) |
| In-memory list (I7) | NoSQL documents + indexes (I8/final) | Performance & flexible schema |
| Ad-hoc JSON | `schema_version: "1.0"` + published JSON Schema at `GET /schema` | Interoperability |

---

## FAIR assessment — **new** SBP structure

| Principle | How SBP addresses it |
|-----------|----------------------|
| **Findable** | Stable `id` per business; `schema_version`; GitHub repo URL in `provenance.repository` |
| **Accessible** | REST over HTTPS; `GET /health`; public vs restricted fields; standard HTTP errors |
| **Interoperable** | Schema.org-aligned categories; JSON Schema contract; E.164 phones |
| **Reusable** | `provenance.license`, `retrieved_at`, `source`; CC-BY-4.0 on curated demo dataset |

---

## Deficiencies remediated in final build

1. **No provenance** → every API response includes `provenance`  
2. **No quality metrics** → `quality_flags` per record + `completeness_score` in `query_summary`  
3. **No access control** → Bearer token unlocks full `contact` when `data_classification` is `restricted`  
4. **Poor query performance** → MongoDB indexes on `id`, `category`, `location.zip`, `tags`, `communityRating`  
5. **No contract testing** → `jsonschema` validation in CI (`tests/`)

---

## Data used in demo

The running system uses a **curated Seattle small-business dataset** (`small_businesses.json`, 6 records) normalized to SBP v1.0. Yelp is documented as the **production upstream** we would integrate when a team API key is available (see `G8/G8_AccessMethodology.md`). This satisfies the assignment’s “existing information” analysis while keeping the demo reproducible without secrets.
