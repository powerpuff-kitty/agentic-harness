# Local verification — 2026-09-18

Status: runnable application, deterministic adoption probes and reviewed local execution verified. **Issue #86 remains open**: caller-approved scoped completion is verified in the follow-up below; signed producers and a native-host/model trial remain unverified. The first sections record the earlier adoption baseline; the executor follow-up below uses the corrected CLI.

## Reproduction identities

| Input | Exact identity |
| --- | --- |
| Local platform | macOS x86_64 |
| Node / npm | 26.8.1 / 12.0.2 |
| Vue / TypeScript | 3.5.43 / 5.9.3 |
| Vite / Vue plugin / vue-tsc | 8.3.0 / 6.0.9 / 3.3.11 |
| Playwright / axe integration | 1.63.0 / 4.13.0 |
| Browser | Chromium 153.0.8010.12 (Playwright build 1243) |
| npm lock SHA-256 | `f31d5a926abca33a3816aa3101191d672fe22d03094bd14572198861c596c314` |
| CLI source | `f8a0bbf1a25a5ec2bec5f6857da16956437b3b29` |
| CLI debug binary SHA-256 | `86b8f90302d5f74ed21123ec2ecfbd4847372b5d3cdf722472df7655320845b7` |
| Embedded canonical source | `dc8902e3fcbaf521ec9ada022bf60f7da094e385` |
| Embedded agent procedures | `5fceb09a50222a29ef0c9a52338ba9be9a82e995` |
| Embedded model registry | `3b6635f036d4648dc7b4dc570df24ec1d509da51` |

These source commits are local and unpublished at the time of verification. Fresh remote-only source synchronization cannot retrieve them until publication. The fixture changes no distributed target-project schema or CLI source pins. The unresolved committed fixture lock is deliberately not used as installation evidence.

## Executed checks

From this directory:

```sh
npm ci --workspaces=false --no-fund --no-audit
npm test
npm run build
npx --no-install playwright install chromium
npm run test:browser
python3 tests/adoption.py /absolute/path/to/ah
```

| Check | Observed result |
| --- | --- |
| Unit tests | 4 passed: title limits, URL rejection, duplicates, mutation isolation and independent sessions |
| Production build | vue-tsc and Vite passed; runtime dependency license copied to dist |
| Browser tests | 4 passed: keyboard/focus/filter journey, input recovery, escaped text/link/storage/request boundaries, 320px reflow and axe checks |
| CLI adoption probes | 7 passed: clean source/design, wrong-direction import, narrow/expired exception, raw control/color and exception, incomplete dynamic import, plan drift, installation/adapter preservation |
| Existing architecture gate | Clean graph accepted; seeded wrong-direction and incomplete computed-import graphs rejected |
| CLI regressions | 146 Rust tests passed; formatting and Clippy with warnings denied passed |
| Canonical checks | Catalog structure, architecture registry, CLI schema/evidence compatibility and diff checks passed |

The CLI probes also passed with the same binary copied outside its checkout. Installation preservation first initializes a fresh project, overlays authored fixture content while retaining the generated manifest/lock, then repeats init/upgrade and Codex base/Claude typed-UI adapter sync. It checks exact embedded source identities and byte preservation, including conflict cases. Codex base routing is a native no-op; creating Claude rule files is installation evidence only.

The broad audit returns 1 because this intentionally undeployed fixture lacks standalone CI/operations material. Its architecture/design sections are checked independently. The existing architecture gate does not establish runtime test execution, design compliance or freshness.

Browser tests initially passed on port 4173. A later clean-install run correctly failed when an unrelated server occupied that port. The fixture now uses configurable port 43186, refuses server reuse, and the full browser suite passed again. No unrelated process was stopped.

## Bug found and fixed

The original CLI accepted computed `import(name)` as complete architecture evidence. The fixture's negative probe failed, leading to the CLI commit above: computed identifier/interpolated targets now produce source-line coverage gaps. They do not invent graph edges. A parser unit test and executable CLI regression protect this behavior.

## Remaining completion gates

- CLI #55 / draft PR #60 has local executor corrections and the trial below. The later follow-up verifies caller-approved imported completion and rejects post-invocation source changes. Signed producer authentication remains deferred.
- Run an actual native coding-host/model trial with delivered context, an implementation change and recorded accept/reject evidence. Neither adapter installation nor this Codex-authored fixture proves host effectiveness.
- Observe Linux CI after publication; other operating systems/browsers, screen-reader/zoom testing, full accessibility review and performance budgets remain unverified. Axe checks in three states are not a WCAG compliance certification.
- The layered profile does not enforce component-versus-view ownership within presentation, external Vue imports into domain, or semantic logic placement. The design checker does not prove every token use. Those gaps remain explicit review obligations.
- Changes are local; no issue status, remote branch, pull request or deployment was published by this work.

Tool references: [Vite setup/build](https://vite.dev/guide/), [Playwright configuration](https://playwright.dev/docs/test-configuration). Project rules and acceptance remain in `.agentic/`, not in these external references.

## Executor follow-up

CLI source `283817f` passed this fixture through the #55 executor with #61 ledger, #62 ownership and #63 budget corrections. Binary SHA-256: `bfede1e7a1b94c8014142e240538a52b80128e2a24d4dfd7c8086181cc6909c0`; embedded canonical source: `e109cabb62521143cb4abe6c475dbe61d6a3d1d6`. Agent and model pins match the baseline above.

```sh
python3 tests/execution.py /absolute/path/to/ah --report /tmp/reading-list-execution.json
```

All four declared native-Node commands passed: unit, types, build and browser. All direct children were reaped; macOS reported inspected `no-live-group-members` cleanup. Total invocation was 39,113 ms, including 20,536 ms of review/revalidation. A changed source refused the old approval digest; an absent native tool failed preparation. Global `completion_verified` stayed false.

The fixed synthetic trial copies source into a temporary project, checks exact authored argv before approving that trial, and links preinstalled dependencies. It is not approval automation for arbitrary projects. Installed transitive dependency bytes and runtime versions are not authenticated by the executor. Full CLI validation passed 174 Rust tests, Clippy, formatting, canonical schema checks and copied-binary candidate probes. These remain local macOS x86_64 results; no remote CI or native-host effectiveness claim is made.

## Caller-approved completion follow-up

The owner selected explicit caller-approved report digests first, signed producers later (ADR-010). The updated `tests/execution.py` ran all four app checks, saved the run and an exact-digest evidence manifest outside declared inputs, and obtained `check-completion` for `scope:declared-checks-and-required-controls` with `producer_authenticated:false`. Changing source after that run rejected the same approved manifest. The original check-run's completion field and this trial's whole-project completion remain false.

CLI implementation `1f08b82`; 190 Rust tests, Clippy/formatting, actual schemas and copied-binary candidate validation (25 completion cases) passed. Tested binary SHA-256: `a5ab1faca2e0741496eb47049eefad5328c6d23c271f2d3496b70a01ea44f68c`; canonical pin `eac2d48`, agents pin `7e7d44e`. Run duration: 23,678 ms. This fixture declares no required governance controls; it does not fabricate host evidence. Separate synthetic CLI probes cover required governance claims and producer/reference bindings. The synthetic harness approves only its fixed authored artifacts, not arbitrary imported reports.

These are local macOS x86_64 results. Signed producers, cross-platform CI and native coding-host/model verification remain outstanding, and #86 stays open.
