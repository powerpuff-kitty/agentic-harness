# library-sdk

Use for reusable packages, SDKs, public libraries, protocols, or developer tooling.

## Decisions to record

| Decision | Required project detail |
| --- | --- |
| Public surface | List supported entry points, types, commands or wire formats; distinguish internal modules from extension points. |
| Compatibility | Define supported runtimes/platforms, versioning policy and what counts as a breaking change, including error and serialization behavior. |
| Failure behavior | Specify typed errors, cancellation, timeouts, retries and resource ownership where applicable. |
| Distribution | Identify package/artifact contents, licenses/notices and reproducible consumer installation commands. |
| Evolution | Define deprecation notice, migration examples, support window and removal criteria. |
| Publication | Link project release gates, artifact verification and rollback/recovery procedure. |

Keep unresolved compatibility promises explicit. Public API changes require compatibility review under the project's policy; this pack does not authorize a release.

## Example and anti-patterns

A synthetic parser exposes `parseEntry(text)` with documented success and invalid-input results. Changing invalid input from a returned error to a thrown exception changes consumer behavior even if the function name is unchanged. Adding a required property to a public input type also needs compatibility review. Test a consumer importing the published entry point rather than an internal source path.

Avoid claiming runtime support from compilation alone, accidentally exporting internal helpers, changing serialized field meanings without versioning, or writing examples that depend on unpublished workspace files. Do not interpret a prerelease label as permission to silently break existing consumers.

## Evidence and completion

- Compare the public API and representative old-consumer behavior before and after the change; explain intended incompatibilities.
- Exercise error paths and relevant cancellation/resource cleanup, not only a successful example.
- Install the actual candidate artifact in a clean synthetic consumer for each advertised support target; retain missing targets as gaps.
- Verify packaged files, license notices and runnable examples against that artifact's identity.
- Document migration/deprecation behavior when relevant, and report exact tests and environments used.

Source tests, packaged-consumer tests and publication approval are distinct. If only source tests ran, say so; do not claim verified distribution or release readiness.
