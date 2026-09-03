# Design Source of Truth

This is the compact design-system index. Put detailed rules under `docs/design/`; keep raw evidence in `REFERENCE.md`.

## Principles

- Prefer reusable rules over page-specific pixel descriptions.
- Separate observed evidence from accepted design decisions.
- Use primitive -> semantic -> component token layers.
- Components and layouts should consume semantic/component tokens rather than scattered raw values.
- Document states, responsive behavior, accessibility, content constraints, examples, and anti-patterns.
- Convert stable visual rules into code/tokens/tests where practical.

## Ontology

- `docs/design/tokens/` — primitives, semantic aliases, component tokens
- `docs/design/foundations/` — grid, containers, density, breakpoints, accessibility
- `docs/design/layouts/` — reusable composition
- `docs/design/components/` — anatomy, variants, behavior and states
- `docs/design/patterns/` — repeated interactions and product states
- `docs/design/content/` — voice, labels, formatting and microcopy
- `docs/design/anti-patterns.md` — known bad outcomes
- `docs/design/decisions.md` — accepted design decisions
- `examples/` — accepted outcomes

Agents doing design-system work should use the installed `.agents/skills/design-system/SKILL.md` when available. The source boilerplate keeps the reusable skill under `skills/design-system/`.