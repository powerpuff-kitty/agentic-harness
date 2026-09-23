# Changelog

## Unreleased

- Added AgentConnection v2 with explicit capability support, repository/tool access, credential references, readiness evidence, usage/rate-limit observations, continuation modes, and deterministic WorkAction eligibility checks while retaining v1 compatibility.

- Added WorkAction v2 with approval state, parent/root lineage, produced-result references, and chained audit/remediate/reassess validation while retaining v1 compatibility.

- Added Architecture Graph v1, a language-neutral capability/contract/provider/adapter model with semantic dependency validation and explicit declaration/check/enforcement states.

- License authored content under MIT and retain copied Harness attribution without licensing generated application code.

- Continue beta validation, migration fixtures, release hardening, and ecosystem compatibility work.

## 0.3.0-beta.1 - 2026-09-04

- Made `agentic-harness` a self-hosting complete reference installation.
- Standardized target projects on root `AGENTS.md` plus canonical `.agentic/` context.
- Added manifest and lockfile contracts, first-class ADRs, plans, tasks, docs, evals, packs, and policies.
- Moved reusable content under `catalog/` and published complete materialized variants.
- Added real architecture decisions, migration guidance, stronger catalog validation, and new schemas.
- Defined explicit compatibility, precedence, root-hygiene, adapter, and migration-safety rules.

## 0.2.0 - 2026-09-03

- Added evidence-backed codebase auditing and production-readiness scoring.
- Added design-system component planning and compliance checks.
- Split canonical content, agent procedures, and Rust tooling into three repositories.

## 0.1.0 - 2026-09-03

- Initial agent-native boilerplates, packs, skills, design-system ontology, security model, and guided workflows.
