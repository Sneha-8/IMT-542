# Final Project — Neighborhood Small Business Platform (SBP)

**Course:** IMT 542 A Sp 26 — Portable Information Structures  
**Canvas:** [Final Project assignment](https://canvas.uw.edu/courses/1883881/assignments/11160571)  
**Author:** Sneha

## Summary

Portable JSON API that helps Seattle residents **discover and support local small businesses**. Builds on I4 (access), I7 (REST API), I8 (NoSQL), G8 (access methodology), and G9 (test plan).

## Deliverables

| Item | Location |
|------|----------|
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

# No MongoDB required for local demo:
export USE_MONGITA=true
python seed_db.py
export SBP_API_TOKEN=dev-class-token
flask --app app run -p 5002
```

In another terminal:

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
