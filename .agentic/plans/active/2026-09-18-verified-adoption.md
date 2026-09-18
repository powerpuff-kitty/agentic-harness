# Verified adoption — issue #86

Status: runnable fixture, local deterministic/browser verification and corrected executor trial complete; imported completion freshness and native-host outcomes pending.

The [reading-list fixture](../../evals/fixtures/adoption/reading-list/README.md) implements the accepted session-only Vue/TypeScript scenario. Its [verification record](../../evals/fixtures/adoption/reading-list/VERIFICATION.md) carries exact tool/source identities, reproducible commands, observed passes and coverage limits.

Completed locally:

1. Domain validation, session-service API, Vue view, shared controls and semantic tokens.
2. Project-selected architecture/design configuration and explicit enforcement gaps.
3. Domain/build/browser checks, including input/link handling, keyboard focus, 320px and automated accessibility.
4. Disposable CLI probes for clean/seeded checks, scoped/expired exceptions, incomplete analysis, review-digest drift and authored-file preservation.
5. CLI fix for computed-import false completeness, with parser/executable regressions and full existing suite validation.
6. Catalog validation coverage and a CI job for the runnable app (job not yet observed remotely).
7. Local CLI `283817f` integrates the #61 ledger and corrects #62 ownership and #63 budgets; 174 Rust tests and copied-candidate checks passed.
8. The fixture passed four reviewed executor commands, with direct-child reaping and stale-review/missing-tool refusal. `completion_verified` remains false.

Next dependencies, in order:

1. Review the local CLI #55 / PR #60 corrections across Linux/macOS and retain their explicit cleanup/platform limits. GitHub issues #55/#61–#63 and #86 now record local progress and are In progress; remote source/PR state remains unchanged.
2. Integrate authenticated imported-evidence freshness/completion rejection. Local CLI `7d49d13` adds a pure governance evaluator (190 Rust tests passed, including 16 evaluator tests; formatting/Clippy/catalog passed). It validates caller-supplied trust bindings, references, identities, age and exact required capabilities. It does not acquire trust or current filesystem snapshots and does not verify completion. The first consuming command still needs an explicit trust-mechanism decision and execution-report validation.
3. Exercise native context delivery and a real host/model implementation task; preserve separate installed/configured/verified evidence states.
4. Publish only when authorized, observe CI and then reconcile the board against executed evidence. Do not close #86 early.

Rollback is a normal reviewed revert of fixture/CI files and the isolated CLI parser correction. No installed user project or production data was changed. The original context-only #84 fixture remains intact.
