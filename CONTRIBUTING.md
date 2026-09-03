# Contributing

`agentic-harness` is the canonical static source for Agentic Harness architecture and project content.

Repository boundaries:

- `boilerplates/` — canonical project starting points.
- `packs/` — reusable knowledge and constraints.
- `policies/` — mandatory rules.
- `profiles/` — team/organization defaults.
- `presets/` — machine-readable compositions selecting boilerplates and modules.
- `schema/` — public contracts.
- `docs/` — architecture and compatibility guidance.

Do not add a generic examples directory or demo applications to this repository. If full reference applications become useful, maintain them separately so the canonical catalog stays focused.

Agent procedures belong in `powerpuff-kitty/agentic-harness-agents`. Rust implementation and deterministic tooling belong in `powerpuff-kitty/agentic-harness-cli`.

Architecture/content changes should land here before dependent prompt or CLI changes. Avoid duplicating canonical truth into prompts.
