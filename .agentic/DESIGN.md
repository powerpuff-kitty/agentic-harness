# Design and documentation experience

## Primary experience

A visitor should understand Agentic Harness in this order:

1. Root README: what it is and where to start.
2. Root `AGENTS.md`: compact agent router.
3. `.agentic/README.md`: annotated project-context map.
4. `catalog/`: reusable variants and modules.
5. CLI help: deterministic actions and compatibility behavior.

## Principles

- Teachability before ontology depth.
- One obvious canonical path for each kind of truth.
- Plain Markdown/YAML/JSON that humans and tools can inspect.
- Complete examples of the contract rather than hidden generator-only overlays.
- Progressive disclosure: concise canonical truth links to deeper supporting docs.
- Vendor-neutral names; vendor adapters stay thin.
- Explicit lifecycle and precedence instead of implicit conventions.

## Naming

- `.agentic/`: project knowledge, governance, provenance, and work state.
- `.agents/`: reusable agent procedures installed into the project.
- `decisions/`: durable accepted or proposed choices.
- `plans/`: temporary strategy.
- `tasks/`: active coordination state.
- `catalog/variants/`: complete project-type starting structures.

## Design-system compliance

For user-facing projects, the design-system pack and audit enforce use of canonical tokens and components. Component planning is based on product flows and must distinguish inferred need from implemented evidence.

## Documentation quality

Every first-class directory has a README explaining purpose, lifecycle, and non-goals. Machine contracts have schemas. Terminology must remain consistent across canonical content, skills, CLI output, and migration guidance.
