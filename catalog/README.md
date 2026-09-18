# Agentic Harness catalog

This directory contains reusable authoring sources. The repository root and `.agentic/` demonstrate a real installation; the catalog provides content that can be selected and installed into other projects.

```text
catalog/
├── variants/   complete materialized project structures under <name>/files/
├── packs/      reusable domain and technical knowledge
├── policies/   mandatory must/must-not rules
├── profiles/   organization/team defaults
├── presets/    named compositions
└── schema/     public machine-readable contracts
```

Each public variant is complete and directly browsable. Metadata may describe inheritance, but users and tools do not need to mentally compose hidden overlays to understand the resulting project.

CLI evidence contracts include `schema/codebase-audit.v2.schema.json`, `schema/agentic-readiness.v2.schema.json`, and `schema/design-system-discovery.schema.json`. See [CLI contract semantics](../.agentic/docs/project/cli-contracts.md).

The [filled synthetic context example](../.agentic/evals/fixtures/context/reading-list/README.md) illustrates authored truth and explicit unknowns. [Context selection](context/README.md) defines full/minimal composition for compatible CLI versions while retaining complete materialized source variants. See the [implementation plan](../.agentic/plans/active/2026-09-18-minimal-context.md) for delivery evidence and remaining work.
