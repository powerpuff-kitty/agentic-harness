# Audit realignment: finish a verified workflow

Date: 2026-10-11. Tracking owner: [#87](https://github.com/powerpuff-kitty/agentic-harness/issues/87).
This plan supersedes the delivery order in the [September plan](audit-remediation-2026-09-12.md),
not its historical evidence or safety boundaries. It is not release approval.

## Priorities and ownership

Decision/Jev work #105 and context/token efficiency #114 remain P0. Canonical
contracts/reference tools stay here, reusable procedures stay in
`agentic-harness-agents`, and deterministic product mechanics stay in
`agentic-harness-cli`. Current implementation focuses on canonical correctness and
status consistency; downstream runtime rollout is a separately reviewed batch.

Do not create another agent host, provider adapter, memory store or parallel rule
system merely because the existing workflow is not yet complete. Preserve the
original SEO/GEO, design, quality and language requirements in their existing issues.

## Batch 1: correctness and truthful delivery

| Work | Tracking | Boundary |
| --- | --- | --- |
| Strict evidence JSON/numeric input | #196 | Shared local helper and token-economics integration; no blanket consumer migration |
| Revision-bound capability status | #197 | Generated source-review snapshot; consumer/host/release evidence remains separate |
| Shared adversarial consumer conformance | #198 | Existing contracts and actual consumers; no untested pin promotion |

The first implementation adds strict JSON handling and its regression tests, a
repository-local capability snapshot/generator with exact drift checking, and routes
from the README. The snapshot deliberately records reviewed historical source,
including the older CLI catalog pin and command-documentation discrepancy. See
[capability status](../docs/project/capability-status.md) and
[strict input semantics](../docs/project/strict-json-inputs.md).

These changes alone do not finish #197's consumer command synchronization or #198's
cross-language conformance runner. The Jev epic remains open; existing hosted CLI
transport must not be reimplemented as though absent.

## Batch 2: one supported adoption/change/verification loop

Connect accepted project context, a supported host, a bounded change, actual checks
and current evidence. Retain the delivered scope of #84/#85/#86 and historical POSIX
execution tests rather than relabeling them as a new full-host trial.

Architecture #176/#75/#98 connects declared rules to observed source and one stable
rule identity across diagnostics, agent context and supported enforcement adapters.
Quality #102/#104 connects project-native commands to executed findings and
changed-code ratchets. Design #66/#38/#62 adds a small rendered viewport/state loop
and explicit human-review gaps before expanding export backends.

Installation, conflict-preserving upgrades and release evidence remain under CLI
#50/#56/#57. Host scope/loading and procedure depth remain under agents #24/#25.
No merge, release, credential access, deployment or workflow redesign is implied.

## Batch 3: measured outcomes and efficient reuse

Reuse #115/#116/#117/#118/#137/#171 for explainable context, safe incremental reuse
and invalidation. Changed paths should map through #176 to affected capabilities,
contracts, mandatory context and required checks. Changed source, task, rules,
configuration, question/provider or compiler identities require affected evidence to
be re-evaluated. Missing dependency coverage requires broader review, not a pass.

Use existing decision/calibration work #105/#109/#110 for advisory routing where it
outperforms a deterministic or current-agent baseline. Keep mandatory evidence and
consequence permission outside probabilistic decisions.

Agents #26/#32/#36 own repeated matched trials. Retain failures and retries; account
for context acquisition, model input, tool output, model output, latency, cost,
manual correction and acceptance checks. Fixture-byte compression is not measured
model-token savings. Unknown channels remain unknown.

## Completion bar

A named compatible combination can be installed into an existing repository, loaded
by a supported host, used for a bounded change, checked against current requirements,
and upgraded without losing authored truth. Invalid, stale, missing or unexecuted
evidence cannot produce an unwarranted success verdict. Any efficiency claim needs
representative outcome and whole-task cost evidence.

Issue bodies, review branches, merged source, tested consumer compatibility, host
verification and released artifacts are distinct states. Keep broad epics open until
their accepted scope is delivered. Updating GitHub issues does not update Projects
fields automatically. Historical status documents are not current readiness reports.
