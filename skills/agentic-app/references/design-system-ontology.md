# Design-System Ontology

Use this ontology when extracting, documenting, generating, or auditing UI design systems.

## Layers

1. Evidence: screenshots, Figma, existing code, brand references -> `REFERENCE.md` or source links.
2. Primitive tokens: raw scales such as neutral.100, space.4, radius.2.
3. Semantic tokens: purpose-based aliases such as color.text.muted, color.surface, space.section.
4. Component tokens: button.primary.background, input.border.focus.
5. Foundations: grid, containers, density, breakpoints, accessibility.
6. Layouts: app shell, page container, stack, cluster, grid, sidebar, split pane, detail, form.
7. Components: anatomy, variants, states, behavior.
8. Patterns: search, filters, empty/loading/error states, onboarding, destructive confirmation.
9. Content: voice, labels, formatting, microcopy.
10. Exemplars and anti-patterns.

## Classification examples
- `16px gap between cards` -> spacing/layout token or layout rule, not a component unless card-specific.
- `content max-width 1280px` -> container/layout.
- `button height 36px` -> component anatomy, preferably referencing a size token.
- `muted text #71717A` -> semantic color token mapped to a primitive.
- `sidebar collapses below 1024px` -> responsive layout behavior.

Prefer primitive -> semantic -> component token chains. Avoid scattering raw values through component docs.

## Recommended docs/design structure

```text
docs/design/
├── README.md
├── principles.md
├── tokens/
├── foundations/
├── layouts/
├── components/
├── patterns/
├── content/
├── anti-patterns.md
└── decisions.md
```

Do not invent design rules from a single ambiguous screenshot. Record observations separately from distilled rules and state confidence when inference is uncertain.
