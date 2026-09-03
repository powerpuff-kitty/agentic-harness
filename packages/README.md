# Official Packages

This directory contains the official Agentic Harness package bundle.

- `templates/` — repository shapes
- `presets/` — named compositions
- `profiles/` — organization/team defaults
- `packs/` — reusable knowledge and constraints
- `skills/` — repeatable agent procedures
- `policies/` — mandatory development rules
- `core/` — package-set compatibility metadata

These packages are currently embedded into the native `ah` binary at compile time. Keeping them behind a package boundary allows future independent versioning, registries, third-party sources, or separate repositories without changing generated project-local paths.
