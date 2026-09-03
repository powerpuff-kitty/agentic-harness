# Implementation Plan Skill

Use for non-trivial changes spanning multiple components, migrations, or architectural boundaries.

## Procedure

1. Read `PRODUCT.md`, `ARCHITECTURE.md`, relevant ADRs, and relevant domain docs.
2. Define the goal and explicit non-goals.
3. List affected components and trust boundaries.
4. Identify migrations, compatibility constraints, rollout needs, and rollback strategy.
5. Break work into independently verifiable steps.
6. Define validation for each step.
7. Record unresolved decisions before implementation.
8. Keep `docs/plans/current.md` updated while the work is active.

A plan should explain sequencing and validation, not duplicate implementation details that belong in code.
