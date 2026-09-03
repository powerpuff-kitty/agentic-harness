# Release Review Skill

Use before declaring a feature, fix, or refactor complete.

## Review sequence

1. Re-read the task and applicable source-of-truth docs.
2. Inspect the diff for unrelated changes.
3. Run tests, type checks, linting, build steps, and applicable evals.
4. Check error, empty, loading, permission-denied, timeout, and partial-failure behavior where relevant.
5. Check observability for important new failure modes.
6. Check security implications and data migrations.
7. Verify docs and ADRs reflect durable changes.
8. List remaining assumptions, known limitations, and follow-up work.

Never hide failing checks or unresolved risks behind a generic completion statement.
