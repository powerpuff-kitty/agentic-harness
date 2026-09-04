# Agentic Harness

[![Status: Beta](https://img.shields.io/badge/status-beta-orange)](.agentic/PRODUCT.md#current-status)
[![Catalog validation](https://github.com/powerpuff-kitty/agentic-harness/actions/workflows/content-validation.yml/badge.svg)](https://github.com/powerpuff-kitty/agentic-harness/actions/workflows/content-validation.yml)
[![Agent native](https://img.shields.io/badge/agent--native-AGENTS.md-5c6ac4)](AGENTS.md)

A clean, vendor-neutral project contract for Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other coding agents.

Agentic Harness keeps a project root readable: normal project files stay where developers expect them, `AGENTS.md` is the compact agent entrypoint, and durable product/architecture/security context lives under `.agentic/`.

> **Beta:** the filesystem contract is versioned and migration-aware, but schemas and CLI behavior may still evolve before 1.0.

## Start here

This repository is both:

1. **A complete working reference installation** under [`.agentic/`](.agentic/README.md).
2. **The canonical authoring catalog** under [`catalog/`](catalog/README.md).

```text
agentic-harness/
├── README.md                    human landing page
├── AGENTS.md                    compact agent router
├── normal repository files
│
├── .agentic/                    this project's canonical context
│   ├── README.md                annotated map and precedence
│   ├── manifest.yaml            machine-readable configuration
│   ├── lock.json                source/module resolution
│   ├── PRODUCT.md               product truth
│   ├── ARCHITECTURE.md          current architecture
│   ├── SECURITY.md              security model
│   ├── DESIGN.md                documentation/design truth
│   ├── REFERENCE.md             evidence and provenance
│   ├── decisions/               durable ADR history
│   ├── plans/                   temporary strategies
│   ├── tasks/                   active execution state
│   ├── docs/                    supporting documentation
│   ├── evals/                   quality rubrics
│   ├── packs/                   installed knowledge modules
│   └── policies/                installed mandatory rules
│
├── catalog/                     reusable authoring source
│   ├── variants/                complete project structures
│   ├── packs/                   reusable knowledge + constraints
│   ├── policies/                mandatory rules
│   ├── profiles/                organization/team defaults
│   ├── presets/                 named compositions
│   └── schema/                  public machine contracts
│
└── .github/                     repository automation/adapters
```

Opening [`.agentic/README.md`](.agentic/README.md) explains when to read and update every path. The key lifecycle is:

```text
research / evidence
        ↓
ADR records why a durable decision was accepted
        ↓
current truth describes the resulting system
        ↓
plan describes temporary implementation strategy
        ↓
task tracks active execution
        ↓
implementation + validation
```

## Complete boilerplates

Every catalog variant contains a complete, materialized target tree under `files/`; no hidden overlay composition is required to understand it.

| Variant | Use it for |
| --- | --- |
| [`base`](catalog/variants/base/) | Minimal agent-native project contract |
| [`web-app`](catalog/variants/web-app/) | User-facing web applications and design systems |
| [`backend-api`](catalog/variants/backend-api/) | APIs and deployed services |
| [`saas`](catalog/variants/saas/) | Multi-user SaaS products and tenant isolation |
| [`monorepo`](catalog/variants/monorepo/) | Multi-application/package repositories |
| [`library-sdk`](catalog/variants/library-sdk/) | Public or internal libraries and SDKs |

## Quick start with `ah`

The native Rust CLI lives in [`agentic-harness-cli`](https://github.com/powerpuff-kitty/agentic-harness-cli).

```bash
ah init ./my-app --boilerplate web-app
ah doctor ./my-app
ah new adr "Choose the primary database" --target ./my-app
ah audit ./my-app
```

For an existing legacy installation:

```bash
ah migrate ./existing-project
ah migrate ./existing-project --apply --backup .agentic-migration-backup
ah validate ./existing-project
```

Migration defaults to dry-run and reports identical duplicates separately from conflicts.

## Repository responsibilities

```text
agentic-harness
what is true: project contract, variants, packs, policies, profiles, presets, schemas
        ↓
agentic-harness-agents
what agents should do: skills, prompts, adapters, agent workflows
        ↓
agentic-harness-cli
how it is applied and checked: native composition, migration, audit, validation
```

- [Agent procedures and prompts](https://github.com/powerpuff-kitty/agentic-harness-agents)
- [Native Rust CLI](https://github.com/powerpuff-kitty/agentic-harness-cli)

## Why `.agentic/` and `.agents/` are separate

- `.agentic/` is project-owned truth, governance, provenance, and state.
- `.agents/` contains reusable agent procedures such as installed skills.

Skills can explain how to work but cannot silently redefine project truth or policy.

## Contributions

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md), the relevant ADR/current truth, and catalog validation. Good contributions include clearer schemas, safer migration fixtures, additional deterministic checks, improved agent procedures in the agents repository, and narrowly scoped project variants.
