# Agentic Harness Architecture

Agentic Harness separates canonical project knowledge, agent behavior, and deterministic tooling into three repositories.

```text
┌──────────────────────────────────────────┐
│ agentic-harness                          │
│ canonical static source                  │
│ templates · packs · policies · profiles  │
│ presets · schemas · examples · docs      │
└───────────────────┬──────────────────────┘
                    │ source of truth
          ┌─────────┴─────────┐
          ▼                   ▼
┌──────────────────┐  ┌────────────────────┐
│ harness-agents   │  │ harness-cli        │
│ skills/prompts   │  │ Rust `ah`          │
│ adapters         │  │ audit/validation   │
│ agent workflows  │  │ composition/gates │
└──────────────────┘  └────────────────────┘
```

## Authority

1. This repository owns durable architecture and project-shape truth.
2. `agentic-harness-agents` owns procedures for agents using that truth.
3. `agentic-harness-cli` owns deterministic mechanics and enforcement.

Prompts are never allowed to silently redefine canonical architecture. CLI implementation details are never the canonical explanation of a template or policy.

## Project overlay model

Agentic Harness sits on top of an application rather than replacing its framework or source tree:

```text
project
+ template
+ packs
+ policies
+ profile
+ selected skills
+ deterministic evals / audit
= agent-native governed project
```

Generated repositories should be self-contained. External Agentic Harness repositories are authoring/distribution sources, not runtime dependencies of the resulting application.
