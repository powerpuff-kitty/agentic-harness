# ADR-006: Add a repository-native design intelligence contract

- Status: accepted
- Date: 2026-09-08
- Deciders: project owner
- Supersedes: none
- Superseded by: none
- Public-scope clarification: 2026-09-12; consumer-neutral wording, technical decision unchanged.

## Context

AI-assisted UI development can drift away from an existing product's visual identity, component system, states, and interaction rules even when the code remains technically valid. Existing design-context tools tend to focus on extraction, generation, inspiration, or AI delivery separately. Agentic Harness already separates canonical truth, agent procedure, and deterministic enforcement, which provides a natural place to govern design identity as project-owned context.

Canonical design artifacts should be interoperable without coupling their semantics to a particular implementation or interface.

## Decision drivers

- Preserve identity across agents, models, sessions, and contributors.
- Prefer deterministic measurement and compilation where AI is unnecessary.
- Keep imported references and AI inferences subordinate to reviewed project truth.
- Avoid coupling core workflows to a commercial design/reference provider.
- Prevent semantic drift through versioned contracts and shared fixtures.
- Make research/provenance recoverable from the repository instead of chat history.

## Considered options

1. Store only a prose `DESIGN.md` and rely on agents to interpret it.
2. Adopt a third-party design-context SaaS as the canonical source.
3. Build a repository-native Design Genome, unified analysis artifact, and deterministic compiler with optional AI/provider adapters.

## Decision

Adopt option 3.

Agentic Harness will define:

- a versioned Design Genome for approved identity, rules, components, examples, and provenance;
- a unified design-analysis format that separates deterministic measurements, findings, inference, recommendation, and review;
- an analyzer-first workflow where AI interpretation is optional;
- a deterministic Design Compiler whose targets include prompts/briefs and can expand to tokens, docs, QA, and tool context;
- a provider-neutral research layer with explicit licensing/retention capabilities;
- interoperable artifact semantics through canonical schemas and fixtures rather than implementation-specific dependencies.

The initial product slice is **Understand & Preserve**: analyze an existing product, review/capture identity, compile precise task context, and detect drift after changes.

## Consequences

Positive:
- design identity becomes explicit, versioned, portable, and reviewable;
- users can benefit without an AI API for deterministic paths;
- implementation details can evolve without duplicating artifact semantics;
- external providers become optional evidence sources rather than dependencies.

Costs/risks:
- schema evolution and migration become part of the public contract;
- subjective design quality cannot be reduced safely to deterministic metrics;
- runtime analysis requires controlled render environments for reproducible visual evidence;
- provider licensing/retention rules need explicit governance.

Reversibility:
- schemas are additive public artifacts and can be versioned/superseded;
- the design track is initially pre-stable and can change before a stable release;
- external providers remain adapters and can be removed without invalidating canonical project identity.

## Evidence

See `../docs/research/design/README.md` and linked research notes. Product scope is tracked by issues #22-#68 and the corresponding public CLI backlog. This decision records intended architecture, not completion of every implementation target.

## Verification requirements

- catalog validation accepts all public design schemas;
- design-analysis fixtures validate against the unified schema;
- Design Genome fixtures validate against its schema;
- producer/consumer compatibility uses shared canonical fixtures;
- no inference/import becomes approved Design Genome truth without explicit review;
- v0.1 demonstrates analyze -> review -> compile -> re-analyze without requiring a model API key.

Record executed evidence separately; the requirements above are not test results.
