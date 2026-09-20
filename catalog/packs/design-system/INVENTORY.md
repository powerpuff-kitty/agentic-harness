# Design-system inventory contract v1

The design-system pack standardizes **how** projects describe and prove their design systems. It does not standardize projects onto one visual identity, component implementation technology, or frontend framework.

Canonical inputs:

- `components.json` — stable catalogue ids and categories.
- `profiles.json` — minimum applicable capabilities by project type.
- `../../schema/design-system-inventory.v1.schema.json` — project inventory/evidence interchange contract.

## Layers

Keep three layers distinct:

1. **Foundations** — tokens, typography, icons, layout and surfaces.
2. **Reusable components** — generic UI capabilities drawn from the shared catalogue.
3. **Product patterns** — project-specific compositions such as an issue workspace, property card workflow, editor canvas, trading signal panel or messenger room.

Patterns may compose catalogue components but do not create new catalogue ids merely because a product has a unique workflow.

## Independent status dimensions

Never collapse these dimensions into one vague `complete` flag:

- **Applicability**: `required`, `optional`, `not-applicable`.
- **Implementation**: `missing`, `recipe-only`, `app-local`, `shared`.
- **Verification**: `not-run`, `passed`, `failed`, `blocked`, `not-applicable`.
- **Publication**: `private`, `approved`, `published`.

A design may be approved while its implementation is missing. A component may be implemented while browser verification is blocked. A verified component may remain private. Reporting must preserve those distinctions.

## Profiles

Profiles define minimum capabilities, not mandatory UI on every page. Select the closest profile and classify the rest of the catalogue explicitly:

- `headless` — no visual-component baseline.
- `marketing-site` — foundations plus a small content/action/form baseline.
- `web-app` — the reusable interactive application core.
- `data-heavy-app` — web-app plus dense navigation/data capabilities.
- `custom` — project-specific applicability with universal foundations.

Any optional catalogue capability becomes required for a project when the product actually implements or depends on that capability.

## Evidence rules

Inventory records reference implementation sources instead of duplicating claims. `recipe-only`, `app-local` and `shared` implementations require at least one source reference. Use specimens for reproducible examples, but do not treat a screenshot alone as implementation evidence.

Verification status refers to evidence for the stated project revision. Static markup or class-string assertions must not be reported as browser interaction/accessibility passes. Store revision-bound browser, responsive, interaction and visual-regression evidence separately and reference it from downstream reporting.

## Portfolio publication

Portfolio renderers such as tcsn.io should consume an approved project export derived from this inventory rather than scrape private repositories at runtime. Publication adapters must preserve each project's own tokens and components and must not recolor the host design system to impersonate missing project components.

The inventory is suitable for publication only after the project owner has set the relevant entries to `approved` or `published`; the schema itself does not grant publication permission.
