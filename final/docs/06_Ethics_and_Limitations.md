# Ethics, Societal Impact, and Limitations (G6-style)

**Project:** Neighborhood Small Business Platform (SBP)

## Societal benefit

- Supports **local commerce** and neighborhood economic resilience.
- Makes small-business discovery **machine-readable** for civic tools, newsletters, and accessibility tech.

## Ethical considerations

| Frame | Application |
|-------|-------------|
| **Virtue** | Transparency via `provenance` and honest `quality_flags` rather than overstating completeness. |
| **Consequentialist** | Public benefit of discoverability vs risk of exposing owner contact — mitigated by default **public** classification and Bearer-gated email/phone. |
| **Deontological** | Respect upstream licenses (Yelp display-only if used; CC-BY-4.0 on curated demo data). |

## Privacy & security

- Owner email/phone treated as **restricted** unless client presents valid `SBP_API_TOKEN`.
- No API secrets in repository or API responses.
- Demo dataset is fictionalized contact info for class use only.

## Limitations

1. **Dataset size** — six curated Seattle businesses; not production coverage.
2. **Upstream** — Yelp Fusion documented in G8 but not required for demo; live integration needs API key and rate-limit handling.
3. **Agentic consumers** — JSON is agent-friendly; HTML consumer UI is out of scope for API deliverable.
4. **Network effects** — SBP does not replicate Yelp’s review graph or social proof; portability focuses on **structure**, not platform scale.

## What we would do next

- Community partner review of fields designated `public` vs `restricted`.
- Data retention policy if caching Yelp responses (see G9 TTL discussion).
