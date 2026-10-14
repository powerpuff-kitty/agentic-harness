# Ecosystem repositories

`agentic-harness` owns the project contract, catalog, policies, profiles, presets, and schemas. `skills` owns skills, prompts, adapters, and agent-only workflows. `agentic-harness-cli` owns deterministic composition, migration, validation, audit, and release binaries.

Changes flow from canonical contract to procedure and then to deterministic implementation. Compatibility changes must update source pins and tests explicitly.

The procedure repository was renamed from `agentic-harness-agents` to `skills`
without replacing its history, issues, tags or individual skill names. Use
`https://github.com/powerpuff-kitty/skills` for current source declarations.
Historical records and published archives may retain the previous name. Source
commit pins and installed checksums remain unchanged by the rename. See
[ADR-013](../../decisions/ADR-013-skills-repository-name.md).
