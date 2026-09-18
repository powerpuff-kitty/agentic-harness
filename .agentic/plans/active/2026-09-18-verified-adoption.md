# Verified adoption — issue #86

Status: runnable fixture and local deterministic/browser verification complete; executor and native-host outcome integration pending.

The [reading-list fixture](../../evals/fixtures/adoption/reading-list/README.md) implements the accepted session-only Vue/TypeScript scenario. Its [verification record](../../evals/fixtures/adoption/reading-list/VERIFICATION.md) carries exact tool/source identities, reproducible commands, observed passes and coverage limits.

Completed locally:

1. Domain validation, session-service API, Vue view, shared controls and semantic tokens.
2. Project-selected architecture/design configuration and explicit enforcement gaps.
3. Domain/build/browser checks, including input/link handling, keyboard focus, 320px and automated accessibility.
4. Disposable CLI probes for clean/seeded checks, scoped/expired exceptions, incomplete analysis, review-digest drift and authored-file preservation.
5. CLI fix for computed-import false completeness, with parser/executable regressions and full existing suite validation.
6. Catalog validation coverage and a CI job for the runnable app (job not yet observed remotely).

Next dependencies, in order:

1. Finish the existing CLI #55 / PR #60 executor work, including #61 ledger integration, #62 process ownership/cleanup and #63 budgets/deadlines. Do not add a competing executor to the fixture.
2. Run the fixture's declared checks through that executor, exercise missing tools and changed inputs, and prove stale completion is rejected.
3. Exercise native context delivery and a real host/model implementation task; preserve separate installed/configured/verified evidence states.
4. Publish only when authorized, observe CI and then reconcile the board against executed evidence. Do not close #86 early.

Rollback is a normal reviewed revert of fixture/CI files and the isolated CLI parser correction. No installed user project or production data was changed. The original context-only #84 fixture remains intact.
