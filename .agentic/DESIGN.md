# Design and documentation experience

## Primary experience

A visitor should understand Agentic Harness in this order:

1. Root README: what it is and where to start.
2. Root `AGENTS.md`: compact agent router.
3. `.agentic/README.md`: annotated project-context map.
4. `catalog/`: reusable variants and modules.
5. CLI help: deterministic actions and compatibility behavior.
6. For design-intelligence workflows, analysis evidence precedes inference, approved identity, and generated outputs.

## Principles

- Teachability before ontology depth.
- One obvious canonical path for each kind of truth.
- Plain Markdown/YAML/JSON that humans and tools can inspect.
- Complete examples of the contract rather than hidden generator-only overlays.
- Progressive disclosure: concise canonical truth links to deeper supporting docs.
- Vendor-neutral names; vendor adapters stay thin.
- Explicit lifecycle and precedence instead of implicit conventions.
- Deterministic measurement before optional AI interpretation.
- Imported references are evidence until explicitly approved.
- Consistency and distinctiveness are separate goals; do not encode one fashionable aesthetic as a universal anti-slop rule.

## Naming

- `.agentic/`: project knowledge, governance, provenance, and work state.
- `.agents/`: reusable agent procedures installed into the project.
- `decisions/`: durable accepted or proposed choices.
- `plans/`: temporary strategy.
- `tasks/`: active coordination state.
- `catalog/variants/`: complete project-type starting structures.
- **Design Genome**: versioned approved identity/design contract used to preserve a product's visual and interaction language.
- **Design analysis**: evidence artifact containing deterministic measurements/findings plus optional reviewed interpretations.
- **Design Compiler**: deterministic transformation from approved design context/task inputs to prompts, briefs, tokens, docs, QA artifacts, and other targets.

## Design Genome

A Design Genome should capture enough structured context for a fresh human or agent to extend a product coherently without the original conversation. It may include:

- brand/product intent, personality, differentiation, and scoped anti-patterns;
- typography, color, spacing, geometry, imagery, icons, motion, and density;
- composition/hierarchy and responsive principles;
- approved component vocabulary, variants, states, and accessibility expectations;
- required/recommended/optional rules with scope, rationale, provenance, and exceptions;
- approved/rejected/reference examples with reasons.

The Design Genome references the application's canonical token/component implementations where possible; it must not create a competing implementation source of truth merely to satisfy an importer or compiler.

## Design work modes

- `explore`: generate or compare materially different directions.
- `extend`: implement within the approved identity.
- `reproduce`: preserve an approved design with minimal interpretation.
- `revise`: propose changes to canonical identity with impact review.

Routine feature work should default to preserving the current approved identity rather than opportunistically redesigning the product.

## Design-system compliance

For user-facing projects, the design-system pack and audit enforce use of canonical tokens and components. Component planning is based on product flows and must distinguish inferred need from implemented evidence.

Design-intelligence compliance adds evidence for visual values, component/state coverage, responsive/runtime behavior, accessibility checks, and identity drift. Automated results must state what was not checked and must not claim complete accessibility, subjective quality, or originality verification.

## Documentation quality

Every first-class directory has a README explaining purpose, lifecycle, and non-goals. Machine contracts have schemas. Terminology must remain consistent across canonical content, skills, CLI output, app output, and migration guidance.
