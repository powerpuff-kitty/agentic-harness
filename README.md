# Agentic App Boilerplate

A framework-neutral, composable development harness for coding agents such as Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other filesystem/tool-using agents.

**The repository is durable institutional memory; agents are interchangeable workers.**

The source repository is split into `templates/` (generated project shape), `skills/` (repeatable agent procedures), `packs/` (knowledge/constraints), `schema/` (machine contracts), `scripts/` (deterministic tooling), and `tests/`.

## CLI

The repository now includes a deterministic composition/audit CLI:

```bash
python3 scripts/agentic.py init ./my-app --name my-app --maturity production --pack web-app --pack postgres
python3 scripts/agentic.py upgrade ./existing-app --pack design-system --skill codebase-audit
python3 scripts/agentic.py audit ./existing-app > audit.json
python3 scripts/agentic.py compare before.json after.json
python3 scripts/agentic.py gate audit.json --min-overall 80 --min-score security=80
```

`INIT` refuses a non-empty target unless explicitly allowed. `UPGRADE` preserves existing files and only fills missing template files, while explicitly selected packs/skills are installed into `.agentic/packs/` and `.agents/skills/` so the target remains self-contained.

## Agentic-app skill

Use `skills/agentic-app/SKILL.md` for guided `INIT`, `UPGRADE`, and agent-driven `AUDIT`. It inspects first, asks only unresolved high-impact questions, resolves maturity/packs/permissions, and preserves project-specific truth.

## Codebase audit

Use `skills/codebase-audit/SKILL.md` for QUICK/STANDARD/DEEP/COMPARE/GATE review. The deterministic baseline is `scripts/codebase_audit.py`; machine output follows `schema/codebase-audit.schema.json`. Scores are evidence-backed and explicitly separate performed checks from unverified areas.

## Design systems

The design-system pack/skill organizes evidence into primitive → semantic → component tokens, then foundations, layouts, components, patterns, examples, anti-patterns, and visual/accessibility checks.

## Security

Security covers both application and agent threats: prompt injection, excessive tool permissions, secret exfiltration, confused-deputy behavior, unsafe generated code, untrusted retrieval, agent memory, destructive actions, least privilege, and supply-chain review. See root `SECURITY.md`, `templates/base/SECURITY.md`, `skills/agentic-app/references/security-for-agents.md`, and `packs/security-critical/`.

CI compiles tooling, runs unit tests, validates module/template shape, audits the base template, and performs a scheduled high-signal secret scan. The repository still benefits from GitHub branch protection/rules requiring these checks; see `docs/branch-protection.md`.

## Versioning

Framework releases use semantic versioning. Template, skill, and pack module versions are indexed in `templates/base/template.json`, `skills/manifest.json`, and `packs/manifest.json`. See `VERSIONING.md` and `docs/compatibility.md`.

## Repository shape

```text
.
├── README.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── VERSIONING.md
├── templates/base/
├── skills/
├── packs/
├── schema/
├── scripts/
├── tests/
├── docs/
└── .github/workflows/
```

## Principle

Do not turn `AGENTS.md`, `CLAUDE.md`, or one giant prompt into the knowledge base. Keep entry points short and route agents to small, version-controlled sources of truth. Generated repositories must be self-contained and must not silently replace project-specific decisions with boilerplate.
