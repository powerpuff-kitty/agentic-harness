# Assisted adoption trial

The owner confirmed Claude is unavailable. Claude authentication is **not an adoption prerequisite**. The default route uses the existing coding-agent session, without starting a separate host, accessing credentials or requiring another account.

The task changes only `src/presentation/views/ReadingList.vue`: implement the unread counter described in the disposable project's `.agentic/DESIGN.md`. Preparation is deterministic and never launches a model.

## Current-session route

```sh
python3 native-host/prepare.py /absolute/path/to/ah /new/trial-directory --host current-session
```

Preparation initializes a fresh minimal web-app harness, retains actual manifest/lock provenance, overlays authored application truth and adds an independent browser acceptance test. It does not install or invoke Claude. The existing session explicitly reads `AGENTS.md`, the context map, manifest and relevant project rules, then edits the one allowed file.

`trial.json` records the CLI hash/source pins, file inventory, allowed edit and prompt. Separate-host argv, host version, API budget and supervisor timeout are null in current-session mode: the active session has no separately launched process or independently observed billing/timeout receipt. Never attribute an installed Codex CLI version to a session that did not run through that CLI.

Before editing, build the baseline and run `npm run test:browser -- tests/browser/native-host.spec.ts`; it must fail because the unread status is absent. After the edit, compare all starting-file hashes and dependency links **before** running changed code. Reject changes outside the permitted Vue file, including tests, policies, context and dependencies. Generated test/build output is separate from authored-file comparisons.

Then run `npm test`, `npm run build`, all browser tests, `python3 tests/adoption.py /absolute/path/to/ah` and `python3 tests/execution.py /absolute/path/to/ah --report /outside/project/execution.json`. The executor probe approves only its fixed synthetic policy/report bytes; it is not approval for arbitrary project commands.

## Recorded assisted Codex outcome

See [the observation](2026-09-18-codex-session.json) and [the exact application patch](2026-09-18-codex-session.patch). The existing Codex session explicitly read the context and authored this change. The baseline failed; the changed app passed acceptance. Deterministic checks and scoped completion evidence are recorded separately in the observation.

This is one assisted implementation run, not a blinded or comparative evaluation: the session already had fixture/reference context. There is no independent host/model version or billing receipt. Explicit context reads are observed; automatic native loading, scoped-rule selection and host enforcement remain unverified. The evidence does not certify Claude compatibility or finish the broader agents #24/#26 evaluation matrix.

The patch can reproduce the changed fixture with `patch -p1 < /path/to/2026-09-18-codex-session.patch` from a newly prepared project. Replaying a patch reproduces application checks, not a new model outcome. The committed baseline app remains unchanged so the negative acceptance test stays meaningful.

## Optional Claude route

`--host claude` retains the earlier preparation recipe for environments that independently provide Claude. It installs the pinned typed-UI adapter and proposes a tool-restricted command with a requested $1 API cap and a 300-second supervisor deadline. It never runs automatically and is not required here. No authentication bypass is implemented.

## Local preflight — 2026-09-18

Preparation used CLI source `f017973` and debug binary SHA-256 `a5ab1faca2e0741496eb47049eefad5328c6d23c271f2d3496b70a01ea44f68c`, with installed Claude Code 2.1.76. The new browser test rejected the unchanged app. An authored reference change passed four domain tests, type/build and all five browser tests. The reference change was then removed; every recorded starting-file hash matched and generated browser/build outputs were removed.

This validates preparation and the acceptance harness only. No Claude model was launched, no model/version was inferred from an alias, and native loading/enforcement remain unverified. At preflight completion, the prepared session awaited explicit separate-agent authorization.

## Authorized attempt — 2026-09-18

The owner authorized the prepared bounded trial. Claude Code 2.1.76 started with configured model `claude-opus-4-6[1m]` and exactly Glob/Grep/Read/Edit/Write available. It exited naturally with code 1 after 198.524 seconds, before the five-minute supervisor deadline, reporting an API 401 authentication error. Its final record had `subtype:success` but `is_error:true`; that is a failure. No actual model response was observed (the only message model was synthetic).

The client reported $0 cost, not independently verified billing. There were no tool calls or observed context reads. Every recorded starting-file hash and the dependency link remained unchanged; no files were added, removed or replaced. No implementation was produced, so post-model application tests were not run. The earlier reference patch was not present and cannot count as model evidence.

Raw transcript/stderr remain local; the linked receipt publishes only bounded metadata and hashes. The owner subsequently confirmed Claude is unavailable and removed it as an adoption prerequisite. No Claude retry or credential workaround is planned. This failed attempt remains historical evidence; Claude loading/enforcement stay unverified. The current-session route above now owns the adoption task evidence.
