# Ecosystem repositories

`agentic-harness` owns the project contract, catalog, policies, profiles, presets, and schemas. `agentic-harness-agents` owns skills, prompts, adapters, and agent-only workflows. `agentic-harness-cli` owns deterministic composition, migration, validation, audit, and release binaries.

Changes flow from canonical contract to procedure and then to deterministic implementation. Compatibility changes must update source pins and tests explicitly.
