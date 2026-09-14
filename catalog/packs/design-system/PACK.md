# design-system

Use when visual consistency or design fidelity is important.

Required knowledge: evidence/reference separation, primitive/semantic/component tokens, foundations, layouts, components, interaction states, patterns, responsive behavior, accessibility, content rules, exemplars, anti-patterns.

Follow `skill/references/design-system-ontology.md`. Prefer deterministic tokens and component APIs over prose-only visual rules.

## Reproducible project baseline

Use the existing `components.json` catalogue as the canonical vocabulary. Do not create project-local parallel component lists when an existing catalogue id applies.

Select the closest project profile from `profiles.json`, then classify every applicable capability in a project inventory that conforms to `catalog/schema/design-system-inventory.v1.schema.json`. Keep foundations, reusable components and product-specific patterns separate.

Do not conflate:

- design approval with implementation maturity,
- implementation with verification,
- verification with publication permission.

The required status dimensions and evidence rules are documented in `INVENTORY.md`.

Profiles define minimum capabilities rather than mandatory screen content. A capability that is optional in a profile becomes required for a project once the product actually implements or depends on it. A `not-applicable` classification needs an explicit reason.

Project inventories should point to canonical implementation sources and revision-bound specimens/evidence instead of duplicating style claims. Portfolio consumers such as tcsn.io should consume approved exports derived from those inventories; they must not reskin host components to impersonate project components that do not exist.
