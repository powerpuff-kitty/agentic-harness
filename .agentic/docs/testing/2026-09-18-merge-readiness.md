# Verified-adoption merge readiness — 2026-09-18

Outcome: the implemented catalog, procedure and POSIX execution/completion slices are ready for review/merge. This is a focused author self-review, not an independent GitHub approval, a complete security audit or a release decision. No new blocking security defect was confirmed in the reviewed paths. The seven candidate-linked issues separate verified implementation from remaining delivery and broader scope below.

## Evidence and scope

Review set: canonical #112, agents #35, CLI #83. [Published candidate evidence](2026-09-18-verified-adoption-ci.md) records exact tested source/pin/artifact identities and successful four-platform CI. The [assisted-session observation](../../evals/fixtures/adoption/reading-list/native-host/2026-09-18-codex-session.json) records the one-file task and its limits. Claude is not required.

Inspected the CLI's `completion.rs`, `check_execution.rs`, `check_inputs.rs`, `execution_budget.rs`, `process_check.rs` and governance bounds, plus agents' minimal-context/completion guidance. Approval is checked against exact manifest bytes before following evidence references; paths reject traversal/links; repeat snapshots and current reviews bind accepted inputs; RunLedger recomputes outcomes. Execution keeps ownership through the final group signal and retains outcomes before later fallible checks. Guidance does not authorize self-approved arbitrary evidence. Existing actual-output rejection probes, native fault tests and candidate artifacts corroborate those specific boundaries.

Do not infer protection against hostile concurrent races, reverted mutations, an unrestricted caller supplying approval flags, detached descendants or uncatchable termination. Process groups are not a sandbox. Signed producer authentication and automatic native host loading/enforcement are not implemented claims. Windows execution stays disabled. No new stress test, live provider call, secret scan or independent penetration test was performed in this review; the existing fresh RustSec and notice reports remain candidate-specific evidence.

## Resolved finding

Low severity, high confidence: trial preparation overlaid the context-only README onto a real CLI installation. It then incorrectly described source pins as unresolved and installed modules as absent, conflicting with the actual manifest/lock. Future prepared trials now describe resolved installation sources and authored overlays accurately. Their pre-edit inventory also records link targets explicitly.

Verified using the downloaded macOS candidate with no host executable on PATH: successful preparation, matching recorded/catalog-agent source pins, actual installed policy/pack files, complete file/link inventory and refusal to overwrite an existing trial. The committed baseline fixture and earlier assisted-session receipt are unchanged. That earlier receipt belongs to its original preparation; it is not relabeled as a rerun with the corrected map. Its manifest was explicitly read and its application/evidence checks remain recorded separately.

## Issue disposition after an approved merge

| Issue | Verified scope | Remaining delivery or scope |
| --- | --- | --- |
| Canonical #84 | Minimal/full selection, authored-file preservation, useful packs, filled example and measurements | Merge the three coordinated PRs |
| Canonical #85 | Independent governance semantics and caller-approved current scoped completion | Merge coordinated contracts/procedures/CLI; signed producers explicitly deferred |
| Canonical #86 | Runnable rules-selected fixture, positive/negative probes, assisted Codex change and scoped completion | Merge/review the demonstrated assisted scope; no automatic-loading or comparative-model claim |
| CLI #61 | Ledger integration, prior-result retention and backend integrity mapping | Merge #83 |
| CLI #62 | Ownership through cleanup/reaping, cancellation/recovery and disabled unsupported execution | Merge #83 |
| CLI #63 | Invocation deadlines, bounded review reads and explicit cleanup/recovery timing | Merge #83 |
| CLI #55 | Published POSIX executor and caller-approved evidence gate | Merge #83; retain its broader Windows execution item as open |

Agents #24/#25/#26 and CLI #50 are not resolved by these merges: their broader host/managed-operation, procedure/evaluation and release-review requirements remain explicit. Canonical #87 is a coordinating roadmap, not a ticket to close just because this slice is delivered.

## Concrete merge proposal

Merge canonical #112 and agents #35 before CLI #83. Prefer normal merge commits for the upstream PRs so the exact tested ancestor pins remain reachable on main without changing the CLI candidate. Do not squash away pinned ancestry or silently repin to untested bytes. Require current checks to remain green and respect repository review/protection rules; do not bypass them. Inspect the resulting main CI and then close only the six scoped issues above whose acceptance is delivered. Keep CLI #55, the roadmap, broader host/evaluation work and release review open.

The owner's earlier approval explicitly covered publishing branches and draft PRs without merging or releasing. Merge approval remains the final action boundary; this review does not infer that approval or authorize a release.
