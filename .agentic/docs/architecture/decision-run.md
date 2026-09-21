# DecisionRun fan-out, cache/replay and reducer contract v1

Status: additive Decision Kernel contract for #110. It records bounded execution
evidence; it does not implement provider execution, scheduling, cache storage, or
application side effects.

## Stable run identity

A DecisionRun identity binds the immutable state schema/version/fingerprint, one
question-set ID/revision/digest, and the provider type/ID/model/version. The
canonical identity SHA-256 is recomputed from those fields. Changing state,
questions, provider or model/version changes the identity.

The question-set digest is expected to bind the reviewed DecisionGraph/spec set.
This inspector does not fetch or authenticate the graph; callers must retain its
actual artifact/provenance separately.

## Parallel fan-out

Nodes repeat stable spec IDs/revisions and declared dependencies. Recorded start/end
intervals are checked so a node cannot overlap a direct or transitive dependency.
Peak concurrent intervals must stay within `limits.max_parallel`. These are
consistency checks over supplied timestamps, not proof that a runtime scheduler
actually isolated or ran work in parallel.

Timeout and cost limits are recorded boundaries. Terminal non-success states remain
distinct, including insufficient/conflicting evidence, out-of-distribution,
provider failure, timeout, budget exceeded, cancelled and dependency-blocked.
Explicit reason codes prevent those states from collapsing into false or success.
Fallback is one of fail-closed, review or abstain.

## Cache and replay

A cached/replayed node records its originating run reference and originating
identity SHA. It is accepted as structurally equivalent only when that identity
matches the current DecisionRun identity. Matching identity is not automatic cache
permission: current policy, evidence freshness/authenticity, retention rights and
scope must still permit reuse.

Replay mode requires zero provider calls and forbids provider-sourced nodes. It
therefore allows recorded reducer inputs to be reconstructed without re-inference.
The inspector never calls a provider or cache backend.

## Deterministic reducers

Reducer records contain an explicit version, exact input node/status/receipt
references and digests, an input digest and output digest. `pure: true`,
`side_effects: false` and `consequence_authorized: false` are schema constants.
The inspector recomputes the reducer-input digest and verifies each supplied input
against the recorded node result.

A reducer may select a recorded fallback, but that fallback remains data; this
contract does not execute workflow branches. DecisionPolicy and separately
authorized application workflows still own consequence decisions.

## Relationship to existing Decision Kernel

DecisionSpec defines each atomic judgment. DecisionGraph defines dependencies and
deterministic reducers. DecisionRequest identifies immutable state and budget.
DecisionReceipt records each judgment. DecisionRun binds those execution/reuse
records together without changing any existing v1 schema.

The CLI may later implement provider fan-out/cache/replay mechanics. Publishing this
contract is not evidence that such a runtime exists or that a Jev call occurred.

## Validation

`.github/scripts/decision_run.py` inspects supplied records only. Focused tests
cover identity drift, dependency cycles/overlap, concurrency, cache/replay
provenance, provider-call boundaries, explicit failure states, reducer purity/input
identity and size limits. Tests are deterministic contract evidence, not model or
provider outcomes.
