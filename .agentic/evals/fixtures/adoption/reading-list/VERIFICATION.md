# Local verification — 2026-09-18

Status: runnable application and deterministic adoption probes verified locally. **Issue #86 remains open**: this record is not executor-generated completion evidence or a native-host/model trial.

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

- CLI #55 / draft PR #60 still own reviewed execution, process cleanup, deadlines/budgets, outcome ledger integration and stale completion rejection. The fixture only declares checks and verifies planning digests. Missing-tool execution outcomes remain part of that executor integration.
- Run an actual native coding-host/model trial with delivered context, an implementation change and recorded accept/reject evidence. Neither adapter installation nor this Codex-authored fixture proves host effectiveness.
- Observe Linux CI after publication; other operating systems/browsers, screen-reader/zoom testing, full accessibility review and performance budgets remain unverified. Axe checks in three states are not a WCAG compliance certification.
- The layered profile does not enforce component-versus-view ownership within presentation, external Vue imports into domain, or semantic logic placement. The design checker does not prove every token use. Those gaps remain explicit review obligations.
- Changes are local; no issue status, remote branch, pull request or deployment was published by this work.

Tool references: [Vite setup/build](https://vite.dev/guide/), [Playwright configuration](https://playwright.dev/docs/test-configuration). Project rules and acceptance remain in `.agentic/`, not in these external references.
