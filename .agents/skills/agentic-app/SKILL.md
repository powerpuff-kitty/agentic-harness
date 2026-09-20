---
name: agentic-app
description: "Initialize, upgrade, migrate, or broadly audit a repository using the Agentic Harness project contract and selected catalog modules. Use when the requested job spans overall harness setup or lifecycle rather than one specialist procedure. Do not use for a focused readiness score, a standalone legacy migration, or a single domain review when a narrower skill owns the task."
---
# Agentic App

## Objective

Orchestrate the end-to-end Agentic Harness lifecycle while delegating specialist work to narrower skills and deterministic operations that are actually available in the target environment.

## Inputs

Required: target repository and requested mode (`init`, `upgrade`, `migrate`, or broad audit). Optional: project type, maturity, stack constraints, profile/preset, packs, policies, skills, design posture, installed tooling/capabilities, and approval boundaries.

## Context

Resolve the current contract/catalog from `agentic-harness`. In a target project, route from root `AGENTS.md` to `.agentic/manifest.yaml` and task-relevant truth. Follow `references/repository-discovery.md`, `references/context-engineering.md`, and progressive disclosure.

## Procedure

1. Inspect the target before asking for facts the repository can answer.
2. Resolve only missing high-impact choices and state consequential assumptions.
3. Select the canonical variant/preset/profile plus modules and skills.
   When supported by the installed CLI, select `--context-profile minimal|full` separately from organization profiles. Omission preserves an existing selection and uses full for a new project. Consult the canonical context-selection contract; never maintain a competing file allowlist here. Minimal retains required truth, attribution and selected-module contents; it does not authorize pruning existing files. Reconcile reported map conflicts and preserve custom or explicitly null routes when changing modes. Treat template prompts as unresolved decisions and keep structure installed, project configured, checks configured and behavior verified separate.
4. Prefer deterministic composition, migration, validation, analysis, and audit when the installed CLI/version actually exposes the required capability. Do not assume planned commands exist; inspect help/version/manifests or use a documented artifact/manual fallback.
5. Preserve project-authored truth and accepted ADRs during upgrades/migration; surface conflicts rather than silently selecting a newer source.
6. Route specialist security, model-fit, ADR, release, and domain work to the appropriate narrower skill.
7. When design work spans multiple stages, route through `design-intelligence` for Analyze → Preserve → Compile → Verify. A broad lifecycle request must not bypass candidate-to-approved Design Genome review gates.
8. Verify root hygiene, router links, manifest/lock integrity, native tests, relevant quality gates, and exact checks skipped because a capability/provider was unavailable.

When an installed CLI supports `checks complete`, follow the canonical completion contract. Obtain explicit caller review of the exact evidence manifest binding report, producer and reference digests; never calculate and supply approval automatically for arbitrary project evidence. Keep execution approval separate. Report the verdict scope and trust mode, retain producer authentication as unverified, and do not turn declared-check/control acceptance into whole-project readiness. Missing, stale, mismatched or rejected evidence keeps completion unverified.

## Output

Return resolved composition or audit scope, files/modules affected, delegated skills, assumptions, deterministic command/capability results, artifact/manual fallbacks used, conflicts, approvals, and remaining risks.

## Completion

The requested lifecycle operation is complete and repeatable, canonical truth is preserved, installed sources are locked, available checks pass, unavailable capabilities are not fabricated, design approval gates are preserved when relevant, and unresolved decisions or skipped validation are explicit.
