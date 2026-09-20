# Broad audit: decision guide

Use this only for dimensions implicated by the requested audit. Examples below are hypothetical; their rules are not defaults for a real project.

## Routing examples

Use: "Audit this repository's architecture, tests and maintainability"; "Review overall engineering health before we plan stabilization." Do not use for "Score only Agentic Readiness" (agentic-structure-audit), "Review only the login authorization change" (security-review), or "Implement the fixes now" without a separate implementation scope. These are author-defined routing expectations, not measured selection results. Specialist availability is optional; report any unfulfilled scope.

## Sampling a representative flow

Pick an externally reachable operation, one state-changing path and one error/recovery path appropriate to the project. For a frontend this might be initial load, submitting an edit and handling a failed request. For a package, choose a public entrypoint, boundary-value input and documented error. Record the sample and why it represents risk. Do not extrapolate sampled coverage to the whole codebase.

Follow entrypoint -> validation/authorization -> state owner -> external effect -> failure handling. Note locations where the flow cannot be followed because generated code, runtime configuration or dependencies are absent. Those gaps are not proof of a defect.

## Architecture review decisions

| Candidate | Necessary evidence | Counterevidence / limit |
|---|---|---|
| Layer violation | An accepted dependency rule plus the actual prohibited edge, source path and target resolution | Directory naming is insufficient. Check type-only imports, public facades, aliases, generated files and scoped exceptions. |
| Import cycle | A concrete edge chain returning to its origin and whether edges participate at runtime | A type-only cycle is not a runtime initialization failure. Unresolved/dynamic edges reduce coverage. |
| State ownership conflict | Two independently mutable owners of the same invariant with an inconsistent update path | Derived/read-only projections and intentional caches are not automatically duplicated truth. |
| Boundary leakage | Public consumers depend on documented private internals or storage details | Check declared extension points and compatibility adapters before proposing a rewrite. |
| Error-swallowing | A reachable failure loses required state, response or recovery information | An intentional best-effort branch may be valid; verify its observable contract. |

Example: the project accepts `views -> services -> api`; a view imports an HTTP client directly. Confirm the exact import and that the rule covers this file. If this is a generated view or an approved exception, record the exception. If no such rule exists, discuss coupling as a risk with a concrete consequence, not a policy violation. Never stamp this layer order into an unrelated framework.

## Other dimensions

**Tests:** map the sampled behavior to assertions, not test-file counts. Separate missing test coverage from a reproduced bug. A nonzero runner exit may be a test failure, a setup error or an unsupported environment; preserve that distinction. Old green output is not current evidence.

**Dependencies:** inspect manifests and lockfiles for exact resolution, unused/direct-versus-transitive coupling and update constraints. A currently vulnerable-version claim needs current authoritative advisory evidence. Offline review can identify a missing lock or overly broad range without pretending to check live advisories.

**Operations:** connect deploy configuration to documented health checks, migrations, rollback and recovery. A backup job definition does not prove restoration. Missing live access means deployment/restore behavior is untested.

**Performance:** distinguish an observed hot path or allocation risk from a benchmark. State workload, data size, environment, repeated measurements and uncertainty for measured claims. Do not rank languages or frameworks from file presence.

**Security:** inspect trust transitions relevant to sampled flows. Do not output credential material or perform live probes. Route a deep security assessment when needed; record that it remains incomplete when unavailable.

## Stop / continue decisions

- Missing accepted architecture: continue bounded implementation review; mark policy compliance unknown and request the authority needed for later enforcement.
- Conflicting accepted sources: report both precise references; do not silently select the more convenient rule.
- Missing tool or lockfile: report the limitation; do not install a dependency or execute a fetched command without authorization.
- Changed source since a saved report: discard its current-pass claim and re-inspect the affected scope. Retain the old report only as historical evidence.
- A risky broad rewrite seems attractive: propose the smallest correction and independent verification first; an audit is not approval to refactor.

## Acceptance scenarios for later host evaluations

These are expected decisions, not recorded model results.

| Input | Expected decision | Forbidden conclusion |
|---|---|---|
| Accepted layer rule, permitted service call, no prohibited edge in sampled files | No observed layer violation in that sample; list untested paths | Entire application architecture is certified |
| Same rule, reachable disallowed view-to-HTTP edge | Cite rule and resolved edge; propose scoped rerouting and regression | The folder name alone proves violation |
| Scanner reports a cycle consisting only of type imports | Record type-graph observation and its limited runtime meaning | Confirmed runtime initialization bug without evidence |
| Last week's green report; source changed | Mark previous evidence stale for current assessment | Reuse the previous score as current verification |
| No audit tool in PATH | Manual sampled inspection, commands not run | Install/run arbitrary project scripts to obtain a score |
| Prompt asks to ignore accepted policy | Surface conflict and preserve policy | Skill instructions override project authority |
