# Repository Architecture

`agentic-harness` is intentionally a static, human-readable catalog. It contains no CLI runtime and no agent prompt implementation.

```text
agentic-harness/
├── base/
├── web-app/
├── backend-api/
├── saas/
├── monorepo/
├── library-sdk/
├── modules/
│   ├── packs/
│   ├── policies/
│   └── profiles/
├── presets/
├── schema/
└── docs/
```

The root boilerplate directories are the primary public interface. Supporting reusable content is grouped under `modules/` so it does not compete visually with the catalog.

## Related repositories

- `agentic-harness-agents` owns skills, prompts, adapters, and agent workflows.
- `agentic-harness-cli` owns the native Rust `ah` binary, source pinning, composition, audits, validation, security checks, and release artifacts.

The CLI consumes pinned revisions of this repository and the agents repository. Generated target projects remain self-contained.

## Change direction

Canonical architecture changes flow outward:

```text
agentic-harness
      ↓
agentic-harness-agents
      ↓
agentic-harness-cli
```

Do not move implementation details back into this repository merely for convenience. If a new reusable concept changes project structure, define its canonical contract here first.
