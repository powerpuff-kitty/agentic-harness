# Agentic App Boilerplate

A framework-neutral, composable development harness for coding agents such as Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other filesystem/tool-using agents.

**The repository is durable institutional memory; agents are interchangeable workers.**

The source repository is intentionally split into clean building blocks:

```text
.
├── README.md
├── templates/              project skeletons
│   └── base/
├── skills/                 reusable agent procedures
│   ├── agentic-app/
│   ├── codebase-audit/
│   ├── design-system/
│   ├── implementation-plan/
│   ├── product-design/
│   ├── release-review/
│   └── security-review/
├── packs/                  composable technical/domain knowledge
├── schema/                 machine-readable contracts
├── scripts/                deterministic tooling/audits
├── tests/                  tests for deterministic tooling
└── .github/workflows/      CI for this source repository
```

This separation is deliberate: **templates are files to compose into a target project; skills are procedures an agent can install/use; packs are knowledge and constraints.**

## Agentic-app skill

Use `skills/agentic-app/SKILL.md`.

```text
INIT    create the right harness for a new project
UPGRADE inspect an existing project and add only what is missing
AUDIT   read-only audit with score, gaps, conflicts, and recommended packs
```

INIT/UPGRADE first inspect the repository, infer what they safely can, ask only unresolved high-impact questions, resolve maturity/packs/permissions, show the proposed setup when appropriate, then compose the target repository.

Example:

```text
Use skills/agentic-app/SKILL.md in UPGRADE mode.
Inspect this repository first. Ask me only for decisions you cannot infer safely.
Propose the packs and permissions before modifying the harness.
```

## Composition model

```text
templates/base/
      +
selected packs/
      +
selected skills/
      +
project-specific answers
      ↓
resolved target repository
      ↓
AGENTS.md + agentic.yaml + docs + installed skills + examples + evals
```

The target project should be self-contained. The generated files must not depend on paths back into this source repository unless a linked installation was explicitly requested.

## Base template

`templates/base/` contains the framework-neutral project structure: `AGENTS.md`, `agentic.yaml`, product/architecture/design/security sources of truth, evidence/reference docs, detailed `docs/`, examples, evals, and agent entry-point adapters. `templates/base/skills.manifest.yaml` declares default and optional reusable skills; the setup skill chooses what to install based on the actual project.

## Skills

- `agentic-app` — INIT / UPGRADE / AUDIT orchestration, guided setup, maturity, permissions, security, provenance and pack resolution.
- `codebase-audit` — QUICK / STANDARD / DEEP / COMPARE / GATE audits with evidence-backed scores for code quality, maintainability, architecture, tests, security, performance, dependencies, documentation, agent docs, operations, and production readiness.
- `design-system` — extract and organize design evidence, tokens, foundations, layouts, components, patterns and checks.
- `implementation-plan` — durable execution planning for larger changes.
- `product-design` — product/UI design procedure.
- `release-review` — completion/release review.
- `security-review` — security-sensitive change review.

Agent-specific adapters for the portable agentic-app skill live under `skills/agentic-app/adapters/` rather than polluting the repository root.

## Packs

Starter packs include `web-app`, `design-system`, `backend-api`, `saas`, `mobile`, `ai-app`, `data-platform`, `realtime`, `security-critical`, `library-sdk`, and `postgres`.

A pack is **what the agent needs to know**. A skill is **how the agent performs a repeatable task**. A template is **initial shape**. An exemplar is **what good looks like**. An eval is **how success is measured**.

## Design systems

The design-system pack/skill use:

```text
evidence
  ↓
primitive tokens
  ↓
semantic tokens
  ↓
component tokens
  ↓
foundations / layouts / components / patterns
  ↓
examples + visual/a11y validation
```

See `skills/agentic-app/references/design-system-ontology.md` and the design docs under `templates/base/docs/design/`.

## Security

Security is part of the core harness, including prompt injection, indirect prompt injection, tool permissions, secret handling, data exfiltration, unsafe generated-code execution, untrusted retrieval, destructive-action approval, agent memory, confused-deputy risks, least privilege and security-sensitive review gates.

See `templates/base/SECURITY.md`, `skills/agentic-app/references/security-for-agents.md`, the `security-review` skill, and the `security-critical` pack.

## Audits

Structural agent-harness audit:

```bash
python3 scripts/agentic_audit.py templates/base
```

Baseline codebase-quality audit of any local repository:

```bash
python3 scripts/codebase_audit.py /path/to/project
```

For deeper evidence-backed review, use `skills/codebase-audit/SKILL.md`. Its modes include QUICK, STANDARD, DEEP, COMPARE and GATE. Machine-readable results use `schema/codebase-audit.schema.json`.

The baseline scripts intentionally do not pretend to have executed tests, vulnerability scanners, coverage, benchmarks, or deployment checks when those checks were not actually run.

## Principle

Do not turn `AGENTS.md`, `CLAUDE.md`, or one giant prompt into the knowledge base. Keep entry points short and route agents to small, version-controlled sources of truth.
