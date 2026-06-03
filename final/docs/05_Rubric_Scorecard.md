# Final Project Rubric Scorecard

**Student:** Sneha Reddy | **Course:** IMT 542 A Sp 26  
**Canvas:** [Final Project assignment](https://canvas.uw.edu/courses/1883881/assignments/11160571)  
**Submission guide:** [00_FINAL_SUBMISSION_GUIDE.md](00_FINAL_SUBMISSION_GUIDE.md)

Mark each item **Done** before submitting. Total: **50 points** (10 × 5).

| Rubric item | Done | Evidence |
|-------------|------|----------|
| **Info story 1** — Purpose, user, goal clear; no extra scope | ☑ | [01_Information_Story.md](01_Information_Story.md) §1–4 |
| **Info story 2** — Requirements in/out of scope; portability in reqs | ☑ | [01_Information_Story.md](01_Information_Story.md) §5–6, R8–R9 |
| **Existing structures 1** — Sources analyzed; access & quality | ☑ | [02_FAIR_Assessment.md](02_FAIR_Assessment.md) |
| **Existing structures 2** — Transformations defined | ☑ | [02_FAIR_Assessment.md](02_FAIR_Assessment.md) §3–4, [03_Structure_Design.md](03_Structure_Design.md) |
| **New portable structure 1** — ≥2 of: info, structure, format, access | ☑ | [03_Structure_Design.md](03_Structure_Design.md) §1; [sbp_schema_v1.json](../sbp_schema_v1.json) |
| **New portable structure 2** — Meets requirements only | ☑ | `normalizer.py`, `app.py`, `live_search.py` |
| **Functional system 1** — Information accessible as documented | ☑ | [../README.md](../README.md); Flask + ngrok; [web/platform.html](../web/platform.html) |
| **Functional system 2** — Correct and complete per story | ☑ | Live Yelp+OSM search; 12 `pytest` tests; end-to-end UI |
| **Quality 1** — Desired vs actual quality documented | ☑ | [04_Quality_Performance_Security.md](04_Quality_Performance_Security.md) §1–2 |
| **Performance 2** — Desired vs actual performance + remediation | ☑ | [04_Quality_Performance_Security.md](04_Quality_Performance_Security.md) §3–5 |

---

## Presentation deliverables

| Item | Location |
|------|----------|
| PPTX (in-class) | [presentation/IMT542_Final_Project.pptx](../presentation/IMT542_Final_Project.pptx) |
| HTML slides (Reveal.js) | [presentation/index.html](../presentation/index.html) |

---

## Canvas submission checklist

- [ ] GitHub repo public: https://github.com/Sneha-8/IMT-542  
- [ ] `final/README.md` describes setup and API  
- [ ] PPTX committed under `final/presentation/`  
- [ ] Canvas URL field: **HTTPS** API link (ngrok or deploy)  
- [ ] Optional: link to `http://YOUR_HOST/web/platform.html` if UI hosted

**Ngrok example:**

```bash
cd final && USE_MONGITA=true flask --app app run -p 5002
ngrok http 5002
# Submit: https://xxxx.ngrok-free.app/health
```
