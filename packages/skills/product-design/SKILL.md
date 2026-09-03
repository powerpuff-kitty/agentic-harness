# Product Design Skill

Use this skill for UI, UX, design-system, and product-surface work.

## Before implementation

1. Read `DESIGN.md`.
2. Read only the relevant files under `docs/design/`.
3. Inspect accepted examples under `examples/design/`.
4. Identify missing rules instead of inventing them.

## Procedure

1. Restate the user/task goal in product terms.
2. Identify the existing component/pattern that is closest.
3. Reuse design tokens; do not introduce one-off visual values without justification.
4. Preserve accessibility, responsive behavior, keyboard use, focus states, loading, empty, error, and disabled states.
5. Prefer a small number of coherent variants over polishing the first idea when exploration is requested.
6. Implement the chosen pattern completely.
7. Run applicable UI checks/tests.
8. Compare the result against accepted exemplars.

## After implementation

- Add a reusable exemplar when a new accepted visual pattern is introduced.
- Update `docs/design/` when a durable rule changed.
- Convert mechanically enforceable design rules into lint/tests when practical.
