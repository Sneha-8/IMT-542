# Ethics, Societal Impact, and Limitations

**Project:** LocalFind / SBP v1.0 | **Author:** Sneha Reddy

## Societal benefit

- Supports **local commerce** and neighborhood economic resilience.
- Makes small-business discovery **machine-readable** for civic newsletters, maps, and accessibility tools.
- Covers diverse business types (not only restaurants): fashion, fitness, services, retail.

## Ethical considerations

| Frame | Application |
|-------|-------------|
| **Virtue** | Transparent `provenance` and honest `quality_flags`; we do not overstate data completeness. |
| **Consequentialist** | Public benefit of discoverability vs risk of exposing owner contact — mitigated by default **public** classification and Bearer-gated phone/email. |
| **Deontological** | Respect Yelp Fusion terms (display-only, attribution via links) and OSM ODbL (attribution in `provenance`). |

## Privacy and security

- Owner email/phone are **restricted** unless client presents valid `SBP_API_TOKEN`.
- `YELP_API_KEY` stored only in `.env` (gitignored).
- Curated demo contacts in `small_businesses.json` are fictionalized for class use.

## Limitations

1. **Geography** — Seattle metro focus; not national coverage.
2. **Upstream dependency** — Yelp rate limits and OSM throttle; live refresh can take 15–40 seconds.
3. **Coverage gaps** — OSM lacks ratings; Yelp lacks some independents; merged cache is best-effort.
4. **Not a replacement for Yelp/Google** — We provide **portable structure** for a specific civic story, not full review graphs or ads.
5. **Agentic consumers** — JSON is agent-ready; full M2M terms of service not defined beyond class scope.

## What we would do next

- Community partner review of public vs restricted fields.
- Data retention policy for cached Yelp responses.
- Neighborhood association partnerships for verified listings.
- Deploy on fixed HTTPS with uptime monitoring (G9 roadmap).
