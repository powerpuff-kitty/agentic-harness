# Verified-adoption published candidate — 2026-09-18

The owner authorized branch publication and draft PRs, excluding merge/release. The published review set is [catalog #112](https://github.com/powerpuff-kitty/agentic-harness/pull/112), [agents #35](https://github.com/powerpuff-kitty/agentic-harness-agents/pull/35) and [CLI #83](https://github.com/powerpuff-kitty/agentic-harness-cli/pull/83). Original CLI #60 now points to the corrected candidate and retains its review history.

## Exact candidate and CI

CLI head: `d6e34792c8235c987d838775fdba4a029dcd9d7d`. Tested/packaged PR merge: `2d8deab3ae5c600e430cc1e3646870819256ca0d`, combining this head with main `8ee4960c66ad121b416dda4f4c4bd194cc1511ce` (Decision Kernel replay). Do not relabel those artifacts as another commit or a release.

Embedded pins: catalog `6b03603e9f0cfdb8348f5be4442622f8e8cdab0d`, agents `7e7d44e9f9d7e4579048c4e8c1073243f6bcf61c`, registry `3b6635f036d4648dc7b4dc570df24ec1d509da51`. Both newly published upstream commits were independently confirmed reachable through GitHub. CI fetched its sources remotely.

- [Catalog CI](https://github.com/powerpuff-kitty/agentic-harness/actions/runs/35389701698) passed contracts/catalog validation and the actual Vue fixture's domain/build/browser checks for head `4f15fc4`.
- [Agents CI](https://github.com/powerpuff-kitty/agentic-harness-agents/actions/runs/35389702769) passed 30-skill/routing/distribution validation, 23 adapter tests, 34 bundle tests, 13 static design scenarios and actual collection ZIP retention/integrity checks for head `7e7d44e`. These are not model outcomes.
- [CLI CI](https://github.com/powerpuff-kitty/agentic-harness-cli/actions/runs/35389912962) passed all nine jobs: four platform builds, four downloaded-candidate checks and dependency review. Rust tests: 201 each on Linux and both macOS architectures; 194 on Windows. Formatting, Clippy, TypeScript fixtures, actual output/schema probes, attribution and packaging checks passed. Linux also passed downloaded-candidate verification with networking disabled.
- Fresh downloaded RustSec evidence reports zero known vulnerabilities and no warnings. SPDX inventory has 123 packages and no missing license metadata. Metadata inventory is distinct from the separately verified authored notices.

The first CLI run failed Linux Clippy on a conditional that simplified to a boolean literal outside macOS. Commit `d6e3479` preserves behavior while simplifying the platform branch; local formatting, Clippy and four process ownership/cleanup tests passed. The superseded run was canceled, and the complete corrected matrix above passed. No check was disabled or weakened.

## Downloaded artifact verification

All four archives were downloaded, checked against their SHA-256 sidecars, and validated with required authored-license notices. Provenance source pins and tested merge identity agree across platforms. Every downloaded evidence report's binary hash and version match its actual asset.

Each POSIX candidate records 85 main invocations, 17 onboarding probes, 20 adapter probes, 16 skill-delivery probes, 17 context-selection probes and 25 completion cases. Counts describe overlapping report sections and are not summed into an invented total. Windows records 58 main invocations and an explicit unsupported execution/completion result, not a positive completion claim.

The downloaded macOS x86_64 binary independently passed the copied-binary suite locally, including all 25 completion cases. Other platform execution is established by the remote CI jobs, not local execution on incompatible hardware.

| Asset | Binary SHA-256 | ZIP SHA-256 |
| --- | --- | --- |
| ah-linux-x86_64 | `fcd3b829f4963c14862ce606fd6869fb1f615b34aaecfd11f240c34afc900cbb` | `9d56ae9d130673658f31076ac13a5e50cc63a7abd93f7b1f78d47472d6c651d4` |
| ah-macos-arm64 | `b7555820e12fe73f34609a803bdf8d4599a5913099ddb2e5305a7c0139a44645` | `7210c9ce4a28ae1a894e2577661de6121bcb488f0b9251dd33d2bb81b03325a2` |
| ah-macos-x86_64 | `e49d5c71b7153db17a7806ceb2a5267e3fde57334812e644a9e8d8bb1bbb8e3d` | `9d193de1b170b70ae5ae890bda3793dc258e427692c5b6417821d8db16b162a1` |
| ah-windows-x86_64.exe | `64da06d9efb4eff3cf6dd8a62875cacb78158b736e83d98f6a5430f906d93a8a` | `d367d3ce15c82485785f8532aa668edecf3e9e3a98b5664fe5a35112262f96b3` |

## Remaining delivery gates

The PRs remain drafts, unmerged. Canonical #84/#85 and CLI #55/#61–#63 now have published candidate/platform evidence and await review/merge against their acceptance criteria. #87 remains the coordinating roadmap. No issue is closed solely by CI success.

Canonical #86 and agents #24 still lack successful native-host acceptance: the authorized Claude trial failed authentication before tools/edits. Agents #24/#25/#26 retain their broader managed-operation, procedure and repeated model-evaluation scope. Explicit caller-approved digests remain the accepted trust mechanism; signed producers are deferred and `producer_authenticated` remains false.

CLI #50's earlier missing-platform and missing-current-RustSec evidence gaps are resolved for this exact candidate. This record does not itself complete all release/production-core review criteria or authorize publication of a release. No tag, release or main merge occurred.
