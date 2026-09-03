# Agentic App Boilerplate

A framework-neutral repository boilerplate for building software with coding agents such as Codex, Claude Code, Cursor, GitHub Copilot, and other agentic tools.

The core idea is simple: **the repository is the durable source of truth; the agent is an interchangeable worker.**

## Principles

1. Keep root agent instructions short and navigational.
2. Separate durable knowledge from task procedures.
3. Record architecture and product decisions explicitly.
4. Store examples of accepted work so agents can imitate real quality.
5. Convert deterministic rules into tests, linters, schemas, and CI checks.
6. Update repository knowledge when a decision changes.
7. Ask rather than invent when the source of truth is missing.

## Repository map

```text
.
├── AGENTS.md                 # Agent router / global instructions
├── CLAUDE.md                 # Claude-compatible entry point
├── ARCHITECTURE.md           # System architecture index
├── PRODUCT.md                # Product intent and constraints
├── DESIGN.md                 # Design-system index
├── SECURITY.md               # Security baseline
├── docs/
│   ├── architecture/         # Detailed architecture knowledge
│   ├── product/              # Product/domain knowledge
│   ├── design/               # Design rules and tokens
│   ├── decisions/            # ADRs / durable decisions
│   └── plans/                # Current execution plans
├── .agents/skills/           # Reusable task procedures
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

## Getting started

Replace the placeholders in `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, and `SECURITY.md` first. Then add project-specific skills under `.agents/skills/` and accepted examples under `examples/`.

Do **not** turn `AGENTS.md` into a giant handbook. It should remain a compact router to deeper, version-controlled knowledge.
