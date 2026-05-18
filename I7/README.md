# I7 API Access — Local Small Business Discovery API

**Course:** IMT 542 A Sp 26 — Portable Information Structures
**Assignment:** I7 — Create a simple API endpoint to host an information structure
**Author:** Sneha

## Project Idea

A platform to help people discover and support small businesses in their neighborhood. Users can search by ZIP code, neighborhood, or category to find local shops, cafes, and services near them and buy from them directly.

## Files

| File | Description |
|------|-------------|
| app.py | Flask REST API server |
| small_businesses.json | Sample data — 3 local businesses |
| access_api.py | Python client using requests |

## Setup

```bash
pip install flask requests
```

Place all files in the same folder, then run:

```bash
flask --app app run -p 5002
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + endpoint list |
| GET | `/businesses` | All businesses (summary) |
| GET | `/businesses/<id>` | One business by ID |
| GET | `/businesses/category/<cat>` | Filter by category (e.g. cafe, retail) |
| GET | `/businesses/zip/<zip>` | Filter by ZIP code |
| GET | `/businesses/neighborhood/<name>` | Filter by neighborhood |
| GET | `/search?q=<keyword>` | Search across all fields |
| GET | `/categories` | List all categories |

## Expose with ngrok

```bash
ngrok http http://localhost:5002
```

Update BASE_URL in access_api.py with your ngrok HTTPS URL, then:

```bash
python access_api.py
```

## Video Demo

[Add your video link here after recording]

## Video Demo Checklist
- [ ] Terminal running Flask
- [ ] Terminal running ngrok
- [ ] access_api.py running and showing API responses
- [ ] Response data printed to screen
