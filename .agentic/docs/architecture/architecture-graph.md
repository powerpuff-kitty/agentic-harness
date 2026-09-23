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

## Runtime boundary

This repository owns the canonical schema and semantic meaning. Deterministic repository inspection, generated dependency checks and drift analysis belong in `agentic-harness-cli`. Reusable agent procedures belong in `agentic-harness-agents`.

The synthetic fixture at `.agentic/evals/fixtures/architecture-graph.v1.json` validates the public contract without identifying a downstream project.
