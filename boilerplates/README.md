# Boilerplate Catalog

Each directory is a canonical Agentic Harness project starting point.

- `base` — minimal agent-native repository foundation.
- `web-app` — browser-facing application structure.
- `backend-api` — service/API structure.
- `saas` — SaaS-oriented application structure.
- `monorepo` — multi-application/package repository structure.
- `library-sdk` — reusable library or SDK structure.

Boilerplates define initial repository shape and durable harness files. They should remain understandable without the CLI and consumable by humans, agents, and tooling.

Use `presets/` to express machine-readable compositions that select a boilerplate plus packs and other modules. Do not place full demonstration applications here; this catalog contains starting structures, not showcases.
