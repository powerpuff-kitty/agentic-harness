# Architecture

## Ecosystem boundaries

```text
agentic-harness
canonical project contract + catalog + schemas
        ↓ pinned source
agentic-harness-agents
skills, prompts, adapters, and agent procedures
        ↓ pinned source
agentic-harness-cli
native Rust composition, migration, audit, and validation
        ↓
self-contained target repository
```

The canonical repository owns what is true. The agents repository owns how an agent should work. The CLI owns deterministic mechanics and enforcement. No downstream layer may silently redefine an upstream contract.

## Target-project contract

```text
project/
├── README.md
├── AGENTS.md
├── source and normal project files
├── .agentic/
│   ├── README.md
│   ├── manifest.yaml
│   ├── lock.json
│   ├── PRODUCT.md
│   ├── ARCHITECTURE.md
│   ├── SECURITY.md
│   ├── optional DESIGN.md and REFERENCE.md
│   ├── decisions/
│   ├── plans/
│   ├── tasks/
│   ├── docs/
│   ├── evals/
│   ├── packs/
│   └── policies/
└── .agents/skills/
```

Only the compact `AGENTS.md` router is mandatory at the project root. Vendor adapters remain at vendor-required paths and point back to the router.

## Authoring catalog

`catalog/variants/<name>/files/` contains a complete materialized target structure. `catalog/packs`, `catalog/policies`, `catalog/profiles`, `catalog/presets`, and `catalog/schema` are independently reusable authoring sources. Complete variant trees are intentionally inspectable; the CLI may optimize internally but cannot make hidden overlays the only source of truth.

## Composition flow

1. Select a variant directly or through a preset/profile.
2. Copy the complete variant tree into the target while excluding source metadata.
3. Install selected packs, policies, and skills into local project paths.
4. Resolve names, maturity, permissions, versions, source revisions, and checksums into the manifest and lockfile.
5. Synchronize thin vendor adapters.
6. Validate the resulting contract and report conflicts rather than silently overwriting project-owned truth.

## Upgrade and migration

Legacy root-level context is read for compatibility. `ah migrate` performs an inspectable plan, detects duplicate/conflicting canonical files, and only writes after explicit application. Existing project truth wins over generic catalog placeholders.

## Invariants

- Project truth is local and self-contained after composition.
- Policies have explicit precedence and remain inspectable.
- Skills are procedures, not architecture truth.
- Source metadata does not leak into generated projects.
- Destructive, production, secret, and publication actions obey declared permissions.
- Audits say what was and was not checked.
- Re-running deterministic operations does not create drift.
