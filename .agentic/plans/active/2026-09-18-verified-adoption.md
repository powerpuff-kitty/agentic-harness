# Verified adoption — issue #86

Status: runnable fixture, local deterministic/browser verification and corrected executor trial complete; caller-approved imported completion and post-invocation freshness verified locally; assisted Codex task completed; automatic native loading/enforcement unverified and signed producers deferred.

The [reading-list fixture](../../evals/fixtures/adoption/reading-list/README.md) implements the accepted session-only Vue/TypeScript scenario. Its [verification record](../../evals/fixtures/adoption/reading-list/VERIFICATION.md) carries exact tool/source identities, reproducible commands, observed passes and coverage limits.

Completed locally:

1. Domain validation, session-service API, Vue view, shared controls and semantic tokens.
2. Project-selected architecture/design configuration and explicit enforcement gaps.
3. Domain/build/browser checks, including input/link handling, keyboard focus, 320px and automated accessibility.
4. Disposable CLI probes for clean/seeded checks, scoped/expired exceptions, incomplete analysis, review-digest drift and authored-file preservation.
5. CLI fix for computed-import false completeness, with parser/executable regressions and full existing suite validation.
6. Catalog validation coverage and remote CI for the runnable app pass; see the published candidate record.
7. Local CLI `283817f` integrates the #61 ledger and corrects #62 ownership and #63 budgets; 174 Rust tests and copied-candidate checks passed.
8. The fixture passed four reviewed executor commands, with direct-child reaping and stale-review/missing-tool refusal. The execution report's `completion_verified` remains false.
9. CLI `1f08b82` adds caller-approved `checks complete`; 190 Rust tests, actual schemas and copied-candidate validation passed (25 completion cases). The app trial accepts a separate scoped verdict and rejects it after source changes.

Current delivery and remaining work:

1. Published catalog #112, agents #35 and CLI #83 are draft PRs awaiting review/merge. The [candidate record](../../docs/testing/2026-09-18-verified-adoption-ci.md) records successful platform CI, downloaded artifacts and current-input completion checks.
2. The owner confirmed Claude is unavailable and removed it as a prerequisite. The [assisted current-session trial](../../evals/fixtures/adoption/reading-list/native-host/README.md) uses existing Codex context/tools without launching another agent or accessing credentials. Only the permitted Vue view changed. Baseline acceptance failed; 4 domain tests, type/build, 5 browser tests, 7 adoption probes and the four-command executor/scoped-completion/drift sequence passed. The patch and sanitized observation are committed separately from the unchanged baseline app.
3. This is assisted task evidence with explicit context reads, not a blinded benchmark or independent native-loading test. Exact host/model version and billing are unknown. Automatic loading/enforcement and broader agents #24/#26 acceptance remain unverified. Claude-specific compatibility is optional/unavailable here, not an authentication repair gate for #86.
4. Review the demonstrated scope and evidence before closing #86. Signed producers remain deferred by owner decision; the verdict stays scoped and caller-approved.

Rollback is a normal reviewed revert of fixture/CI files and the isolated CLI parser correction. No installed user project or production data was changed. The original context-only #84 fixture remains intact.

Current board ownership, combined-main reconciliation and finishing order are recorded in the [roadmap reconciliation](2026-09-18-roadmap-reconciliation.md).
