# Information Story — LocalFind (SBP v1.0)

**Course:** IMT 542 A Sp 26 — Portable Information Structures  
**Final Project** | **Author:** Sneha Reddy  
**Repository:** https://github.com/Sneha-8/IMT-542/tree/main/final

---

## 1. Who is the user?

| Persona | Goal | Pain today |
|---------|------|------------|
| **Local resident (Alex)** | Find independent shops and services nearby (fashion, fitness, food, repair, etc.) | Yelp/Google favor chains and ads; no single filter for neighborhood + category + trust |
| **Small-business owner (Maya)** | See how her shop appears in discovery feeds | Listings differ across Yelp, Instagram, and chamber sites |
| **Civic / developer (Jordan)** | Build a neighborhood map, newsletter, or agent | No stable JSON API with provenance and quality metrics |

## 2. Problem statement

Small-business information exists but is **not portable**: it is locked in Yelp, Google Maps, HTML directories, and social posts. Residents who want to **support local commerce** cannot combine neighborhood, category, hours, and ratings in one machine-readable query.

**Information story:**

> *As a Seattle resident, I want a single, trustworthy feed of neighborhood small businesses (shops, salons, gyms, cafes, and more) so I can discover and support local businesses near me—without re-scraping five different websites.*

## 3. Transcendent / community goal

Spending at locally owned businesses strengthens neighborhoods (jobs, character, tax base). A **portable structure** makes that choice easier to automate (newsletters, maps, accessibility tools) and easier to **audit** (provenance, completeness scores).

## 4. Insight area (course taxonomy)

| Type | How LocalFind delivers |
|------|------------------------|
| **Primary — Visualize info to a human** | LocalFind web UI: search, category browse, neighborhood filter, detail modal with hours, ratings, directions |
| **Secondary — Analyze relationships** | Sidebar stats by category; JSON API for BI tools (`GET /stats`) |

## 5. Requirements (in scope)

| ID | Requirement |
|----|-------------|
| R1 | Return businesses as **SBP schema v1.0** JSON with `schema_version`, `provenance`, `query_summary` |
| R2 | **Search** by keyword, category, neighborhood, location (including lat/lon “near me”) |
| R3 | **Single-record** fetch by stable `id` with enriched hours on detail |
| R4 | Attach **quality_flags** and **completeness_score** on every list response |
| R5 | **data_classification**; strip restricted `contact` unless valid Bearer token |
| R6 | Expose via **HTTPS REST API** (Flask; ngrok for Canvas) |
| R7 | Store records in **NoSQL** (MongoDB/Mongita); cache live API results |
| R8 | Integrate **real upstream APIs** (Yelp Fusion + OpenStreetMap) with FAIR documentation |
| R9 | **LocalFind web prototype** for end-to-end discover → detail flow |

## 6. Out of scope

- Payments, reservations, user accounts, owner self-service editing
- National coverage (Seattle metro focus)
- Native mobile apps
- Scraping Google Maps or Instagram (documented as silos only)

## 7. Wireframes (implemented in LocalFind)

### 7.1 Search home

- Category chips: All nearby, Food, Fashion, Fitness, Shops, Services, Beauty, Pets, Books, Home  
- Search box + location + neighborhood dropdown + **Near me**  
- Result cards: name, rating, category, tags, photo (Yelp when available)

### 7.2 Business detail

- Address, type, description, rating, review count  
- Compact hours (today highlighted; grouped weekdays)  
- Actions: Directions, Yelp, website, OpenStreetMap  
- Provenance footer (SBP v1.0)

### 7.3 API consumer

```
GET /businesses/search?term=fashion&location=Capitol%20Hill,%20Seattle,%20WA&fast=true
GET /businesses/{id}?full=1
GET /schema
```

## 8. User stories

1. **As Alex**, I want to browse **fashion** businesses in **Capitol Hill** so I can shop local boutiques.  
2. **As Alex**, I want **near me** search so I can find businesses close to my current location.  
3. **As Alex**, I want **hours and directions** on a detail page so I can visit today.  
4. **As Jordan**, I want `provenance` and `quality_flags` so I can trust the feed in a civic dashboard.  
5. **As Jordan**, I want responses in &lt;1 second when cached so the UI feels usable.

## 9. Success criteria (rubric alignment)

- Clear information story; API fields match story scope  
- Requirements define in/out of scope; portable structure differs from Yelp/OSM on **information, structure, format, access**  
- System reachable: UI + API return correct data for live and curated sources  
- Quality and performance measured in [04_Quality_Performance_Security.md](04_Quality_Performance_Security.md)
