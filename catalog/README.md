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

The language-neutral architecture contract is `schema/architecture-graph.v1.schema.json`; it models capabilities, contracts, providers/adapters, apps, engines, surfaces, infrastructure and authorities without prescribing folders. Derived graph-only routing, duplicate-candidate and summary results use `schema/architecture-analysis.v1.schema.json`; guardrail/surface/diagram derivatives use `schema/architecture-derivatives.v1.schema.json`, declared graph-to-graph changes use `schema/architecture-drift.v1.schema.json`, and revision-bound public-project conformance snapshots use `schema/architecture-reference.v1.schema.json`. See [Architecture Graph semantics](../.agentic/docs/architecture/architecture-graph.md).

CLI evidence contracts include `schema/codebase-audit.v2.schema.json`, `schema/agentic-readiness.v2.schema.json`, and `schema/design-system-discovery.schema.json`. Task-scoped context selection uses `schema/compiled-context-plan.v1.schema.json`; it separates mandatory authority from relevance and records explicit token-estimate budgets, source digests, disclosure level and incomplete coverage. The provider-neutral Decision Kernel contract is the `schema/decision-*.v1.schema.json` family covering specs, graphs, requests, provider capabilities, policy, immutable receipts, outcomes, labeled evaluation datasets, empirical calibration reports, regression budgets and side-effect-free evaluation. See [Decision Kernel architecture](../.agentic/docs/architecture/decision-kernel.md) and [CLI contract semantics](../.agentic/docs/project/cli-contracts.md).
