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
