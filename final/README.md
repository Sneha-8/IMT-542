# Final Project — Neighborhood Small Business Platform (SBP)

**Course:** IMT 542 A Sp 26 — Portable Information Structures  
**Canvas:** [Final Project assignment](https://canvas.uw.edu/courses/1883881/assignments/11160571)  
**Author:** Sneha Reddy

## Summary

Portable JSON API + **LocalFind web app** that helps Seattle residents discover real local businesses using **live external APIs** (not a static demo-only dataset).

| API | Key required? | Role |
|-----|---------------|------|
| **OpenStreetMap** (Nominatim + Overpass) | No | Real business names, addresses, coordinates — always on |
| **Yelp Fusion** | Yes (`YELP_API_KEY`) | Ratings, photos, reviews, hours — enriches results |

Data is normalized to **SBP v1.0**, cached in MongoDB, and served through Flask. Builds on I4–I8, G8, G9.

## Final submission (rubric)

Start here: **[docs/00_FINAL_SUBMISSION_GUIDE.md](docs/00_FINAL_SUBMISSION_GUIDE.md)** — maps all 10 rubric items to evidence files.

## Deliverables

| Item | Location |
|------|----------|
| Submission guide + rubric map | [docs/00_FINAL_SUBMISSION_GUIDE.md](docs/00_FINAL_SUBMISSION_GUIDE.md) |
| Information story + wireframes | [docs/01_Information_Story.md](docs/01_Information_Story.md) |
| FAIR assessment | [docs/02_FAIR_Assessment.md](docs/02_FAIR_Assessment.md) |
| Structure design | [docs/03_Structure_Design.md](docs/03_Structure_Design.md) |
| Quality / performance / security | [docs/04_Quality_Performance_Security.md](docs/04_Quality_Performance_Security.md) |
| Rubric checklist | [docs/05_Rubric_Scorecard.md](docs/05_Rubric_Scorecard.md) |
| Ethics & limitations (G6) | [docs/06_Ethics_and_Limitations.md](docs/06_Ethics_and_Limitations.md) |
| Class discussion synthesis | [docs/class_discussion_notes.md](docs/class_discussion_notes.md) |
| JSON Schema | [sbp_schema_v1.json](sbp_schema_v1.json) |
| Working API | [app.py](app.py) |
| Presentation (PPTX) | [presentation/IMT542_Final_Project.pptx](presentation/IMT542_Final_Project.pptx) |
| Presentation (HTML, live demo links) | [presentation/index.html](presentation/index.html) — see [presentation/README.md](presentation/README.md) |

## Quick start

```bash
cd final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set YELP_API_KEY from https://www.yelp.com/developers/v3/manage_app

export USE_MONGITA=true
python seed_db.py
export SBP_API_TOKEN=dev-class-token
flask --app app run -p 5002
```

**LocalFind web app** (in another terminal):

```bash
cd final
python3 -m http.server 8777 --bind 127.0.0.1
# Open http://127.0.0.1:8777/web/platform.html
```

**Default search uses live APIs** (OpenStreetMap always; Yelp when keyed). Results are cached in MongoDB for fast repeat searches. The 6-record curated file is only used when `source=local` (for tests).

**One-command demo:**

```bash
cd final
POPULATE_LIVE=1 ./run_localfind.sh   # first run: fetch real OSM/Yelp data (~4 min)
# Then open http://127.0.0.1:8777/web/platform.html
```

Use **Refresh from APIs** in the UI (or `?refresh=true`) to bypass cache and pull fresh data.

## Adding more small business data

| Method | What it adds | How |
|--------|----------------|-----|
| **Bulk OSM cache** | Many real shops per neighborhood | `python scripts/populate_live_data.py` (edit `scripts/populate_queries.json`) |
| **Neighborhood-only sweep** | All named cafes/shops in an area (no keyword) | `python scripts/populate_live_data.py --neighborhoods-only` |
| **Live search in UI** | New results on demand | Search in LocalFind; check **Refresh from APIs** for a fresh pull |
| **Yelp** | Ratings, photos, hours | Set `YELP_API_KEY` in `.env`, then re-run populate or search with `refresh=true` |
| **Curated records** | Your own demo/owner rows with full hours & tags | Add objects to `small_businesses.json`, then `python scripts/import_curated.py` and `python seed_db.py` |

```bash
cd final
source .venv/bin/activate
export USE_MONGITA=true

# ~15–25 min: 20 keyword queries + 12 Seattle neighborhood sweeps
LIMIT=25 python scripts/populate_live_data.py

# Faster: only neighborhood bulk pulls
python scripts/populate_live_data.py --neighborhoods-only
```

After populate, normal searches use the **MongoDB cache** (fast). Use `?refresh=true` when you need newly opened businesses from OSM/Yelp.

Pre-load the database with real searches:

```bash
python scripts/populate_live_data.py
```

API query params:

- `GET /businesses/search?term=coffee&location=Seattle, WA&radius=5000`
- `source=auto|yelp|local` (default `auto` = Yelp if key is set)

In another terminal (Canvas submission):

```bash
ngrok http 5002
python access_api.py
```

Submit the **ngrok HTTPS URL** to Canvas.

## Tests

```bash
export USE_MONGITA=true
pytest -q
```

## Regenerate slides

```bash
python scripts/build_presentation.py
```

## Related repo folders

- `I7/` — first Flask + JSON API
- `I8/` — MongoDB + optional knowledge graph
- `G8/` — access methodology
- `G9/` — test plan
