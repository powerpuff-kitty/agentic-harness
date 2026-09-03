# Contributing

`agentic-harness` is the canonical static source for Agentic Harness architecture and project content.

Repository boundaries:

- `templates/` — canonical project shapes.
- `boilerplates/` — human-readable starter compositions.
- `packs/` — reusable knowledge and constraints.
- `policies/` — mandatory rules.
- `profiles/` — team/organization defaults.
- `presets/` — machine-readable compositions.
- `schema/` — contracts.
- `examples/` — accepted compact examples.

Agent procedures belong in `powerpuff-kitty/agentic-harness-agents`. Rust implementation and deterministic tooling belong in `powerpuff-kitty/agentic-harness-cli`.

Architecture/content changes should land here before dependent prompt or CLI changes. Avoid duplicating canonical truth into prompts.
