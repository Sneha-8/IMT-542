# Information Story — Neighborhood Small Business Discovery Platform (SBP)

**Course:** IMT 542 A Sp 26 — Portable Information Structures  
**Final Project** | **Author:** Sneha

---

## 1. Who is the user?

| Persona | Goal | Pain today |
|---------|------|------------|
| **Local resident (Alex)** | Find independent shops, cafes, and services near home that match values (sustainable, women-owned, open now) | Yelp/Google mix chains with locals; filters are ad-driven and incomplete |
| **Small-business owner (Maya)** | Confirm how her shop appears in public discovery feeds | Data is scattered across Yelp, Instagram, and chamber-of-commerce PDFs with no single portable record |
| **Civic / developer (Jordan)** | Build a neighborhood dashboard or agent that recommends local businesses | No clean JSON API with provenance, quality flags, and stable schema |

## 2. Problem statement

Information about small businesses exists, but it is **not portable**: it is locked in proprietary apps (Yelp, Google Maps), unstructured social posts, and static HTML directories. Residents who want to **support local commerce** cannot easily combine “open now,” “tags,” “price range,” and “neighborhood” in one machine-readable query. Our **information story** is:

> *As a Seattle resident, I want a single, trustworthy JSON feed of neighborhood small businesses so I can discover and support local shops that match my needs—without re-scraping five different websites.*

## 3. Transcendent / community goal

Keeping spending in **locally owned businesses** strengthens neighborhoods (tax base, jobs, character). A portable structure makes that choice **easier to automate** (maps, chatbots, community newsletters) and **easier to audit** (provenance, completeness scores).

## 4. Insight area (course taxonomy)

**Primary:** Visualize info to a human (search UI + JSON for BI tools)  
**Secondary:** Analyze relationships (category stats, graph of tags/neighborhoods via I8 KG variant)

## 5. Requirements (in scope)

| ID | Requirement |
|----|-------------|
| R1 | Return businesses as **SBP schema v1.0** JSON with `schema_version`, `provenance`, `query_summary` |
| R2 | **Search** by keyword, category, neighborhood, ZIP, tags, price range |
| R3 | **Single-record** fetch by stable `id` |
| R4 | Attach **quality_flags** and **completeness_score** on every list response |
| R5 | Mark **data_classification**; strip restricted `contact` fields unless `Authorization: Bearer` token present |
| R6 | Expose via **HTTPS REST API** (Flask + ngrok for demo) |
| R7 | Store canonical records in **NoSQL** (MongoDB / Mongita) for indexed queries |
| R8 | Document **FAIR** assessment of upstream sources and remediation for gaps |

## 6. Out of scope

- Real-time Yelp Fusion integration in production (documented as upstream source; demo uses curated Seattle dataset)
- Payments, reservations, or user accounts
- Mobile native apps (API-only deliverable; wireframes show a future web client)

## 7. Wireframes (conceptual)

### 7.1 Home / search

```
+--------------------------------------------------+
|  Neighborhood Small Business Finder              |
|  [ Search: bakery, vegan, wifi...          ] [Go]|
|  Neighborhood [ Capitol Hill v ]  ZIP [ 98122 ]  |
+--------------------------------------------------+
|  3 results · completeness 92% · via SBP API v1.0 |
+--------------------------------------------------+
|  Brew & Bloom Coffee        * 4.7  cafe          |
|  412 Pine St · Open today 7am-6pm                |
|  tags: coffee, vegan-options, wifi               |
+--------------------------------------------------+
|  Green Leaf Bookstore       * 4.8  retail        |
|  ...                                             |
+--------------------------------------------------+
```

### 7.2 Business detail

```
+--------------------------------------------------+
|  <- Back          Brew & Bloom Coffee            |
|  Category: cafe · Capitol Hill · est. 2018       |
|  [ Call ] [ Website ] [ Instagram ]              |
+--------------------------------------------------+
|  Hours today: 7am-6pm (Mon)                      |
|  Products: House Drip $3.50 · Lavender Latte ... |
|  Owner: Maya Chen · Accepts online orders        |
+--------------------------------------------------+
|  Data: SBP v1.0 · source: curated_local_v1       |
|  Retrieved: 2026-05-23T... · license: CC-BY-4.0  |
+--------------------------------------------------+
```

### 7.3 API consumer (developer)

```
GET /businesses/search?term=coffee&location=Capitol%20Hill
-> 200 application/json (SBP envelope + businesses[])
```

## 8. User stories

1. **As Alex**, I want to filter by neighborhood and tag `wifi` so I can work from a local cafe.  
2. **As Alex**, I want `open-now` so I do not walk to a closed shop.  
3. **As Maya**, I want a stable `id` and public fields separated from owner contact so I control what is shared.  
4. **As Jordan**, I want `provenance` and `quality_flags` so I can trust the feed in a civic dashboard.

## 9. Success criteria (aligned with rubric)

- Information story is clear; no fields in API responses outside story scope  
- Requirements define scope; portable structure differs from Yelp/HTML on **structure, format, and access**  
- System is reachable and returns correct, complete data per story  
- Quality and performance are measured and documented with remediation plans
