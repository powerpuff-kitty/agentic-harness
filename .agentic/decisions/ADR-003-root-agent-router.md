# ADR-003: Keep `AGENTS.md` as the root router

- Status: accepted
- Date: 2026-09-04
- Deciders: project maintainer
- Supersedes: none
- Superseded by: none

## Context

Coding agents need an immediately discoverable entrypoint, while large always-on instruction files waste context and become stale duplicates.

## Decision

Keep a compact root `AGENTS.md` that points to `.agentic/README.md`, `.agentic/manifest.yaml`, and relevant context. Vendor adapters point to this router instead of duplicating canonical content.

## Consequences

Agents receive a stable entrypoint and load only relevant context. The router and manifest paths become part of the compatibility contract and must be audited.

## Verification

`ah doctor` and `ah audit` validate router targets and adapter thinness. `ah sync-adapters` produces deterministic adapter content.
