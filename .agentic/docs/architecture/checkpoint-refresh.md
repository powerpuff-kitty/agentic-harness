# Selective checkpoint refresh

The optional `plan_refresh(previous, current, current_source_ids=[...])` function in
`.github/scripts/context_checkpoint.py` compares two supplied ContextCheckpoint v1
records. It identifies old notes and historical checks whose declared dependencies
need review. It does not collect current source or certify a cached answer. This is
repository contract tooling, not a shipped runtime, host hook or additional skill.

Use the existing `context-checkpoint.v1.schema.json`; there is no replacement schema.
Existing `inspect` and `decode` behavior is unchanged. Both records must pass the
existing semantic inspection. The current record cannot have an earlier declared
timestamp, but a timestamp is not evidence that a source was freshly observed.

## Acquire evidence before comparing records

Resolve the actual target repository, current request, root/nested instructions and
criteria first. The v1 checkpoint has no authenticated repository-identity field:
include target/criteria identity in the task scope and independently verify that
both records concern that same target. An equal generic task name is insufficient.
Use approved source reads or the existing selected-evidence helper to obtain current
hashes; never copy an old hash simply to obtain a match. Retain unavailable sources
as unavailable, not omitted successes. Preserve old source IDs and add a new ID for
a new version, keeping old check inputs tied to the bytes actually recorded then.

Pass an explicit list of source IDs from the current checkpoint. A record can retain
several versions of one path, but the selected current view must choose at most one
version for each exact reference/role pair. Missing, duplicate or ambiguous IDs
fail before a plan is returned. No reference is opened by this function, regardless
of whether it looks like a path, URL or command. Current acquisition remains the
caller's independently permitted responsibility.

For already decoded, reviewed records, after importing the existing repository module:

```python
plan = context_checkpoint.plan_refresh(
    previous,
    current,
    current_source_ids=["rules-current", "criteria-current", "api-current", "log-current"],
)
```

Those IDs are examples, not presumed files or authentic observations. Select the
actual relevant IDs, including available diagnostic artifacts when checking old
log provenance. Keep required evidence and contradictory sources in scope.

## Interpret changes narrowly

Exact reference, role and hash comparisons produce matching, changed, unselected,
previously unavailable or currently unavailable states. Source-only changes mark
dependent old notes and check attempts; unrelated recorded inputs can still match.
Changes, omissions or additions to instructions/criteria require broader context
review even when a note did not explicitly cite the rule. An instruction present
in the current record but omitted from selection is visible, not silently ignored.
Changed goal, scope, task ID, base revision, or an unknown base revision also require
broader review. Matching base revision does not account for uncommitted changes.

New selected ordinary evidence triggers selection review: it may reveal a new
relationship that old notes did not record. Unselected ordinary sources and rules
absent from both records cannot be assessed. The planner does not discover semantic
dependencies or automatically mark newly found files irrelevant.

Historical check IDs must not disappear or silently change command, outcome, capture
completeness or resolved input/log provenance. The report flags those divergences
and retains every old attempt, including failures and unexecuted checks. It reports
only historical status; matching inputs never means a check ran again or passed.
Open blockers remain blockers. The output excludes statement bodies, commands, hashes
and references; use the IDs to retrieve permitted underlying evidence when needed.

`matching-recorded-inputs` means only field equality within this supplied view.
It is not a cache hit, current truth, restored model context, accepted policy, action
permission or Jev-result eligibility. Spec/state/provider/criteria changes must
still be reviewed before reusing a semantic judgment. Forged records can agree.
All authenticity, automatic-reuse, source-freshness and check-verification claims
remain explicitly false, and model token usage remains unknown.

## Validation and scope

Run `python3 .github/scripts/test_checkpoint_refresh.py` from the canonical checkout.
The tests are part of existing contract validation and cover selective source change,
policy-only change, new/omitted evidence, same-path versions, role/path substitution,
retry history, rewritten check inputs, scope/timestamp drift, input immutability and
absence of reference reads. They are deterministic consistency tests, not independent
model trials or token-savings measurements. No source acquisition, persistent cache,
summary generation, provider call or downstream application work is added here.
