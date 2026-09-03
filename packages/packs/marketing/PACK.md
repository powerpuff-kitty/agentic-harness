# Marketing Pack

Use this pack when a product needs durable go-to-market, positioning, messaging, audience, launch, pricing, or content knowledge.

## Purpose

Marketing knowledge is not implementation truth. Keep product behavior and technical truth in canonical product/architecture/security docs, and keep communication strategy in `marketing/`.

## Canonical project shape

When this pack is selected, create or maintain the following project-local structure when relevant:

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

Do not create empty ceremony. Omit files that are genuinely irrelevant.

## Boundaries

- `PRODUCT.md` = what the product actually does and why it exists.
- `ARCHITECTURE.md` = how the system is built.
- `DESIGN.md` / `BRAND.md` = product and brand rules.
- `marketing/` = how the product is positioned, communicated, distributed, launched, and sold.
- `REFERENCE.md` = evidence and observations, not approved claims.

Marketing claims must be traceable to product truth or evidence. Never convert assumptions, roadmap items, benchmarks, customer anecdotes, or competitor claims into facts without support.

## POSITIONING.md

Capture category, target market, problem, alternatives, differentiation, value proposition, reasons to believe, constraints, and explicit non-goals.

## MESSAGING.md

Capture approved one-liner, short description, long description, headlines, feature-to-benefit mapping, proof points, objection handling, terminology, tone, and prohibited/unsupported claims.

## AUDIENCES.md

Define audience segments, jobs-to-be-done, pains, desired outcomes, buying context, technical sophistication, objections, and decision criteria. Keep observed evidence distinct from hypotheses.

## COMPETITORS.md

Track alternatives, category positioning, strengths, weaknesses, pricing/packaging evidence, and meaningful differentiation. Date external evidence and avoid stale comparisons.

## PRICING.md

Document packaging hypotheses, metric, tiers, limits, cost drivers, willingness-to-pay evidence, constraints, experiments, and accepted decisions. Pricing experiments are not automatically durable policy.

## LAUNCH.md

Track launch goals, audiences, channels, assets, demos, announcement copy, readiness criteria, owners, timing, and post-launch measurements.

## CHANNELS.md

Document distribution channels, audience fit, acquisition mechanics, constraints, expected feedback loops, and measurement approach.

## CONTENT.md

Maintain content pillars, reusable narratives, demos, tutorials, case-study opportunities, proof assets, editorial backlog, and repurposing opportunities.

## FAQ.md

Keep externally useful answers aligned with current product truth. Flag answers that depend on roadmap or policy changes.

## Agent behavior

Before creating marketing strategy, inspect `PRODUCT.md`, `README.md`, architecture/security constraints, current pricing, user evidence, and existing brand docs. Ask only questions that materially affect positioning or claims. Separate facts, accepted decisions, hypotheses, experiments, and unresolved questions.
