# Agentic Harness Architecture

Agentic Harness separates canonical project knowledge, agent behavior, and deterministic tooling into three repositories.

```text
┌──────────────────────────────────────────┐
│ agentic-harness                          │
│ canonical catalog                        │
│ root boilerplates · modules · schemas    │
└───────────────────┬──────────────────────┘
                    │ source of truth
          ┌─────────┴─────────┐
          ▼                   ▼
┌──────────────────┐  ┌────────────────────┐
│ harness-agents   │  │ harness-cli        │
│ skills/prompts   │  │ Rust `ah`          │
│ adapters         │  │ audit/validation   │
│ workflows        │  │ composition/gates │
└──────────────────┘  └────────────────────┘
```

## Repository role

This repository is deliberately static and easy to browse. Its root directories are the canonical boilerplates:

```text
base/
web-app/
backend-api/
saas/
monorepo/
library-sdk/
```

Shared cross-boilerplate material lives under `modules/`:

```text
modules/
├── packs/
├── policies/
└── profiles/
```

`presets/` provides named compositions and `schema/` defines machine-readable contracts. `docs/` explains decisions and compatibility without becoming another source of project structure.

## Authority

1. `agentic-harness` owns durable architecture, boilerplates, modules, presets, and schemas.
2. `agentic-harness-agents` owns procedures for agents using that truth.
3. `agentic-harness-cli` owns deterministic mechanics, composition, audits, and enforcement.

Prompts must not silently redefine canonical architecture, and CLI implementation details are not the canonical explanation of a boilerplate or policy.

## Project overlay model

```text
project
+ boilerplate
+ packs
+ policies
+ profile
+ selected skills
+ deterministic checks
= agent-native governed project
```

Generated repositories are self-contained. These three repositories are authoring and distribution sources, not runtime dependencies of the generated application.
