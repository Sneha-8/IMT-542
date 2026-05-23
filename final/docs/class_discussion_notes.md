# Class Discussion Notes — Summary for Final Project

Compiled from Canvas discussion threads (Weeks 1–8, Spring 2026). Full threads are in Canvas; this file highlights concepts that apply to the **Neighborhood Small Business Platform (SBP)** final project.

---

## Course definition (class consensus, Week 3)

> A **portable information structure** is a standardized format that enables user access and control and transfer across different systems by emphasizing **FAIR** (findable, accessible, interoperable, reusable) while addressing **privacy and security** so that human and machine readability is possible.

---

## Final project process (Six Sigma style)

| Phase | Class emphasis | SBP mapping |
|-------|----------------|-------------|
| **Ideate** | Info story, user (not data-first), wireframes | `01_Information_Story.md` |
| **Define** | FAIR on existing sources, requirements | `02_FAIR_Assessment.md` |
| **Analyze** | Gaps, transformations needed | `03_Structure_Design.md` |
| **Improve** | New structure + working API | `final/app.py`, schema v1.0 |
| **Control** | Quality, performance, security, tests | `04_Quality_Performance_Security.md`, `G9`, pytest |

**Insight areas:** visualize, analyze, predict, or automate — SBP primary = **visualize + analyze** (search, stats, open-now).

---

## Information story (critical themes)

- Like a user story, but traces the **information journey** (what systems, what data, what outcome).
- **Business question drives structure** — without focus, BI-style “views” have no aim (Week 3, Lincoln).
- Design for what the **user is trying to do**, not only what fields exist in the source (Week 4, G4).
- **Start narrow** — one specific use case, then zoom out (I3 discussion).
- G4 components: info story vs existing systems, wireframes, main concepts, system architecture.

---

## FAIR (Week 5–6)

| Principle | Apply to SBP |
|-----------|----------------|
| **Findable** | Stable `id`, `schema_version`, GitHub repo URI in `provenance.repository` |
| **Accessible** | HTTPS REST, `GET /health`, standard HTTP errors; Bearer for restricted contact |
| **Interoperable** | JSON Schema at `GET /schema`; Schema.org-aligned categories; E.164 phones |
| **Reusable** | `provenance.license`, `retrieved_at`, transformation documented in FAIR doc |

**Chapter 3 theme:** Portability without interoperability/usability is limited — export must be importable and meaningful on the receiving side.

**Agentic AI (Week 5):** Consumers may be machines/agents, not only humans — compact JSON + explicit metadata helps M2M use; document fields clearly for agents.

---

## Ethics & societal impact (G6 / Week 6)

- Evaluate portability choices against **virtue, consequentialist, and deontological** frames where relevant.
- For people-related data: balance public benefit vs privacy (classification, field-level auth).
- SBP: public listings vs **restricted** owner contact; Yelp display-only license if used upstream.
- Document **limitations** in final docs (demo dataset size, curated vs live Yelp).

---

## Backend & hosting (Week 8)

- Pipeline: raw files → processing → **database** (mixed records, query, backup) → API → consumers.
- NoSQL fits document-shaped business records; **knowledge graph** fits relationships (tags, neighborhoods) — see `I8/kg_app.py`.
- Largest “cost” in production is often managed DB storage; for class demo, Mongita/MongoDB is sufficient.

---

## Testing (Week 8, G9)

| Type | SBP coverage |
|------|----------------|
| Unit | `tests/test_normalizer.py` |
| Functional / schema | `tests/test_api.py` + jsonschema |
| Performance | Documented in `04_Quality_Performance_Security.md` |
| Security | Bearer gating tests; no key leakage |

---

## Presentation (Week 8, May 18)

- ~**10 min** present + **5 min** Q&A; wrap at ~15 min.
- Presentation is **low-stakes** (peer feedback); **rubric doc + GitHub** carry the grade.
- Demo is OK instead of polished slides.
- Use rubric as outline; implement peer feedback before deadline (Friday same week).
- Convert prior assignments to **markdown in repo** where helpful (this `final/` folder does that).

---

## Instructor reminders

- **Extensions:** ask before deadline with a new date — no explanation required.
- **AI:** avoid “cognitive surrender” — engage with design choices; quality shows in details.
- **JSON vs CSV:** multiple valid structures; stakeholder familiarity matters (Week 1 JSON/CSV story).
- **GitHub:** public repo, folders per assignment, README for graders.

---

## Session index (source threads)

| Week | Topic | Author (notes) |
|------|--------|----------------|
| 1.1 | Syllabus, final overview, AI policy | Zach Greenman |
| 1.2 | Info structures, JSON, legal/structured data | Samuel A Lee |
| 2.1 | Access, ethics, information stories, G2 | Lilly Bayly |
| 3.1 | PIS definition, knowledge graphs, G3 | Lilly Bayly |
| 3.2 | BI, prediction, I3, machine:machine | Lincoln Brennan |
| 4.1 | User stories, G4, NPD process | Michael Gov |
| 4.2 | File formats, I4 lab | Lavender Chang |
| 5.1 | FAIR quiz & group teach | Steven Gustafson |
| — | FAIR + Cooperative Principle | Zach Greenman (Grice) |
| 6.1 | Ethics, G6 | Emily Song |
| 6.2 | Portability vs interoperability, Ch. 3 | Jieyi Deng |
| 7.1 | Data quality | Pete Namchaisiri |
| 8.1 | Hosting, G8, final presentation Q&A | Em Stelter |
| 8.2 | DBMS vs filesystem, testing, rubric scorecard | Feiyang Gao |
