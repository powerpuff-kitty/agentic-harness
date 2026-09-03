# Agentic App Boilerplate

A framework-neutral, composable development harness for coding agents such as Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other filesystem/tool-using agents.

**The repository is durable institutional memory; agents are interchangeable workers.**

This repo can be used in three ways:

- **Template** — start a new agent-native project.
- **Skill** — teach an agent to initialize, upgrade, or audit another repository.
- **Pack library** — compose domain/technical knowledge such as web, design system, SaaS, realtime, AI, mobile, PostgreSQL, and security-critical behavior.

## Skill modes

Ask an agent to use `skill/SKILL.md`.

```text
INIT    create the right harness for a new project
UPGRADE inspect an existing project and add only what is missing
AUDIT   read-only audit with score, gaps, conflicts, and recommended packs
```

INIT/UPGRADE are intentionally guided. The agent first inspects the repository, infers what it safely can, then asks only the unresolved high-impact questions. It should show the proposed configuration before applying policy/permission changes.

Example:

```text
Use the agentic-app skill in UPGRADE mode.
Inspect this repository first. Ask me only for decisions you cannot infer safely.
Propose the packs and permissions before modifying the harness.
```

## Architecture

```text
                         agentic-app
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
        CORE               PACKS              SKILLS
          │                  │                  │
  source-of-truth docs   knowledge modules   procedures
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ↓
                           AGENT
                    inspect → ask → plan
                             ↓
                     implement / review
                             ↓
                   tests + evals + audit
                             ↓
                  decisions/docs/examples
                             ↓
                    repository memory
```

## Core files

```text
AGENTS.md                 compact router and global rules
agentic.yaml              machine-readable resolved configuration
PRODUCT.md                product intent and constraints
ARCHITECTURE.md           system architecture index
DESIGN.md                 design source-of-truth index
REFERENCE.md              observed evidence / source material index
SECURITY.md               application + agent security baseline
docs/decisions/           ADRs / durable decisions
docs/plans/               implementation plans
docs/tasks/               persistent task state
docs/research/            source provenance
docs/data/                schemas and invariants
docs/testing/             test strategy
docs/operations/          deployment/runbooks/operations
.agents/skills/           reusable procedures
examples/                 accepted exemplars
evals/                    agent-output evaluation
packs/                    composable knowledge modules
skill/                    canonical portable skill
```

## Packs

Starter packs:

`web-app`, `design-system`, `backend-api`, `saas`, `mobile`, `ai-app`, `data-platform`, `realtime`, `security-critical`, `library-sdk`, `postgres`.

A pack is **knowledge and constraints**. A skill is **a repeatable procedure**. A template is **initial structure**. An exemplar is **what good looks like**. An eval is **how success is measured**.

The resolved pack set is stored in `agentic.yaml`.

## Guided setup

The skill follows:

```text
inspect repository
      ↓
detect stack / structure / docs / CI / design / tests
      ↓
separate detected facts from unresolved decisions
      ↓
ask minimal targeted questions
      ↓
recommend packs + maturity + permissions
      ↓
show proposed configuration
      ↓
apply after required approval
      ↓
audit generated harness
```

It must not ask "which framework?" when the repository already answers that question.

## Design systems

The design-system pack and skill organize UI knowledge as:

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

See `skill/references/design-system-ontology.md` and `docs/design/README.md`.

## Maturity

`prototype` → lightweight guardrails.

`startup` → ADRs, CI, migrations, observability/security basics.

`production` → runbooks, rollback, compatibility, performance/accessibility budgets, stronger security.

`critical` → threat models, recovery, auditability, strict permissions and review gates.

## Agent adapters

The canonical methodology lives in `skill/SKILL.md`. Agent-specific files should remain thin adapters:

- Codex/shared agents: `.agents/skills/agentic-app/SKILL.md` and `AGENTS.md`
- Claude Code: `CLAUDE.md` and `.claude/skills/agentic-app/SKILL.md`
- Cursor: `.cursor/rules/agentic-app.mdc`
- GitHub Copilot: `.github/copilot-instructions.md`
- Gemini CLI: `GEMINI.md`

Do not fork the methodology into contradictory agent-specific copies.

## Audit

Run locally:

```bash
python3 scripts/agentic_audit.py
```

The script emits a basic machine-readable audit and CI runs it on pushes/PRs. Agent-driven AUDIT mode goes further by evaluating content quality, contradictions, pack fit, stale docs, examples, security boundaries, and repository-specific gaps.

## Principle

Do not turn `AGENTS.md`, `CLAUDE.md`, or a giant prompt into the whole knowledge base. Keep entry points short and route agents to small, version-controlled sources of truth.
