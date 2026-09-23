# ADR-012: Add a language-neutral architecture capability graph

- Status: accepted
- Date: 2026-09-22
- Deciders: project owner and maintainers
- Supersedes: none
- Superseded by: none

## Context

Agentic Harness can describe project truth, design, decisions, checks and source graphs, but it lacks one canonical contract for architectural ownership across differently structured repositories. Modern projects may express the same capability boundary through TypeScript packages, Rust crates, workers, SDKs, modules or mixed-language monorepos. Requiring one folder convention would confuse structure with architecture and would not support staged migrations.

The architecture contract also needs to preserve the existing distinction between a declared rule, a check that observed the rule, and a restriction that is actually enforced.

## Decision drivers

- represent domain/capability ownership without prescribing folders or languages;
- distinguish apps and surfaces from capabilities that own behavior;
- represent contracts, providers, adapters, engines, infrastructure and authorities explicitly;
- support observed, target and migration architecture in the same public contract;
- make dependency direction and capability cycles machine-checkable;
- preserve evidence semantics so diagrams and manifests do not overclaim enforcement;
- remain usable by future deterministic CLI analysis without requiring hosted services.

## Considered options

1. Keep architecture only in prose and repository-specific scripts.
2. Standardize a mandatory `apps/packages/adapters` directory layout.
3. Reuse the source graph as the architecture model.
4. Add a separate language-neutral Architecture Graph contract with typed roles, edges, constraints and verification state.

## Decision

Adopt option 4.

`catalog/schema/architecture-graph.v1.schema.json` is the canonical public v1 shape. It models capabilities, contracts, providers, adapters, apps, engines, surfaces, infrastructure and authorities as typed nodes. Typed edges describe dependency, ownership, implementation, exposure, adaptation, persistence, authority, composition and calls.

`depends-on` edges are reserved for capability-to-capability dependency direction. Semantic validation requires resolved node references and an acyclic capability dependency graph.

Architecture constraints explicitly record `declared`, `checked`, `enforced` or `unsupported` state. Checked or enforced claims require a named mechanism and evidence references. Schema or semantic validity alone never proves repository conformance.

The contract describes roles, not directory names. A repository may use any physical structure that preserves its declared boundaries.

## Consequences

Positive:
- repositories with different languages and layouts can share one architecture vocabulary;
- migrations can represent current and target ownership without pretending work is complete;
- future CLI tooling can derive dependency checks, drift reports, diagrams and task routing from one bounded contract;
- agent context can reason about capability ownership rather than broad folder names.

Costs and limits:
- projects must map their architecture deliberately instead of receiving a folder template;
- JSON Schema cannot prove path existence, import conformance or all graph semantics;
- CLI/runtime tooling is separate work and publishing this schema does not mean automatic enforcement exists.

The contract is additive and optional for existing projects. Adoption must not rewrite project-authored architecture merely to match a cosmetic layout.

## Evidence

- `catalog/schema/architecture-graph.v1.schema.json`
- `.agentic/docs/architecture/architecture-graph.md`
- `.agentic/evals/fixtures/architecture-graph.v1.json`
- `.github/scripts/validate_architecture_contracts.py`
- Issue #176

## Verification

Catalog validation requires the schema to remain present and valid JSON. Machine-contract CI validates the schema and synthetic fixture, rejects unresolved references and duplicate IDs, enforces capability-only dependency edges, rejects capability dependency cycles, checks coverage counts, and verifies that checked/enforced constraints carry mechanism and evidence.
