# Release Process

Before publishing a canonical catalog revision:

1. Catalog validation must pass.
2. Update `CHANGELOG.md` and any affected boilerplate/module versions.
3. Review schema and preset compatibility and document migrations for breaking changes.
4. Verify dependent `agentic-harness-agents` changes when procedures must adapt.
5. Verify `agentic-harness-cli` against the exact canonical revision before advancing its upstream lock.
6. Tag catalog releases using semantic versioning when a stable public milestone is reached.

Branch protection should require catalog validation and review before merge. CLI binary release testing belongs in `agentic-harness-cli`, not in this static catalog repository.
