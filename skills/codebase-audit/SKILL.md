# Codebase Audit Skill

Use this skill to audit any software repository and produce evidence-backed scores, production-readiness findings, and prioritized remediation work.

## Modes

- `QUICK` — fast structural/static review. Do not run expensive checks.
- `STANDARD` — repository structure, code, docs, tests, security, dependencies, agent docs, CI/operations.
- `DEEP` — STANDARD plus dependency graph, test/build execution where safe, architecture review, threat-model review, operational readiness, and framework-specific checks.
- `COMPARE` — compare two revisions/audits and explain regressions/improvements.
- `GATE` — machine-readable CI policy; fail when configured minimums or no-regression rules are violated.

## Mandatory workflow

1. Inspect the repository before judging it. Detect languages, frameworks, package managers, apps/packages/services, tests, CI, deployment, data stores, and agent instruction files.
2. Classify the project type and target maturity. If not supplied, infer a likely target but label it as an assumption.
3. Gather deterministic evidence first. Use repository-native lint/typecheck/test/build/security tools when available and safe. Never weaken checks merely to make the audit pass.
4. Review the qualitative dimensions in `references/dimensions.md` using the scoring rules in `references/scoring.md`.
5. Separate `observed`, `inferred`, and `not_checked` evidence. Never fabricate coverage, vulnerability status, performance numbers, or CI results.
6. Score each applicable dimension 0–100. Mark dimensions `N/A` when genuinely irrelevant; do not reward absence.
7. Produce readiness for `prototype`, `startup`, `production`, and `critical` where useful.
8. Prioritize findings by severity, confidence, blast radius, and effort. Prefer a small number of high-leverage actions over a long generic checklist.
9. For agent-enabled repositories, audit `AGENTS.md`, vendor adapters, skills, packs, machine-readable policy, stale/conflicting docs, tool permissions, prompt-injection boundaries, and source-of-truth routing.
10. In `GATE` mode, emit JSON conforming to `schema/codebase-audit.schema.json` and apply configured thresholds.

## Default dimensions

- code quality
- maintainability
- architecture
- testing
- security
- performance
- dependency health
- documentation
- agent-doc compliance
- operational readiness

Project-specific dimensions may be added, but the default dimensions should stay comparable across audits.

## Evidence policy

A score without evidence is invalid. For each score, cite concrete files, commands, metrics, or observed patterns. Agent judgment may interpret evidence, but it must not replace it.

Examples of deterministic evidence include: lint/typecheck/test/build result, test count/coverage when available, dependency manifests/lockfiles, CI workflows, file/module size, TODO/FIXME counts, duplicated structures, schema/migration files, secret-scanning/SAST config, CODEOWNERS/branch policy, runbooks, ADRs, and agent-policy files.

## Production readiness

Production readiness is not the overall score. It is a separate judgment based on whether the repository has the controls required to operate safely in production: reliable tests/builds, security controls, deployment/rollback, observability, migrations/data safety, incident/runbook coverage, dependency/supply-chain hygiene, and maintained documentation.

Use `references/production-readiness.md`.

## Completion format

Return:

1. repository profile / detected stack
2. overall score and dimension scores
3. maturity/readiness scores
4. strongest areas
5. critical/high findings
6. what the project currently does well
7. what it lacks
8. production blockers
9. prioritized next actions
10. checks not performed / uncertainty

For machine-readable output follow `schema/codebase-audit.schema.json`.