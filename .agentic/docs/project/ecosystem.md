# Ecosystem repositories

`agentic-harness` owns the project contract, catalog, policies, profiles, presets, and schemas. `skills` contains only `skills/<name>/` directories with self-contained procedures and their local references, helpers, assets, tests and licenses. `agentic-harness-cli` owns deterministic composition, migration, validation, audit, and release binaries.

Changes flow from canonical contract to procedure and then to deterministic implementation. Compatibility changes must update source pins and tests explicitly.

The procedure repository was renamed from `agentic-harness-agents` to `skills`
without replacing its history, issues, tags or individual skill names. Use
`https://github.com/powerpuff-kitty/skills` for current source declarations.
Historical records and published archives may retain the previous name. Source
commit pins and installed checksums remain unchanged by the rename. See
[ADR-013](../../decisions/ADR-013-skills-repository-name.md).

The skills source has no collection-level project context, prompts, plugin manifests,
CI/release workflows or packaging scripts. Host adapter templates belong to the
`adapter-sync` skill. Whole-collection plugin imports are available only from the
historical versions that shipped them; current installs copy individual skill
folders. See [ADR-014](../../decisions/ADR-014-skill-folders-only.md).
