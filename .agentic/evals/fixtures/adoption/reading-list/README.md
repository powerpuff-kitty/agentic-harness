# Synthetic reading list: runnable adoption fixture

This Vue/TypeScript application is the runnable reference for [#86](https://github.com/powerpuff-kitty/agentic-harness/issues/86). One reader adds titles and optional HTTP(S) links, toggles read status and filters the session list. Reloading clears it. No account, server, external service, persistence or TypeSafe inference is needed.

Run from this directory, independently of any parent JavaScript workspace:

```sh
npm ci --workspaces=false --no-fund --no-audit
npm test
npm run build
npx --no-install playwright install chromium
npm run test:browser
npm run dev
```

Node is pinned in `.node-version`; dependencies are exact in `package.json` and `package-lock.json`. On Linux, Playwright may need `playwright install --with-deps chromium`. Missing tools or browser binaries are failures to remedy, not passing evidence.

Browser tests use port 43186 and refuse to reuse an existing server. Set `READING_LIST_PORT` to another available port if needed.

## Harness adoption probes

Use a locally built compatible CLI, then supply its absolute path:

```sh
python3 tests/adoption.py /absolute/path/to/ah
```

The tests print the binary identity and SHA-256, copy this fixture into temporary directories, and exercise clean architecture/design checks, seeded wrong-direction imports, raw controls/literal colors, scoped exceptions, expired exceptions, computed-import coverage, check-plan drift and repeated initialization/upgrade/adapter synchronization. They require the computed-import completeness fix described in `VERIFICATION.md`; an older binary should fail that regression.

These are bounded regression tests, not an alternative check executor. `.agentic/checks.json` declares unit/build/browser commands for the existing CLI planning contract. `ah checks plan . --config .agentic/checks.json` previews and fingerprints them without running or approving them. The CLI #55 executor, execution evidence ledger, stale completion rejection and native host/model outcomes remain outstanding.

Architecture and design configuration express **this fixture's selected rules**. See [the context map](.agentic/README.md) for their rationale and limitations. `ah audit` also reports the fixture's absent standalone CI/deployment/runbook configuration and returns 1; the adoption tests assert the relevant architecture/design sections, not overall production readiness. The parent catalog workflow runs the application tests.

The committed harness lock deliberately remains unresolved: authored context is not installation provenance. Installation/upgrade tests resolve pins in disposable copies and check preservation. The original [context-only example](../../context/reading-list/README.md) remains independently inspectable.

See [VERIFICATION.md](VERIFICATION.md) for exact local evidence and remaining completion gates. Do not close #86 based only on this fixture.
