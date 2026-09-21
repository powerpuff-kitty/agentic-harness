# Context summaries, cache records and event memory v1

Status: additive provider-neutral contracts for #117. They complement continuation
checkpoints and compiled context plans; they do not create a runtime memory service.

## Boundaries

All three records are generated or historical navigation artifacts. None can become
canonical project truth merely by validating, matching a hash, or being replayed.
ADRs, accepted project truth, current source, required checks and explicit approvals
remain authoritative. The contracts never read referenced paths, call a model or
provider, authorize cache reuse, or execute an action.

## Hierarchical summaries

`context-summary.v1.schema.json` records a generated summary at repository,
package, module, file or symbol scope. Scope ancestry is ordered from broader to
narrower identities. Every source has an exact digest and optional revision.
Coverage is complete, partial or unknown; complete summaries cannot list missing or
unchecked material, while partial/unknown summaries must expose at least one gap.

`summary_sha256` binds the exact UTF-8 summary text. The inspector recomputes it.
This detects changed summary bytes, not truthfulness, source authenticity, complete
source discovery, or model quality.

## Semantic/analysis cache entries

`context-cache-entry.v1.schema.json` records repository revision, artifact type,
producer identity/version and every declared source/config/rule/decision/summary/
diagnostic/tool input with digest and revision. The identity digest is computed from
those fields with inputs sorted by stable ID; the result artifact is recorded
separately so its location does not redefine the request identity.

`inspect_cache(entry, current)` compares a caller-supplied current repository/input
view. Exact equality yields `matching-recorded-inputs`; any changed, missing or
extra dependency yields `stale-or-different-inputs`. Both outcomes keep
`reuse_authorized: false`: freshness is only one prerequisite. Current policy,
scope, provider permission, evidence sufficiency, calibration and consequence
authorization require separate review.

## Append-only event memory

`context-event.v1.schema.json` records compact decision, constraint, change,
verification and unresolved events. Every event has a stable ID, sequence, timestamp,
producer, canonical references and optional evidence references. Events can supersede
prior event IDs but may not supersede themselves or future/unknown IDs within a
reviewed stream.

The inspector requires strictly increasing sequence numbers and nondecreasing
timestamps in the supplied order. It does not authenticate clocks or prove the
stream is globally complete. Event statements summarize history and point back to
ADRs/project truth/tasks/sources/checks/artifacts; they do not replace those records.

## Relationship to checkpoints

ContextCheckpoint remains a task-continuation aid containing a small working set,
historical checks and open items. Context events are append-oriented durable history;
summaries are scoped generated views; cache entries bind reusable computation inputs.
A checkpoint may reference these artifacts, but none should embed full transcripts
as a prerequisite for reconstructing project decisions.

## Validation

`.github/scripts/context_memory.py` performs supplied-record semantic checks only.
Its tests run through `validate_cli_contracts.py`. Schema validity, hash equality
and ordered events are deterministic consistency evidence, not proof of actual host
loading, source acquisition, provider execution, token savings or runtime cache use.
