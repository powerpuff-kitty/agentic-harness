# Marketing

Use this skill to initialize, improve, audit, or update product marketing knowledge without confusing promotional messaging with product truth.

## Modes

### INIT
Inspect the product and existing evidence, ask only high-impact unresolved questions, propose the marketing structure, then create the useful project-local `marketing/` files.

### UPDATE
Preserve accepted positioning and messaging unless evidence or an explicit decision changes them. Update affected files and flag downstream copy that may now be stale.

### AUDIT
Read-only. Evaluate positioning clarity, audience specificity, claim support, competitor freshness, pricing coherence, launch readiness, channel fit, and contradictions with canonical product docs.

## Mandatory workflow

1. Read `PRODUCT.md`, `README.md`, relevant architecture/security docs, brand/design guidance, pricing/configuration, and existing marketing files.
2. Separate detected facts, external evidence, accepted decisions, hypotheses, experiments, and unresolved questions.
3. Determine which marketing files are actually needed. Avoid empty boilerplate.
4. For INIT, ask concise questions about target audience, problem, category, differentiation, business model, geography, launch stage, and major constraints only when they cannot be safely inferred.
5. Propose positioning and supported claims before publishing durable messaging.
6. Create/update project-local files under `marketing/`.
7. Cross-check every factual marketing claim against product truth or cited evidence.
8. Flag contradictions, stale competitive information, unsupported superlatives, invented customer proof, and roadmap presented as shipped functionality.
9. Summarize changed marketing truth and unresolved hypotheses.

## Default project-local structure

```text
marketing/
├── POSITIONING.md
├── MESSAGING.md
├── AUDIENCES.md
├── COMPETITORS.md
├── PRICING.md
├── LAUNCH.md
├── CHANNELS.md
├── CONTENT.md
└── FAQ.md
```

Create only the files that have useful content.

## Positioning questions

Prefer questions such as:
- Who is the primary user/buyer?
- What painful job are they solving?
- What do they use instead today?
- Why should they choose this product?
- What proof can support that claim?
- What markets/geographies matter?
- Is the goal validation, launch, growth, or mature optimization?

Do not ask for information already present in the repository.

## Evidence rules

- Product docs outrank marketing copy on product behavior.
- Accepted business decisions outrank old experiments.
- External competitor/pricing evidence must be dated.
- A hypothesis must remain labeled as a hypothesis until accepted.
- Never fabricate customers, metrics, testimonials, benchmarks, market share, awards, compliance, integrations, or availability.

## Completion

Report which marketing files were created/updated, key positioning decisions, claims that are evidence-backed, hypotheses still being tested, stale/conflicting material, and next recommended validation work.
