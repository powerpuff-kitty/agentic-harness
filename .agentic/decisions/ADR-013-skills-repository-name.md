# ADR-013: Rename the procedure repository to skills

- Status: accepted
- Date: 2026-10-14
- Deciders: project owner
- Supersedes: none

## Context

The existing `agentic-harness-agents` name obscured the repository's reusable
skill collection. The owner accepted a dedicated `skills` repository name.

## Decision

Rename the existing repository to `powerpuff-kitty/skills`, preserving its history,
issues and tags. Keep canonical contracts in `agentic-harness`, reusable skills,
prompts and skill adapters in `skills`, and deterministic mechanics in
`agentic-harness-cli`. This updates the repository name used by ADR-001 and ADR-004
without changing their truth/procedure separation.

Update current documentation, template attribution and source declarations. Retain
historical records and published release assets. Source commit pins and installed
skill bytes remain unchanged. Adapter provenance accepts both repository names so
existing receipts remain valid.

## Alternatives

Keep the old name, or create a replacement repository. Renaming clarifies ownership
while preserving repository continuity.

## Consequences

Downstream tooling uses the new URL. Historical pins remain reproducible because
the existing repository and commits are retained. The rename alone does not refresh
project-local skill copies or host plugin imports and publishes no new release.
