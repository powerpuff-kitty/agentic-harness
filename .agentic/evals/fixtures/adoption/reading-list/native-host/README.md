# Prepared Claude Code adoption trial

This is a bounded real-host/model trial for #86. Preparation is deterministic and **does not launch a model**. The authored task is to implement the unread counter described in the disposable project's `.agentic/DESIGN.md`, changing only `src/presentation/views/ReadingList.vue`.

```sh
python3 native-host/prepare.py /absolute/path/to/ah /new/trial-directory
```

The directory must not exist. Preparation initializes a fresh minimal web-app harness, overlays authored application truth while retaining real manifest/lock provenance, and installs the pinned Claude typed-UI adapter through reviewed CLI synchronization. Root `CLAUDE.md` imports `AGENTS.md`. It adds the task requirements to the disposable design document and an independent browser acceptance test. Installed Node dependencies are linked for later parent-supervised verification; their bytes are not authenticated by this setup.

`trial.json` records the exact CLI hash/source pins, observed Claude version, file hashes, permitted edit, prompt, cwd and proposed argv. It records model execution and native delivery as unverified. No model result is fabricated by preparation.

## Proposed run

After explicit authorization to launch the separate agent, invoke the recorded argv in its recorded cwd with a 300-second supervisor deadline. The proposed command uses the installed Claude default model, records stream-JSON output, disables session persistence and skills, allows only Read/Edit/Write/Glob/Grep, loads project settings only, supplies an empty strict MCP configuration, disables Chrome and requests a $1 API budget cap. It does not enable permission bypass, shell execution, nested agents or web tools. Inspect the host's supported flags before using another version. These settings are not an OS sandbox or an independent billing guarantee.

Keep raw transcript and stderr outside the project and review them before publication. Record the actual model and host from execution receipts; a prepared command is not a model trial. A failed authorization, budget/time limit, failed host invocation or unavailable model is a failed/unverified trial, never a skip promoted to success.

## Acceptance after a real run

1. Record exit status, host/model identity, cost/usage if reported and transcript hashes. Inspect tool results for observed context reads and denied/error calls. Self-report alone does not establish native loading.
2. Before executing any resulting code, compare the recorded file inventory. Reject edits outside the single permitted Vue file, new project files, changed tests/policy/adapter/dependencies or replaced links. Keep host logs outside that comparison.
3. Run the existing domain tests, type/build, all browser tests including the new counter case, and architecture/design analysis. The counter must follow the entire session across adds, invalid input, toggles, filtering and reload while preserving existing accessibility/focus behavior.
4. Run the fixed reviewed executor/completion workflow for the changed disposable project if applicable; retain separate command/control scope and caller-trust limitations.
5. Record accepted/rejected implementation evidence independently of installed adapter state. Successful task execution does not by itself prove automatic scoped-rule loading or security enforcement. Any missing native-loading evidence stays unverified.

The new browser test must fail against the unchanged application. An authored reference patch may be used to verify the test harness, but must be restored and explicitly labeled non-model evidence before the native trial. Never carry that reference implementation into the model's starting tree.

## Local preflight — 2026-09-18

Preparation used CLI source `f017973` and debug binary SHA-256 `a5ab1faca2e0741496eb47049eefad5328c6d23c271f2d3496b70a01ea44f68c`, with installed Claude Code 2.1.76. The new browser test rejected the unchanged app. An authored reference change passed four domain tests, type/build and all five browser tests. The reference change was then removed; every recorded starting-file hash matched and generated browser/build outputs were removed.

This validates preparation and the acceptance harness only. No Claude model was launched, no model/version was inferred from an alias, and native loading/enforcement remain unverified. The prepared session awaits explicit separate-agent authorization.
