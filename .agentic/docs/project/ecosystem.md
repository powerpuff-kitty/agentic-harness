# Ecosystem repositories

`agentic-harness` owns the project contract, catalog, policies, profiles, presets, and schemas. `skills` contains self-contained `<name>/` directories directly at its root, each owning its procedure, local resources and license. `README.md` introduces the catalog and `INSTALL.md` provides installation guidance. `agentic-harness-cli` owns deterministic composition, migration, validation, audit, and release binaries.

Changes flow from canonical contract to procedure and then to deterministic implementation. Compatibility changes must update source pins and tests explicitly.

The procedure repository was renamed from `agentic-harness-agents` to `skills`
without replacing its history, issues, tags or individual skill names. Use
`https://github.com/powerpuff-kitty/skills` for current source declarations.
Historical records and published archives may retain the previous name. Source
commit pins and installed checksums remain unchanged by the rename. See
[ADR-013](../../decisions/ADR-013-skills-repository-name.md).

Beyond its README and installation prompt, the skills source has no collection-level
project context, plugin manifests, CI/release workflows or packaging scripts. Host adapter templates belong to the
`adapter-sync` skill. Whole-collection plugin imports are available only from the
historical versions that shipped them; current installs copy individual skill
folders. OpenCode uses native SKILL.md discovery; installation places those folders
in the supported host/project skill location rather than transforming their format. See [ADR-014](../../decisions/ADR-014-skill-folders-only.md).

The root layout and focused debugging, test-engineering, change-review, CI-triage
and repository-maintenance procedures are recorded in
[ADR-015](../../decisions/ADR-015-root-skill-layout-and-installation.md).
