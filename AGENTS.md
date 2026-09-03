# Agent Guide

This file is the repository-level router for coding agents.

## Operating rules

- Read only the minimum context needed for the task.
- Treat repository documentation as the source of truth.
- Do not invent product, architecture, design, security, or domain decisions.
- If required knowledge is missing or contradictory, surface the gap.
- Prefer deterministic validation over prose instructions when a rule can be tested.
- When a durable decision changes, update the appropriate documentation or ADR.
- Keep changes scoped; avoid unrelated refactors.

## Context routing

For product behavior and business constraints:
- `PRODUCT.md`
- `docs/product/`

For architecture and technical boundaries:
- `ARCHITECTURE.md`
- `docs/architecture/`
- `docs/decisions/`

For UI, UX, visual design, content, and design tokens:
- `DESIGN.md`
- `docs/design/`
- `.agents/skills/product-design/SKILL.md`
- `examples/design/`

For security-sensitive work:
- `SECURITY.md`
- `.agents/skills/security-review/SKILL.md`

For planning larger changes:
- `docs/plans/current.md`
- `.agents/skills/implementation-plan/SKILL.md`

For review before completion:
- `.agents/skills/release-review/SKILL.md`
- `evals/README.md`

## Definition of done

Before declaring work complete:
1. Check the relevant source-of-truth documents.
2. Run applicable tests, type checks, linters, builds, and evals.
3. Verify the implementation against accepted examples where available.
4. Update documentation if behavior, architecture, or a durable decision changed.
5. State unresolved assumptions or risks explicitly.
