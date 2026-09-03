# Compatibility Policy

Compatibility is tracked across the canonical content revision, root boilerplates, reusable modules, presets, schemas, agent skills, and CLI release.

Canonical compatibility surfaces in this repository include:

- each root `boilerplate.json`;
- `modules/packs/manifest.json`;
- `modules/profiles/*/profile.json`;
- `presets/*.json`;
- public contracts under `schema/`.

Agent skill versions are maintained in `agentic-harness-agents`. CLI releases pin exact revisions of both authoring repositories.

An upgrade must preserve existing project-specific truth and report incompatible changes before applying them. Deprecated fields or modules should remain supported for at least one minor compatibility window when practical, with a documented replacement and migration path.
