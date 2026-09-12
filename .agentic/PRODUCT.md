# Product

## Problem

Coding agents receive fragmented, duplicated or stale project context. Product truth, architecture, task state, security rules and vendor instructions often lack explicit precedence or reliable validation. AI-assisted interface changes can also drift from accepted identity, component vocabulary and interaction requirements.

## Users

Developers and teams using coding agents on new or existing repositories; platform/security teams defining reusable rules; and contributors who need compact, scoped context with verifiable completion criteria.

## Public product boundary

Agentic Harness comprises three public responsibilities:

1. `agentic-harness`: project-context contracts, materialized context templates, packs, policies, profiles, presets, schemas and registries.
2. `agentic-harness-agents`: reusable procedures and host-integration guidance, distributed separately from project truth.
3. `agentic-harness-cli`: the Rust `ah` implementation for deterministic composition, validation, audit/artifact gates and experimental architecture/design inspection.

Public documentation describes approved public capabilities only. Follow [public-surface policy](docs/project/public-surface.md) for source, issues, PRs, diagrams and generated artifacts.

## Current capability boundaries

Context templates do not contain application scaffolds, completed product decisions or evidence that an agent obeyed a policy. Installed structure, project configuration, check configuration and verified behavior are distinct.

The CLI command contract is maintained in `agentic-harness-cli/docs/cli-contracts.md`. Initialization, current-layout upgrades, contract validation and explicit artifact gates are implemented. Architecture/design analysis and agentic inspection remain experimental with declared coverage limits. Audit discovers checks but does not execute the project's test suite; unknown overall/readiness measurements remain null.

Filesystem migration automation, ADR-creation commands, comprehensive native adapter synchronization and executed project-completion checks are planned work, not current CLI promises. Experimental model-profile migration preview is separate from filesystem migration.

## Design intelligence

The initial **Understand & Preserve** workflow aims to analyze measurable design evidence, review a candidate Design Genome, compile task-specific context from approved intent, and compare subsequent measured drift. Static evidence cannot establish complete accessibility, runtime behavior, originality or subjective design quality.

Deterministic operations should remain useful without an API key when local inputs are available. AI interpretation and external providers are optional. Canonical schemas and fixtures define interoperability; implementation consumers do not become project-truth authorities.

## Non-goals

- Running or hosting autonomous agents or replacing application frameworks, package managers, issue trackers or CI systems.
- Locking project truth to one vendor or making commercial providers mandatory.
- Treating generated files, written policy or structural validation as proof of safety, enforcement, design quality or production readiness.

## Success criteria

A developer can understand the public contract, install a compatible CLI, configure project-specific context, load it through a supported host integration, detect supported violations and inspect actual verification evidence. Each part must identify its implementation status and checks performed.

Preserve user content during upgrades; record source pins; surface conflicts and unknowns; never silently approve inferred identity or replace accepted project truth. Integration and outcome evaluation are required before claiming improved model performance.

## Current status

Beta. Filesystem/artifact contracts are versioned but pre-stable. The [remediation roadmap](plans/audit-remediation-2026-09-12.md) prioritizes one demonstrably complete adoption path. Tickets and schemas are not evidence that the remaining workflow has shipped.
