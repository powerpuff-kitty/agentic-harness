# Migration to the `.agentic/` layout

## Current support

Automatic filesystem-layout migration is **not implemented** in the current CLI. Experimental `ah agentic migrate` compares model profiles; it does not move context files. Do not use an unimplemented apply command or attempt to force a legacy project through `upgrade`.

## Manual, backup-first procedure

1. Make a restorable backup outside the working target. Record the source revision and include untracked project context; a Git commit alone may omit untracked or ignored files. Do not publish credentials as part of a backup.
2. Inventory existing canonical documents, routes and vendor instructions. Treat the following mapping as a starting point, not permission to overwrite an existing destination.

| Legacy context | Target context |
| --- | --- |
| Root product/architecture/design/reference documents | `.agentic/PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, `REFERENCE.md` |
| Internal project security model | `.agentic/SECURITY.md` |
| `agentic.yaml` | Reviewed `.agentic/manifest.yaml` using the current schema |
| `docs/decisions`, `docs/plans`, `docs/tasks`, root `evals` | Corresponding `.agentic/` directories |

Keep a public vulnerability-disclosure `SECURITY.md` at the root when applicable; it is not necessarily the internal security model.

3. Compare source and destination bytes. Record identical duplicates separately; resolve differing accepted documents explicitly. Preserve custom routes and user-authored content. Do not replace real decisions with catalog placeholders.
4. Prepare the current manifest and lock/provenance data from their supported schemas. Merely renaming the legacy manifest is insufficient. Do not invent source revisions/checksums or copy another project's lockfile as provenance.
5. Update the compact `AGENTS.md` router and relevant native pointers without duplicating canonical truth. Review all links and the complete diff. Only remove a legacy source after its destination is verified and the backup is restorable.
6. Resolve mixed manifests in the reviewed working copy, then run `ah validate TARGET`. Validation checks structure/routes; it does not certify the semantic correctness of the migrated product or architecture. Run the project's separately approved tests as appropriate.
7. Verify the actual host loads the intended context, retain the migration record and reconcile any remaining gaps. Restore the backup rather than continuing from a partially understood state if checks fail.

## Future automation contract

Filesystem migration automation must default to a read-only plan, distinguish duplicates from conflicts, bind the plan to source content, verify a backup and destinations before deletion, confine paths and roll back partial failures. These are requirements for future implementation, not supported command promises.

Tracked by [CLI migration work](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/57). The [version-specific CLI contract](https://github.com/powerpuff-kitty/agentic-harness-cli/blob/main/docs/cli-contracts.md) remains authoritative for supported syntax.
