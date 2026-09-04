# Agentic Harness

[![Status: Beta](https://img.shields.io/badge/status-beta-orange)](https://github.com/powerpuff-kitty/agentic-harness)
[![Catalog validation](https://github.com/powerpuff-kitty/agentic-harness/actions/workflows/content-validation.yml/badge.svg)](https://github.com/powerpuff-kitty/agentic-harness/actions/workflows/content-validation.yml)

**Agent-native boilerplates and repository architecture for Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other filesystem/tool-using coding agents.**

Agentic Harness provides readable project boilerplates, reusable knowledge modules, policies, profiles, schemas, and deterministic tooling for building agent-native software repositories without making prompts the source of truth.

> **Status: Beta.** The canonical repository model is usable for real projects. Public schemas and CLI behavior may still evolve before 1.0.

## Works with

- OpenAI Codex
- Claude Code
- Cursor
- GitHub Copilot
- Gemini CLI
- other coding agents that can read repository files and use development tools

## Ecosystem

```text
agentic-harness          what is true
        ↓
agentic-harness-agents   what agents should do
        ↓
agentic-harness-cli      how it is applied and checked
```

- **This repository:** canonical architecture, boilerplates and reusable modules
- **[agentic-harness-agents](https://github.com/powerpuff-kitty/agentic-harness-agents):** skills, prompts, workflows and agent adapters
- **[agentic-harness-cli](https://github.com/powerpuff-kitty/agentic-harness-cli):** native Rust `ah` CLI, audits, validation and quality gates

## Boilerplate catalog

The boilerplates are intentionally at the repository root so they are the first thing you see:

```text
agentic-harness/
├── base/              minimal agent-native foundation
├── web-app/           user-facing web application
├── backend-api/       API / service repository
├── saas/              multi-user SaaS product
├── monorepo/          multi-app / package repository
├── library-sdk/       public library or SDK
│
├── modules/
│   ├── packs/         reusable knowledge + constraints
│   ├── policies/      mandatory rules
│   └── profiles/      team / organization defaults
│
├── presets/           named machine-readable compositions
├── schema/            public machine contracts
├── docs/              architecture and compatibility guidance
├── ARCHITECTURE.md
└── CONCEPTS.md
```

Start with [`base/`](base), [`web-app/`](web-app), [`backend-api/`](backend-api), [`saas/`](saas), [`monorepo/`](monorepo), or [`library-sdk/`](library-sdk).

Each boilerplate is a complete, directly browsable project starting structure with a `boilerplate.json` describing its metadata and defaults.

## Composition model

```text
boilerplate
+ modules/packs
+ modules/policies
+ modules/profiles
+ preset defaults
+ skills from agentic-harness-agents
        ↓
self-contained project harness
```

A **boilerplate** is the starting project shape. A **preset** selects a boilerplate and common modules for a recognizable stack or posture. Packs, policies, and profiles are reusable across boilerplates rather than duplicated inside them.

## Why Agentic Harness

Coding agents are increasingly capable, but repository guidance often ends up fragmented across prompts, vendor-specific instruction files, and undocumented assumptions. Agentic Harness separates durable project truth from agent procedure and deterministic enforcement:

```text
architecture / policy / product truth
                ↓
        reusable agent skills
                ↓
      tests / schemas / CI / ah
```

This keeps important decisions reviewable by humans and reusable across different agents.

## Canonical-source rule

Architecture changes land here first. The agents and CLI repositories then pin and consume an accepted revision of this repository. Prompts are procedures, not architectural authority.

## Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — ecosystem and repository model
- [`CONCEPTS.md`](CONCEPTS.md) — boilerplate/module vocabulary
- [`docs/`](docs) — composition, compatibility, security and release guidance
- [`schema/`](schema) — machine-readable public contracts

## Examples

This repository intentionally does not contain demo applications. Complete reference apps can live in a separate examples repository later so this catalog remains focused.

## Contributing

Issues and pull requests are welcome while the project is in beta. Small reproducible improvements to boilerplates, schemas, documentation and compatibility are especially useful.
