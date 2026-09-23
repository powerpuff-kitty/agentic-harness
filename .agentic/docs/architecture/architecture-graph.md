# Architecture Graph v1

Architecture Graph v1 is the public, language-neutral contract for describing a project's architectural roles and dependency intent without prescribing a filesystem layout.

## Purpose

The graph answers four separate questions:

1. **What architectural roles exist?** Capabilities, contracts, providers, adapters, apps, engines, surfaces, infrastructure and authorities.
2. **How are those roles related?** Typed edges record dependencies, ownership, implementation, exposure, persistence and authority relationships.
3. **What boundary rules are declared?** Constraints record allowed/forbidden dependencies and similar architectural requirements.
4. **What has actually been verified?** Constraint status, mechanisms, evidence references, coverage and `not_checked` keep declarations separate from checks and enforcement.

A valid graph is not proof that the code follows it. Schema validity is structural evidence only. Semantic validators add referential-integrity and acyclicity checks; repository analyzers and host enforcement require separate evidence.

## Roles, not folders

The contract deliberately does not require `apps/`, `packages/`, `crates/` or any other directory convention.

A capability might be implemented by a TypeScript workspace package, Rust crate, Python module or a set of files during migration. An app is a composition/deployment surface, while a capability owns domain/application behavior. Providers and adapters connect implementations or external systems without becoming implicit domain authorities.

## Capability dependencies

`depends-on` edges are reserved for capability-to-capability dependencies. Semantic validation rejects missing endpoints, non-capability endpoints and cycles.

Other typed edges describe ownership or integration and are not interpreted as capability dependency direction.

## Constraints and evidence

Architecture constraints carry an explicit status:

- `declared`: desired or documented rule; no enforcement claim.
- `checked`: a concrete mechanism evaluated the rule and evidence is referenced.
- `enforced`: a concrete mechanism actively prevents the forbidden state and evidence is referenced.
- `unsupported`: the current toolchain cannot establish the rule.

`checked` and `enforced` require both a mechanism and evidence reference. This preserves the broader Agentic Harness distinction between declaration, checking and enforcement.

## Migration graphs

A graph may be `observed`, `target` or `migration`. Individual nodes also carry lifecycle state. This allows a repository to model today's runtime-first structure and a capability-first target in one bounded artifact without pretending the migration is already complete.

## Graph-only reference analysis

The canonical repository includes a deterministic reference analyzer at `.github/scripts/architecture_graph.py`. It consumes an already-supplied Architecture Graph plus explicit task paths. It does **not** scan a checkout, resolve imports, authenticate declarations or establish enforcement.

### Task-to-capability routing

Routing uses the most-specific declared node path for each task path, then follows typed graph relationships back to capability ownership:

- a capability routes to itself;
- a contract routes through incoming `owns`;
- a surface routes through incoming `exposes`;
- an app/engine routes through `composes` or `adapts`;
- an adapter/provider may route through `implements` to a contract and its owning capability;
- infrastructure routes through incoming `persists-to`;
- an authority routes through `authoritative-for`.

The result preserves matched capabilities, their declared owner paths, contracts and surfaces. A path mapping to multiple capabilities is `ambiguous`; a path with no declared mapping is `unresolved`. Neither case is guessed away.

### Duplicate-capability candidates

A capability node may optionally declare `metadata.capability_key` as a stable logical identity for graph-level review. When it is absent, the reference analyzer falls back to a normalized capability name. Multiple active capability nodes with the same identity at different paths are emitted as `review_required` duplicate **candidates**. Equal identity is not proof that behavior is duplicated, so this result is never an automatic architecture violation.

### Stable architecture summaries

The analyzer can render a stable Markdown summary of capability paths, dependencies, contracts, surfaces, constraints, coverage and explicit `not_checked` items. Exact comparison can detect documentation drift against the supplied graph. This checks generated summary consistency only; it does not prove the graph matches source code.

The machine-readable derived result conforms to `catalog/schema/architecture-analysis.v1.schema.json`. Synthetic TypeScript/Vue, Rust-workspace and mixed-language fixtures demonstrate the same semantics without special-case folder rules.

## Graph-derived guardrails, drift and diagrams

The same reference analyzer can derive additional artifacts from already-declared graph data. These outputs remain descriptive/planning evidence and do not turn declarations into repository enforcement.

### Guardrail plans

Declared `allowed-dependency` and `forbidden-dependency` constraints can become provider-neutral guardrail-plan entries when both subject and target nodes have paths. An entry records the source constraint/status, path pair and an `allow` or `forbid` effect. Its `enforcement_claim` is always false.

If either path is absent, the entry is `unresolved` with an explicit missing-path reason. The analyzer never invents a directory rule, substitutes another node, or upgrades `declared`/`checked` metadata into enforcement.

Actual ESLint, dependency-cruiser, Nx, Rust or other generated rules belong to CLI/runtime adapters and require separate source/enforcement evidence.

### Graph-to-graph drift

`compare_graphs(before, after)` compares two supplied graphs for the same project and reports:

- added, removed and changed nodes;
- added/removed typed edges;
- added, removed and field-level changed constraints;
- coverage changes;
- added/removed `not_checked` declarations.

The result is deterministic under node/edge/constraint ordering. It is graph-document drift only. It does not detect source/import drift unless a repository analyzer first supplies a graph based on observed source.

### Surface inventory

Every capability receives a descriptive surface state: `exposed` with its declared surfaces, or `internal_or_unexposed`. Internal capabilities are valid; absence of a surface is not a universal violation.

### Stable Mermaid

The analyzer renders stable Mermaid from declared node IDs/names/kinds and typed edges. Exact comparison can detect diagram drift against the supplied graph. The diagram does not independently prove runtime or repository architecture.

Machine-readable outputs use `catalog/schema/architecture-derivatives.v1.schema.json` and `catalog/schema/architecture-drift.v1.schema.json`.

## Runtime boundary

This repository owns the canonical schema and semantic meaning. Deterministic repository inspection, generated dependency checks and drift analysis belong in `agentic-harness-cli`. Reusable agent procedures belong in `agentic-harness-agents`.

The synthetic fixture at `.agentic/evals/fixtures/architecture-graph.v1.json` validates the public contract without identifying a downstream project.
