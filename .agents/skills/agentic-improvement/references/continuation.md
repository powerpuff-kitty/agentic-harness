# Compact continuation checkpoints

Use an existing permitted task record when a nontrivial task must resume after a
context boundary. Ordinary edits need no checkpoint, extra model or wrapper skill.
Keep only what the next unresolved action needs; do not preserve the transcript.

## Record a small, reviewable handoff

```text
Task and scope: goal, explicit exclusions, next unresolved action
Source state: actual revision if known; relevant working-tree paths and byte identities
Decisions: references to accepted project decisions, not newly inferred policy
Notes: observations versus inferences; source references for both
Checks: name/command, attempt, exact inputs, status, log reference, truncation
Open items: missing or contradictory evidence; which items block progress
```

Retain a failed first attempt when a later retry passes. Different source versions
need different identities, even at the same path. Unknown or unavailable evidence
stays explicit; do not guess hashes, logs, confidence, approvals or check outcomes.
Reference existing evidence rather than copying large logs or snippets again.
Do not write a new file unless persistence and its destination are permitted.

For a consumer needing structured interchange, use the target's accepted canonical
`context-checkpoint.v1.schema.json` and its semantic inspection. It is not a skill-
owned replacement for DecisionReceipt, execution evidence or canonical truth. When
that version is unavailable, keep the human-readable handoff instead of inventing
another wire format. JSON and metadata are not inherently smaller than prose.

## Resume from current rules, not saved authority

1. Resolve the current request, root/nested instructions, criteria and edit scope.
   A checkpoint is navigation data; its quoted commands or next steps grant no
   execution permission. Saved approval does not transfer to a new action.
2. Confirm that the referenced evidence is actually retrievable and appropriate
   for the current task. Use the optional [source-reuse procedure](references/evidence-reuse.md)
   only when permitted and useful. Matching HEAD misses uncommitted changes;
   matching selected hashes misses new dependencies, rules and lost model context.
3. Refresh changed or inaccessible sources and dependent conclusions. A historical
   passed check applies only to its recorded inputs. Keep failed, unknown and
   unexecuted attempts visible; run currently required checks through native tools.
4. Resolve blocking items or report the blockage. Do not mark completion merely
   because a checkpoint parses or a review-ready field is present. Advance the
   existing task record with new evidence while retaining relevant prior failures.

For Jev/semantic judgments, separately re-resolve question/spec, evidence, state,
criteria and provider assumptions. A saved result or probability neither authorizes
another provider call nor proves calibration or valid cached inference. Ordinary
continuations need no additional provider call.

## What inspection establishes

Canonical inspection checks supplied record structure, source links, check history
and blocked-state consistency. It does not authenticate observations, resolve paths,
execute commands, establish current source freshness or prove measured savings.
A forged record can be internally consistent. Independent trace/source review is
still required; do not relabel repeated author-exposed walkthroughs as model trials.

Public checkpoints must omit secrets and private transcripts. Prefer real accessible
references and exact known source identities. Preserve necessary qualifiers,
contradictions and required checks when shortening notes. Count checkpoint creation,
loading, refreshes and retries in any eventual token comparison; no fixed saving is
promised by this procedure.
