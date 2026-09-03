# Versioning and Compatibility

The framework uses semantic versioning for public releases. Templates, skills, and packs also carry module versions so their compatibility can evolve independently.

- Patch: clarifications and compatible fixes.
- Minor: backward-compatible features, new packs/skills, additive schema fields.
- Major: generated-project layout changes, incompatible schema/policy changes, removed/renamed modules, or behavior requiring migration.

Generated repositories must remain self-contained. A newer framework may upgrade them, but should never silently rewrite project-specific truth. Breaking upgrades require a documented migration path.

See `docs/compatibility.md` and `docs/release-process.md`.
