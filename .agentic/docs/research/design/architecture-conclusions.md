# Design intelligence architecture conclusions

## Canonical identity

A project needs a versioned **Design Genome** that captures approved identity intent, visual language, composition, component vocabulary, scoped rules, examples, provenance, and rationale. It should reference application token/component sources rather than creating a competing implementation source of truth.

## Deterministic analysis first

Measure what can be measured without AI before asking an AI to interpret it. Static/runtime analyzers should emit one shared design-analysis artifact with stable evidence IDs. AI enrichment is optional and must distinguish observation, inference, recommendation, uncertainty, and human approval.

## Design Compiler

The Design Genome should compile deterministically into multiple targets. Natural-language prompts are one backend, not the canonical artifact. Other targets can include DTCG/JSON, CSS/Tailwind-style tokens, implementation briefs, documentation, QA manifests, component contracts, and MCP/context bundles. These are architectural targets, not a statement that every backend is implemented.

Same inputs + same compiler/schema version should produce equivalent normalized output.

## Work modes

Design tasks should declare intent:
- **explore** — propose materially different directions;
- **extend** — build within approved identity;
- **reproduce** — preserve an approved artifact with minimal interpretation;
- **revise** — propose changes to canonical identity with impact review.

Routine implementation must not silently become redesign.

## Research provider model

External screenshots, flows, datasets, and commercial services are evidence providers. Providers need capability/rights metadata for search, indexing, retention, redistribution, benchmark/training use, authentication, and cost. Research observations require review before they can influence canonical product/design truth.

## Artifact interoperability

Canonical schemas, shared fixtures and equivalent normalized outputs define interoperability. Neither a particular implementation stack nor an interface should become a competing source of design truth. Public documentation describes contracts and approved public capabilities, not internal consumer details.

## Reproducibility boundary

Reproducibility means approved structured identity, implementation artifacts, and analysis conditions can be regenerated/compared. It does not mean arbitrary generative models will emit pixel-identical interfaces from the same prose prompt.

## Anti-slop principle

Consistency and distinctiveness are separate goals. The system should detect unapproved drift, arbitrary values, duplicate primitives, missing states, and generic feature/template reuse, but must not replace one fashionable default with a universal anti-slop style.
