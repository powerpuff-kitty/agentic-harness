# ADR-001: Separate canonical, agent, and CLI repositories

- Status: accepted
- Date: 2026-09-03
- Deciders: project maintainer
- Supersedes: none
- Superseded by: none

## Context

Canonical project structures, agent procedures, and a compiled deterministic CLI have different responsibilities, release cadences, and trust boundaries. Keeping them together made the source harder to browse and caused Markdown changes to require binary-oriented repository structure.

## Decision

Use three repositories: `agentic-harness` for canonical truth and authoring content; `agentic-harness-agents` for skills/prompts/adapters; and `agentic-harness-cli` for Rust mechanics and enforcement. The CLI pins and embeds accepted revisions of the first two.

## Consequences

The main repository becomes readable and vendor-neutral. Source compatibility must be explicit across repositories, and coordinated changes require pinned revisions and cross-repository CI.

## Verification

Each repository README states its ownership boundary. CLI lock data identifies exact upstream revisions, and CI checks the pinned sources.
