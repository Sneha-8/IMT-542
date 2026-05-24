# I8 — Advanced DBs: NoSQL behind the Local Small Business Discovery API

**Course:** IMT 542 A Sp 26 — Portable Information Structures  
**Assignment:** I8 — Add a NoSQL or Knowledge Graph to store information behind an API  
**Author:** Sneha

## Video Demo

[Add Google Drive / YouTube link here after recording]

## What changed since I7

In I7, the Flask app loaded `small_businesses.json` into memory at startup and filtered Python lists. I8 moves that data into a **NoSQL document store (MongoDB)** and rewrites every endpoint to query the database directly. I also added new query endpoints that take advantage of NoSQL features — indexes, aggregation pipelines, regex search, and flexible-schema writes.

A `kg_app.py` is included as an optional **Knowledge Graph** variant built with NetworkX, exposing graph-traversal endpoints (related businesses, shortest path, etc.). The assignment allows either NoSQL or a Knowledge Graph — this submission demonstrates both, with the NoSQL version (`app.py`) as the primary deliverable.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask API backed by MongoDB (primary I8 deliverable) |
| `seed_db.py` | One-time loader: JSON → MongoDB |
| `small_businesses.json` | Source dataset (6 businesses, pretty-printed) |
| `access_api.py` | Python client that hits the API via ngrok |
| `kg_app.py` | Optional Knowledge Graph variant (NetworkX) |
| `requirements.txt` | Dependencies |
| `run.sh` | Convenience helper: seeds + starts the Flask server |

## Setup

```bash
pip install -r requirements.txt
```

Then pick a database mode:

**Option A — Real MongoDB (recommended)**

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Option B — No install required**

Open `seed_db.py` and `app.py` and change `USE_MONGITA = False` to `USE_MONGITA = True`. This uses Mongita, a file-based MongoDB-compatible store.

## Run

One-liner (uses the helper script):

```bash
bash run.sh
```

Or run the steps manually:

```bash
python seed_db.py              # loads small_businesses.json into the NoSQL DB
flask --app app run -p 5002    # start the Flask API
ngrok http 5002                # expose it publicly (separate terminal)
python access_api.py           # demo all endpoints (separate terminal)
```

## API Endpoints

### Carried from I7 (now NoSQL-backed)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + endpoint catalog |
| GET | `/businesses` | List all businesses (summary) |
| GET | `/businesses/<id>` | Get one business by ID |
| GET | `/businesses/category/<cat>` | Filter by category |
| GET | `/businesses/zip/<zip>` | Filter by ZIP code |
| GET | `/businesses/neighborhood/<name>` | Filter by neighborhood |
| GET | `/search?q=<keyword>` | Search across name / description / tags / category / owner |
| GET | `/categories` | List all categories |

### New in I8

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/businesses/tag/<tag>` | Filter by tag (NoSQL array query) |
| GET | `/businesses/price?min=&max=` | Filter by product price range (aggregation pipeline) |
| GET | `/top-rated?limit=N` | Top-rated businesses (sorted query + index) |
| GET | `/open-now` | Businesses open today (computed from `hours`) |
| GET | `/stats` | Aggregate stats per category (count + avg rating) |
| POST | `/businesses` | Insert a new business document (flexible-schema write) |

## Why NoSQL fits this dataset

Each business document has nested objects (`location`, `contact`, `hours`), variable-length arrays (`products`, `tags`), and may grow new attributes over time (delivery options, accessibility info, payment methods, etc.). A document model stores each business as a single self-contained JSON document — no joins, no rigid schema — which mirrors the way the information is actually consumed by the frontend.

## Knowledge Graph variant (`kg_app.py`)

Models the same data as a graph:

- **Nodes:** Business, Category, Neighborhood, Tag, Owner
- **Edges:** `BELONGS_TO`, `LOCATED_IN`, `TAGGED_AS`, `OWNED_BY`

Run with `flask --app kg_app run -p 5003`. Useful endpoints:

- `GET /graph/summary` — node-type counts
- `GET /graph/related/<biz_id>` — businesses sharing tags / neighborhood / category
- `GET /graph/path?source=&target=` — shortest path between any two nodes

## Demo script for the video

1. Show `seed_db.py` output: "Seeded 6 businesses into NoSQL store."
2. Start Flask: `flask --app app run -p 5002`
3. Start ngrok: `ngrok http 5002`
4. Run `python access_api.py` — narrate each endpoint response.
5. Call out the new endpoints (`/top-rated`, `/stats`, `/open-now`, `/businesses/tag/...`) and explain they are powered by MongoDB queries / aggregation, not in-memory Python filtering.
6. Finish with the `POST /businesses` insert to show NoSQL writes — the document count goes up and the new record appears in `/businesses`.
