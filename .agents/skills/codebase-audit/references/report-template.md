# Human audit report template

This is a human report format, not `codebase-audit.v2` JSON. Do not invent canonical fields or serialize unsupported readiness scores.

## Scope and identity

- Source revision and relevant dirty-worktree/input identity: ...
- Requested dimensions, exclusions and unavailable files/services: ...
- Accepted rules and exact authority paths/versions: ...
- Sampled operations and why they were selected: ...

## Findings

For each: **ID / classification / severity / confidence**, exact source path and line range, accepted requirement or concrete failure, causal path, strongest counterevidence, impact/preconditions, smallest remediation and proposed regression.

Example (synthetic, not an executed test): `ARCH-1 / violation / medium / high`. Accepted target rule `project-context/layers.md:12` prohibits product views from importing the HTTP client. `src/views/orders.ts:8` imports `src/api/client.ts` directly and uses it at line 31; the generated-file exception does not apply. Route the call through the existing order service; add an import-boundary regression. No browser or application tests ran. These paths are example placeholders, not actual evidence.

Counterexample: two `Button` files, one generated vendor adapter and one product wrapper, do not establish harmful duplication merely because their names match. Record their distinct responsibilities or the precise overlap that remains to be checked.

## Verification ledger

| Check | Input identity / scope | Tool and exact invocation | Result | Limits |
|---|---|---|---|---|
| Focused source inspection | ... | manual, named paths | performed | runtime not tested |
| Build/test | ... | approved command or not invoked | passed / failed / setup-error / not-checked | ... |
| Existing report | original identity | original provenance | historical / stale / applicable | ... |

## Repair order and assessment

Order repairs by risk and prerequisite, not by file count. Each has an owner/scope when known, a regression to run and any required approval. Include unresolved authority conflicts and untested surfaces. A numeric summary requires a named accepted rubric; unknown dimensions stay unknown. A successful sample never establishes universal production readiness.
