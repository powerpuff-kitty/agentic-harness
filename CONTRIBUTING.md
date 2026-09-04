# Contributing

Read `AGENTS.md`, `.agentic/README.md`, the relevant current truth, and accepted ADRs before changing the contract.

Repository boundaries:

- `.agentic/` — this repository's own canonical project context.
- `catalog/variants/` — complete target-project starting structures.
- `catalog/packs/` — reusable knowledge and constraints.
- `catalog/policies/` — mandatory rules.
- `catalog/profiles/` — organization/team defaults.
- `catalog/presets/` — named compositions.
- `catalog/schema/` — public machine contracts.

Before opening a PR:

```bash
python3 .github/scripts/validate_catalog.py
```

A contract change should update the relevant schema, docs, ADR/current truth, migration guidance, and downstream source pins/tests. Do not add root-level canonical project truth or public overlay-only variants. Keep vendor adapters thin.

Agent procedure changes belong in `agentic-harness-agents`; deterministic implementation changes belong in `agentic-harness-cli`.
