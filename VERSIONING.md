# Versioning and Compatibility

Canonical content follows semantic versioning at the release level, while individual boilerplates and reusable modules carry their own versions where useful.

- **Patch** — clarifications and compatible fixes.
- **Minor** — backward-compatible additions, new boilerplates/modules, additive schema fields.
- **Major** — incompatible generated-project layout changes, removed/renamed contracts, or behavior requiring migration.

Each root boilerplate carries `boilerplate.json` metadata. Presets and profiles are public composition contracts. Breaking changes require a documented migration path and coordinated updates to `agentic-harness-agents` and `agentic-harness-cli`.

Generated repositories must remain self-contained. Upgrades should preserve project-specific accepted truth and must not silently rewrite durable decisions.

See `docs/compatibility.md` and `docs/release-process.md`.
