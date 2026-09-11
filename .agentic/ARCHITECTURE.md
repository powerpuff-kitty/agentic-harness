# Architecture

## Ecosystem boundaries

```text
agentic-harness
canonical project contract + catalog + schemas + Design Genome contracts
        ↓ pinned source
agentic-harness-agents
skills, prompts, adapters, and agent procedures
        ↓ pinned source
agentic-harness-cli
native Rust composition, migration, audit, validation, design analysis/compiler mechanics

agentic-harness-app
independent web application for visual design analysis, review, generation, comparison, and export

        ↓ both consume compatible canonical schemas/artifacts
self-contained target repository / project artifacts
```

The canonical repository owns what is true. The agents repository owns how an agent should work. The CLI owns deterministic native mechanics and enforcement. The app is a separate product surface that implements equivalent canonical design operations without shelling out to the CLI binary. No downstream layer may silently redefine an upstream contract.

## Design-intelligence boundary

Canonical design-intelligence contracts live in `agentic-harness`, including the Design Genome and unified design-analysis schemas. The CLI and app may use different implementation stacks, storage, and user interfaces, but parity-critical behavior is defined by shared schemas, fixtures, and semantic outputs.

```text
                    agentic-harness
             Design Genome + analysis schemas
                        /          \
                       /            \
         agentic-harness-cli    agentic-harness-app
          local/native CLI       independent web app
                       \            /
                        \          /
                 compatible artifacts
```

The web app must not make the CLI executable an architectural dependency. The CLI must not depend on the web app or hosted services for deterministic core operations.

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

Public design-intelligence schemas live under `catalog/schema/` so CLI, app, agents, and external consumers can validate compatible artifacts without depending on one frontend implementation.

## Design-intelligence flow

```text
project source / imported artifact / runtime evidence
        ↓
deterministic analysis where possible
        ↓
unified design-analysis artifact
        ↓
optional AI interpretation + human review
        ↓
approved Design Genome
        ↓
Design Compiler
        ↓
prompt / implementation brief / tokens / docs / QA / MCP context / other deterministic targets
        ↓
implementation
        ↓
re-analysis + drift/compliance comparison
```

External design/reference providers remain evidence sources. Their data cannot become canonical project truth without explicit review, and provider licensing/retention restrictions must be enforced before indexing, caching, redistribution, benchmarking, or export.

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
- Design analysis distinguishes measurement from inference and recommendation.
- The Design Genome is project-owned truth only after review/approval.
- CLI and app parity is defined by canonical contracts and fixtures, not by sharing a frontend or invoking one product from the other.

## Authored-source licensing

The CLI, canonical catalog/registry and agent procedures use MIT for their authored
content, as accepted in [ADR-007](decisions/ADR-007-mit-licensing.md). Third-party
licenses remain intact. Complete variants carry `.agentic/THIRD_PARTY_NOTICES.md`
so copying Harness material retains its attribution without assigning a license
to the user's independently authored application. Composition preserves existing
project license files and records the notice in its installed-content checksums.
