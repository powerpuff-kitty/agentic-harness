# Ecosystem repositories

`agentic-harness` owns the project contract, catalog, policies, profiles, presets, and schemas. `ai-skills` contains self-contained `<name>/` directories directly at its root, each owning its procedure, local resources and license. `README.md` introduces the catalog and `INSTALL.md` provides installation guidance. `agentic-harness-cli` owns deterministic composition, migration, validation, audit, and release binaries.

Changes flow from canonical contract to procedure and then to deterministic implementation. Compatibility changes must update source pins and tests explicitly.

The current procedure source is [ai-skills](https://github.com/powerpuff-kitty/ai-skills),
renamed from `skills` (earlier `agentic-harness-agents`). The separate role source is
[ai-agents](https://github.com/powerpuff-kitty/ai-agents), renamed from `agents`.
It owns portable specialist profiles, team declarations and host profile adapters.
Installing either collection does not install the other or grant tool permissions.

Renames preserve repository history, issues, tags and individual skill/role IDs.
Current links and source declarations use the new names. Historical ADRs, imported
source locks and published records retain the names valid for their snapshots;
[ADR-013](../../decisions/ADR-013-skills-repository-name.md) records the earlier rename.
Adapter report schemas accept current and historical procedure-source names.

Beyond its README and installation prompt, the skills source has no collection-level
project context, plugin manifests, CI/release workflows or packaging scripts. Host adapter templates belong to the
`adapter-sync` skill. Whole-collection plugin imports are available only from the
historical versions that shipped them; current installs copy individual skill
folders. OpenCode uses native SKILL.md discovery; installation places those folders
in the supported host/project skill location rather than transforming their format. See [ADR-014](../../decisions/ADR-014-skill-folders-only.md).

The root layout and focused debugging, test-engineering, change-review, CI-triage
and repository-maintenance procedures are recorded in
[ADR-015](../../decisions/ADR-015-root-skill-layout-and-installation.md).
