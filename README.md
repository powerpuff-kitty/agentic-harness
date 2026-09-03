# Agentic Harness

A readable catalog of canonical agent-native project boilerplates and the reusable modules that compose them.

This repository owns **project structure and architecture truth**. Agent procedures live in [`agentic-harness-agents`](https://github.com/powerpuff-kitty/agentic-harness-agents). Deterministic tooling lives in [`agentic-harness-cli`](https://github.com/powerpuff-kitty/agentic-harness-cli).

## Catalog

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

Each boilerplate has a `boilerplate.json` describing inheritance, defaults, and metadata. Child boilerplates may extend another catalog entry (for example `saas` extends `web-app`).

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

## Canonical-source rule

```text
agentic-harness          what is true
        ↓
agentic-harness-agents   what agents should do
        ↓
agentic-harness-cli      how it is applied and checked
```

Architecture changes land here first. The agents and CLI repositories then pin and consume an accepted revision of this repository.

## Examples

This repository intentionally does not contain demo applications. If complete reference apps are maintained later, they should live in a separate examples repository so this catalog remains focused.
