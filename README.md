# Agentic App Boilerplate

A framework-neutral starter **and portable skill pack** for building software with coding agents such as Codex, Claude Code, Cursor, GitHub Copilot, Gemini, and other agentic tools.

The core idea is simple: **the repository is the durable source of truth; the agent is an interchangeable worker.**

## What this repository can do

It supports three modes:

- **INIT** — bootstrap a new agent-native repository.
- **UPGRADE** — adapt an existing application without erasing its existing knowledge or conventions.
- **AUDIT** — review an existing repository's agent architecture and identify missing, duplicated, stale, or conflicting guidance.

The canonical reusable procedure lives in `skill/SKILL.md`.

## Principles

1. Keep root agent instructions short and navigational.
2. Separate durable knowledge from task procedures.
3. Record architecture and product decisions explicitly.
4. Store examples of accepted work so agents can imitate real quality.
5. Convert deterministic rules into tests, linters, schemas, and CI checks.
6. Update repository knowledge when a decision changes.
7. Ask rather than invent when the source of truth is missing.
8. Keep vendor-specific files as thin adapters around shared project truth.

## Repository map

```text
.
├── AGENTS.md                 # Shared agent router / global instructions
├── CLAUDE.md                 # Claude entry point
├── GEMINI.md                 # Gemini entry point
├── ARCHITECTURE.md           # System architecture index
├── PRODUCT.md                # Product intent and constraints
├── DESIGN.md                 # Design-system index
├── SECURITY.md               # Security baseline
├── skill/
│   ├── SKILL.md              # Canonical INIT / UPGRADE / AUDIT procedure
│   └── references/
│       └── audit-checklist.md
├── docs/
│   ├── architecture/         # Detailed architecture knowledge
│   ├── product/              # Product/domain knowledge
│   ├── design/               # Design rules and tokens
│   ├── decisions/            # ADRs / durable decisions
│   └── plans/                # Current execution plans
├── .agents/skills/           # Codex/shared reusable procedures
│   └── agentic-app/SKILL.md  # Adapter to canonical skill
├── .claude/skills/
│   └── agentic-app/SKILL.md  # Claude Code adapter
├── .cursor/rules/
│   └── agentic-app.mdc       # Cursor adapter
├── examples/                 # Accepted examples / exemplars
├── evals/                    # Agent-output evaluation fixtures
└── .github/
    └── copilot-instructions.md
```

## How an agent should use this repository

```text
User task
   ↓
AGENTS.md
   ↓
Load only relevant knowledge
   ├── PRODUCT.md / docs/product
   ├── ARCHITECTURE.md / docs/architecture
   ├── DESIGN.md / docs/design
   ├── SECURITY.md
   └── docs/decisions
   ↓
Load relevant SKILL.md procedure
   ↓
Inspect examples
   ↓
Implement
   ↓
Run deterministic checks + evals
   ↓
Update docs/decisions when durable knowledge changed
```

## Use it as a project template

Clone or use this repository as the base for a new project, then replace the placeholders in `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, and `SECURITY.md`. Add project-specific skills under `.agents/skills/` and accepted examples under `examples/`.

Do **not** turn `AGENTS.md` into a giant handbook. It should remain a compact router to deeper, version-controlled knowledge.

## Use it as a skill

Point your coding agent at `skill/SKILL.md` and ask for one of the three modes.

Examples:

```text
Use the agentic-app skill in INIT mode and make this repository agent-native.
```

```text
Use the agentic-app skill in UPGRADE mode. Preserve all existing conventions and add only missing agent architecture.
```

```text
Use the agentic-app skill in AUDIT mode. Do not modify files; return the audit report and recommended next actions.
```

The adapter files under `.agents/`, `.claude/`, `.cursor/`, and `GEMINI.md` intentionally remain thin so the same rules do not drift between tools.

## Cross-agent model

```text
                        skill/SKILL.md
                              │
                 canonical procedure + rules
                              │
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
       Codex               Claude              Cursor
 .agents/skills/...   .claude/skills/...   .cursor/rules/...
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ↓
                       project knowledge
                 AGENTS / PRODUCT / ARCHITECTURE
                    DESIGN / SECURITY / docs
```

The goal is not to make every agent use identical vendor-specific syntax. The goal is to make every agent consume the **same durable project truth**.
