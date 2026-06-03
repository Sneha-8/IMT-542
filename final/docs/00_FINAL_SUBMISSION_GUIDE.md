# IMT 542 Final Project — Submission Guide

**Student:** Sneha Reddy  
**Course:** IMT 542 A Sp 26 — Portable Information Structures  
**Due:** Friday, June 5, 2026, 11:59 PM  
**GitHub:** https://github.com/Sneha-8/IMT-542/tree/main/final  
**Project name:** LocalFind — Neighborhood Small Business Platform (SBP v1.0)

---

## What you are submitting

| Canvas requirement | Where it lives |
|--------------------|----------------|
| GitHub repo with README | [../README.md](../README.md) and [../../README.md](../../README.md) |
| Code to download, convert, expose data | `normalizer.py`, `yelp_client.py`, `osm_client.py`, `live_search.py`, `app.py`, `scripts/` |
| Working website / API | [web/platform.html](../web/platform.html) + Flask API (`app.py`) |
| PPTX for in-class presentation | [presentation/IMT542_Final_Project.pptx](../presentation/IMT542_Final_Project.pptx) |
| HTML slides (optional backup) | [presentation/index.html](../presentation/index.html) |
| Rubric documentation (10 items) | Files below — one doc per grading theme |

**Canvas URL field:** Public **HTTPS** link to your API (e.g. ngrok) **or** deployed host. Example setup in [../README.md](../README.md#canvas-submission).

---

## Rubric map (50 points = 10 items × 5 pts)

| # | Rubric criterion | Points | Primary evidence |
|---|------------------|--------|------------------|
| 1 | Information story documented (purpose, user, goal) | 5 | [01_Information_Story.md](01_Information_Story.md) §1–4 |
| 2 | Information story (requirements in/out of scope; portability) | 5 | [01_Information_Story.md](01_Information_Story.md) §5–6, §9 |
| 3 | Assessment of existing structures (sources, access, quality) | 5 | [02_FAIR_Assessment.md](02_FAIR_Assessment.md) §1–2 |
| 4 | Assessment of existing structures (transformations defined) | 5 | [02_FAIR_Assessment.md](02_FAIR_Assessment.md) §3–4, [03_Structure_Design.md](03_Structure_Design.md) |
| 5 | Portable structure 1 (≥2 of: info, structure, format, access) | 5 | [03_Structure_Design.md](03_Structure_Design.md) §1–3, [sbp_schema_v1.json](../sbp_schema_v1.json) |
| 6 | Portable structure 2 (meets requirements only) | 5 | `normalizer.py`, `app.py`, `tests/` |
| 7 | Functional system 1 (accessible as documented) | 5 | [../README.md](../README.md), `flask --app app run`, ngrok |
| 8 | Functional system 2 (correct & complete per story) | 5 | [web/platform.html](../web/platform.html), `pytest` (12 tests) |
| 9 | Quality documented (desired vs actual) | 5 | [04_Quality_Performance_Security.md](04_Quality_Performance_Security.md) §1–2 |
| 10 | Performance documented (desired vs actual + remediation) | 5 | [04_Quality_Performance_Security.md](04_Quality_Performance_Security.md) §3–5 |

**Checklist with Done marks:** [05_Rubric_Scorecard.md](05_Rubric_Scorecard.md)

---

## Five grading areas (assignment narrative)

### 1. Ideate — information story, requirements, wireframes

- **Doc:** [01_Information_Story.md](01_Information_Story.md)
- **Product:** LocalFind web UI + SBP REST API
- **Insight area:** Visualize information to humans (primary); analyze category/neighborhood patterns (secondary)

### 2. Define — FAIR assessment of existing information

- **Doc:** [02_FAIR_Assessment.md](02_FAIR_Assessment.md)
- **Sources:** Yelp Fusion, Google Maps, HTML directories, social, I7 JSON; **live integration:** Yelp + OpenStreetMap

### 3. Analyze — deficiencies and portable structure design

- **Docs:** [02_FAIR_Assessment.md](02_FAIR_Assessment.md), [03_Structure_Design.md](03_Structure_Design.md)
- **Artifact:** SBP v1.0 envelope + business record + JSON Schema

### 4. Improve — working system with new structure

- **API:** `GET /businesses/search`, `GET /businesses/{id}`, `GET /schema`, `GET /health`, `GET /config`
- **UI:** Search, category browse, neighborhood filter, business detail with hours and directions
- **Data:** 500+ cached live businesses (Yelp + OSM); 6 curated records for tests

### 5. Control — quality, performance, security

- **Doc:** [04_Quality_Performance_Security.md](04_Quality_Performance_Security.md)
- **Ethics:** [06_Ethics_and_Limitations.md](06_Ethics_and_Limitations.md)
- **Tests:** `tests/` (12 passing)

---

## Presentation tomorrow

1. Open [presentation/index.html](../presentation/index.html) (Reveal.js) **or** PPTX in PowerPoint.
2. Before class: `USE_MONGITA=true flask --app app run -p 5002` and `python3 -m http.server 8777` in `final/`.
3. Demo: http://127.0.0.1:8777/web/platform.html — search Fashion, Fitness, Capitol Hill.
4. Optional ngrok: `ngrok http 5002` → add `?api=https://YOUR_URL` to presentation links.

Regenerate PPTX after doc edits:

```bash
cd final && python scripts/build_presentation.py
```

---

## MSIM focus claimed

**Information architecture** — novel portable envelope (SBP v1.0) with provenance, quality flags, and multi-source normalizer designed for civic reuse, not another Yelp wrapper.

Supporting threads: UX (LocalFind), data science (category stats), cybersecurity (auth-gated contact), BI (JSON export for dashboards).
