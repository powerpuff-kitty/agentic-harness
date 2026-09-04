# Product

## Problem

Coding agents often receive fragmented, duplicated, or stale project context. Repositories mix product truth, architecture, prompts, task state, security rules, and vendor-specific instructions without a clear precedence or deterministic validation model.

## Users

- Developers starting agent-assisted projects.
- Teams upgrading existing repositories for coding-agent use.
- Platform and security teams defining reusable rules and quality gates.
- Coding agents that need compact routing, scoped context, safe permissions, and verifiable completion criteria.

## Product

Agentic Harness provides:

1. A clean target-project contract with `AGENTS.md` as the root router and `.agentic/` as canonical project context.
2. A browsable catalog of complete project variants, packs, policies, profiles, presets, and schemas.
3. Agent-facing skills and prompts in `agentic-harness-agents`.
4. A native Rust `ah` CLI for initialization, migration, upgrades, audits, validation, ADR management, adapter synchronization, and quality gates.

## Non-goals

- Running or hosting autonomous agents.
- Replacing application frameworks, package managers, issue trackers, or CI systems.
- Making model output trustworthy without evidence and deterministic checks.
- Locking projects to one model vendor.

## Success criteria

- A new user understands the filesystem model from the root README and `.agentic/README.md`.
- `ah init` creates a self-contained project without source-only metadata leakage.
- Existing repositories migrate through an explicit dry-run and conflict-aware process.
- Repeated composition and adapter synchronization are idempotent.
- Audits distinguish deterministic evidence, agent-assisted judgment, and checks not performed.
- Release binaries work offline and embed pinned canonical sources.

## Current status

Beta. The target filesystem contract is versioned, but compatibility and migration behavior may evolve before 1.0.
