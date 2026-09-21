# Token-efficiency evaluation and advisory stage routing v1

Status: additive provider-neutral contracts for #118. These records can consume
results from the agents repository's matched/repeated trial tooling; they do not
replace that runner or create a model router.

## Same-task comparison

`token-efficiency-evaluation.v1.schema.json` binds one task/fixture/source revision
and required checks to a full-context baseline and compiled-context candidate.
Each treatment records required evidence presence, estimated usage, optional
observed usage and acceptance/verification outcomes.

Input, tool-output and output token channels are separate. Observed usage can remain
partial; when `token_usage_complete` is true, all three token channels and retry
count must be present. Latency and cost are independently nullable. Any observed
measurement requires an evidence reference. Null cost remains unknown rather than
being interpreted as zero.

The inspector reports channel deltas only when both treatments declare complete
observed token usage. It never sets `token_savings_verified` true: general savings
require representative repeated trials, authenticated/task-scoped usage and outcome
review beyond one record.

Required evidence and checks are quality gates. A candidate that omits required
evidence, fails/skips required checks, fails acceptance or lacks passing verification
is a regression even when token counts are lower. A broken baseline makes the
comparison inconclusive rather than proving the candidate is better.

## Advisory stage routing

`stage-routing-evidence.v1.schema.json` covers deterministic tool,
retrieval/indexing, summarization, reasoning/implementation and review stages.
Routes are always advisory and never authorize execution.

When an exact deterministic answer is available, the semantic inspector requires
the selected mechanism to be a deterministic tool. Unmeasured routes cannot carry
measured quality, cost or evaluation references. A project-evaluated model/provider
route needs project evaluation evidence, model-registry evidence and measured
quality before it is labelled evidence-backed.

Evidence-backed still means advisory. Runtime permissions, data-sharing policy,
budget and consequence authority remain separate.

## Relationship to agents evaluation tooling

The agents repository already prepares/stages matched full/progressive treatments,
retains failed/missing repetitions and can inspect supplied Codex usage snapshots.
Those tools produce experiment evidence; these canonical contracts define a compact
cross-project interchange/inspection boundary. Do not reinterpret cumulative thread
snapshots as complete task usage or fixture tests as model outcomes.

## Validation limits

`.github/scripts/token_economics.py` validates supplied records only. It does not
run checks, models, Jev, tokenizers or billing APIs. Estimated values depend on their
recorded estimator. Observed values are caller-supplied evidence and are not
authenticated by schema validation.
