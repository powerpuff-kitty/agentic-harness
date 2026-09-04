# ADR-002: Store canonical project context under `.agentic/`

- Status: accepted
- Date: 2026-09-04
- Deciders: project maintainer
- Supersedes: legacy root-level context layout
- Superseded by: none

## Context

Placing `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, `SECURITY.md`, `REFERENCE.md`, plans, tasks, decisions, and evals at repository root polluted existing projects and created naming collisions.

## Decision

Keep canonical Agentic Harness project context under `.agentic/`. Reserve `.agents/` for installed reusable procedures. Normal project files remain in their conventional locations.

## Consequences

The harness is obvious, grouped, and removable. Tooling must route through a manifest and support migration from legacy root paths. Vendor-required adapters may remain outside `.agentic/` but must be thin.

## Verification

Catalog variants, generated projects, audits, and migration tests enforce the directory contract and reject duplicate canonical truth.
