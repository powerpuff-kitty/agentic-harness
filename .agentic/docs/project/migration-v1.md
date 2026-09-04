# Migration to `.agentic/` layout

Legacy files such as root `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, `REFERENCE.md`, project `SECURITY.md`, `agentic.yaml`, `docs/decisions`, `docs/plans`, `docs/tasks`, and root `evals` map into `.agentic/`.

`ah migrate` must default to dry-run, identify identical duplicates separately from content conflicts, preserve source files until destination verification, allow an explicit backup directory, update router/adapters, and emit a machine-readable report. Manual migration should use version control and review the resulting diff.
