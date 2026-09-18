# Verified adoption — issue #86

Status: runnable fixture, local deterministic/browser verification and corrected executor trial complete; caller-approved imported completion and post-invocation freshness verified locally; signed producers and native-host outcomes pending.

The [reading-list fixture](../../evals/fixtures/adoption/reading-list/README.md) implements the accepted session-only Vue/TypeScript scenario. Its [verification record](../../evals/fixtures/adoption/reading-list/VERIFICATION.md) carries exact tool/source identities, reproducible commands, observed passes and coverage limits.

Completed locally:

1. Domain validation, session-service API, Vue view, shared controls and semantic tokens.
2. Project-selected architecture/design configuration and explicit enforcement gaps.
3. Domain/build/browser checks, including input/link handling, keyboard focus, 320px and automated accessibility.
4. Disposable CLI probes for clean/seeded checks, scoped/expired exceptions, incomplete analysis, review-digest drift and authored-file preservation.
5. CLI fix for computed-import false completeness, with parser/executable regressions and full existing suite validation.
6. Catalog validation coverage and a CI job for the runnable app (job not yet observed remotely).
7. Local CLI `283817f` integrates the #61 ledger and corrects #62 ownership and #63 budgets; 174 Rust tests and copied-candidate checks passed.
8. The fixture passed four reviewed executor commands, with direct-child reaping and stale-review/missing-tool refusal. The execution report's `completion_verified` remains false.
9. CLI `1f08b82` adds caller-approved `checks complete`; 190 Rust tests, actual schemas and copied-candidate validation passed (25 completion cases). The app trial accepts a separate scoped verdict and rejects it after source changes.

Next dependencies, in order:

1. Review the local CLI #55 / PR #60 corrections across Linux/macOS and retain their explicit cleanup/platform limits. GitHub issues #55/#61–#63 and #86 now record local progress and are In progress; remote source/PR state remains unchanged.
2. Caller-approved imported completion is now implemented and tested under ADR-010: exact manifest/report/reference binding, current review equality, recomputed outcomes and required governance evaluation. The app trial accepts a saved run and rejects it after source changes. Signed producer authentication is deferred; the scoped verdict is not whole-project readiness.
3. Exercise native context delivery and a real host/model implementation task. A [bounded Claude trial](../../evals/fixtures/adoption/reading-list/native-host/README.md) is prepared: real init + typed-UI adapter, one permitted Vue edit, a $1 requested API cap and 300-second supervisor deadline. The owner authorized one run: Claude Code 2.1.76 exited with API 401 authentication failure after 198.524 seconds, client-reported $0, no tools or file changes. The [observation](../../evals/fixtures/adoption/reading-list/native-host/2026-09-18-observation.json) records the failure. Authentication must be repaired before retry; preparation/reference tests are not model evidence and native loading/enforcement remain unverified.
4. Publish only when authorized, observe CI and then reconcile the board against executed evidence. Do not close #86 early.

Rollback is a normal reviewed revert of fixture/CI files and the isolated CLI parser correction. No installed user project or production data was changed. The original context-only #84 fixture remains intact.

Current board ownership, combined-main reconciliation and finishing order are recorded in the [roadmap reconciliation](2026-09-18-roadmap-reconciliation.md).
