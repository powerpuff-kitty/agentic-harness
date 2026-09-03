# Design System Enforcement

When a project has or explicitly wants a design system, Agentic Harness treats it as an implementation constraint rather than optional inspiration.

`ah design-system-components <project>` infers likely required components from product/source evidence. `--write` persists a reviewable `DESIGN_SYSTEM_COMPONENTS.md` checklist. The result is intentionally a planning aid: product owners/designers should confirm inferred flows.

`ah audit` includes a `design_system` section and a `design_system` score when a design system is active. The deterministic baseline checks for likely raw-control bypasses, hard-coded color values outside recognized design-system paths, and inferred required components that are not represented in discovered component paths. These checks complement rather than replace visual regression, accessibility, Storybook/example review, and human design review.

A design system is considered active when the project installs the `design-system` pack, declares design-system language in project evidence, or contains a recognized design-system package. Projects without one are not penalized.
