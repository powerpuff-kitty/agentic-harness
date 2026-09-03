# Contributing

`agentic-harness` is the canonical static catalog for Agentic Harness project architecture.

## Repository boundaries

- Root boilerplate directories (`base/`, `web-app/`, `backend-api/`, `saas/`, `monorepo/`, `library-sdk/`) define canonical project starting points.
- `modules/packs/` contains reusable knowledge and constraints.
- `modules/policies/` contains mandatory rules.
- `modules/profiles/` contains team and organization defaults.
- `presets/` contains machine-readable compositions.
- `schema/` contains public contracts.
- `docs/` contains architecture and compatibility guidance.

Do not add runtime/CLI code, agent skills, generic examples, or product marketing to this repository. Agent procedures belong in `powerpuff-kitty/agentic-harness-agents`; Rust implementation and deterministic tooling belong in `powerpuff-kitty/agentic-harness-cli`.

Every boilerplate must include valid `boilerplate.json` metadata. Architecture/content changes should land here before dependent prompt or CLI changes. Avoid duplicating canonical truth into prompts or implementation code.
