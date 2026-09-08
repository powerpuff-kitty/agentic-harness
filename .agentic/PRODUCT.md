# Product

## Problem

Coding agents often receive fragmented, duplicated, or stale project context. Repositories mix product truth, architecture, prompts, task state, security rules, and vendor-specific instructions without a clear precedence or deterministic validation model.

AI-assisted UI development adds a related problem: agents can reproduce code patterns while gradually drifting away from a product's visual identity, component vocabulary, interaction rules, and accessibility expectations. Teams repeatedly restate design intent and still receive generic or inconsistent generated interfaces.

## Users

- Developers starting agent-assisted projects.
- Teams upgrading existing repositories for coding-agent use.
- Platform and security teams defining reusable rules and quality gates.
- Coding agents that need compact routing, scoped context, safe permissions, and verifiable completion criteria.
- Developers and small product teams using AI coding tools on existing user-facing products who need design consistency across generated changes.

## Product

Agentic Harness provides:

1. A clean target-project contract with `AGENTS.md` as the root router and `.agentic/` as canonical project context.
2. A browsable catalog of complete project variants, packs, policies, profiles, presets, and schemas.
3. Agent-facing skills and prompts in `agentic-harness-agents`.
4. A native Rust `ah` CLI for initialization, migration, upgrades, audits, validation, ADR management, adapter synchronization, quality gates, and deterministic design-intelligence workflows.
5. A separate `agentic-harness-app` web product that exposes equivalent canonical design operations through visual analysis, review, generation, comparison, and export workflows without making the CLI binary its implementation dependency.

### Design intelligence

The first design-intelligence release focuses on **Understand & Preserve**:

1. Analyze an existing project's measurable visual/design-system properties.
2. Separate observed evidence from inference, recommendation, and unknowns.
3. Review and preserve approved identity in a versioned Design Genome.
4. Compile task-specific implementation context/prompts deterministically for any supported AI coding workflow.
5. Re-analyze changes and report design-system/identity drift.

AI interpretation and design generation are optional layers. Deterministic analysis, artifact validation, and prompt/context compilation must remain useful without an API key where the required local inputs are available.

## Non-goals

- Running or hosting autonomous agents.
- Replacing application frameworks, package managers, issue trackers, or CI systems.
- Making model output trustworthy without evidence and deterministic checks.
- Locking projects to one model vendor.
- Claiming that automated checks prove subjective design quality, originality, or complete accessibility.
- Making commercial design-reference providers mandatory for core design-intelligence workflows.

## Success criteria

- A new user understands the filesystem model from the root README and `.agentic/README.md`.
- `ah init` creates a self-contained project without source-only metadata leakage.
- Existing repositories migrate through an explicit dry-run and conflict-aware process.
- Repeated composition and adapter synchronization are idempotent.
- Audits distinguish deterministic evidence, agent-assisted judgment, and checks not performed.
- Release binaries work offline and embed pinned canonical sources.
- Design analysis artifacts preserve evidence/provenance and can be reviewed without turning inference into truth automatically.
- The same approved Design Genome can drive compatible CLI and app workflows.
- Task-specific design context can be regenerated from canonical inputs without requiring an LLM.

## Current status

Beta. The target filesystem contract is versioned, but compatibility and migration behavior may evolve before 1.0. Design intelligence is an early product track under active implementation; its schemas are initially versioned as format version 1 but should be treated as pre-stable until explicitly promoted.
