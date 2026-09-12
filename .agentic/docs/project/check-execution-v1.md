# Explicit local check execution v1

Experimental companion to `check-evidence-v1.md`, implementing the next part of CLI #55. The non-executing check-plan contract remains unchanged. This contract defines a separate host-specific review and a local execution report, not a general-purpose agent runtime or a trusted imported-evidence gate.

## Separate review and execution

`check-execution-settings` explicitly binds each requested executable name to an absolute native executable path, declares the full child environment including PATH, and sets a total execution budget (1..900000 ms). The bindings must exactly cover the executable names in the check policy. Paths, arguments and environment values are local review data and may disclose information: never put credentials in these files or automatically publish them.

Preparing a review starts no subprocess, including version queries. It resolves each tool path, records both the requested and canonical path, fingerprints the exact bytes and permission mode, and identifies the executing CLI binary. Script launcher files are unsupported in this initial slice; bind the native interpreter and pass the script as an explicit argument with appropriate declared inputs. Runtime tool versions remain null/unverified because no version command has been authorized. Byte identity does not imply tool safety or cover every dynamically loaded library or downstream executable.

`check-execution-review` includes the existing plan, settings digest, target absolute path, OS/architecture, tool identities, explicit environment and budget. It always says `inherit_environment: false`, `checks_executed: false`, `execution_permitted: false`. Its approval digest frames, in order: plan review digest, raw settings digest, relative config path, relative settings path, absolute target, OS, architecture, executor binary SHA-256 and compact lexicographically keyed tool-object JSON. The framing algorithm uses the domain `ah-check-execution-review-v1` followed by NUL and length-prefixed fields as defined in the original contract.

Running requires a matching freshly recomputed review digest AND explicit acknowledgment of unsandboxed execution. A plan digest alone is insufficient. Neither flag authenticates an owner against an agent with unrestricted shell access; authorization is an explicit caller decision that a host permission system must mediate when required. No implicit approval is remembered between invocations. A changed source, policy, settings file, tool binding/bytes/mode, host, target or executor invalidates review.

Both policy and execution settings reject duplicate JSON object keys, including escaped aliases. Malformed data and invalid approvals are rejected before execution without echoing file contents.

## Execution behavior and limits

Initial execution backends: Linux and macOS. Windows may produce a review but reports execution as unsupported without spawning commands; equivalent cleanup must be tested before support is advertised.

Commands run sequentially using the exact absolute tool binding and argument array. There is no implicit shell. The inherited environment is cleared and only explicit entries are supplied, including an explicit empty or absolute-component PATH. Working directories are resolved inside the target; no symlink or Windows reparse path is accepted by the existing project-path validator. stdin is disconnected. A shell or interpreter explicitly named by an approved policy is still arbitrary code, not a safe command simply because argv is an array.

On supported platforms each command starts in its own process group. The supervisor polls nonblocking stdout/stderr, bounds captured bytes across both streams, enforces a monotonic per-check deadline constrained by remaining total budget, signals the group on termination, and reaps the direct child. Capture retains at most one extra byte to detect an exceeded output budget. Cleanup has a bounded grace window of 250 ms; scheduling and operating-system calls are not real-time guarantees. Failed cleanup or unreaped direct children cannot be reported as a pass. Normal completion also terminates remaining ordinary descendants in the same group.

This is not a sandbox. Deliberately detached descendants can escape a process group; filesystem/network access and transitive commands are not intercepted. Do not run hostile repositories or untrusted commands with this backend. A sandboxed host is a separate requirement. The supported threat model remains a cooperative, quiescent local project and explicitly reviewed commands.

Recompute source/policy/settings/tool identity before each check and after execution. Detected changes stop subsequent checks and prevent `checks_passed`. Checks that modify declared inputs are therefore unsuitable as passing validation commands. Changes that are reverted between snapshots, undeclared dependencies and malicious concurrent filesystem races are outside this model. The command does not roll back user-code side effects.

## Reports and completion

`check-run` records per-check requested argv/cwd, required flag, outcome, timestamps, monotonic duration, exit/signal status, spawning/reaping and process-group cleanup observations. Outcomes distinguish passed, failed, timeout, output-limit, execution-error, skipped and unsupported. Required checks must pass and reviewed inputs must remain current for `checks_passed: true`. Optional failures remain visible but need not fail that narrow result.

Raw command output is omitted. Reports retain observed byte counts and SHA-256 values, explicitly distinguishing complete streams from observed prefixes. No output files or logs are implicitly written. Even output hashes/lengths and local paths can be sensitive; review reports before sharing. Write redirected reports outside the declared input scope.

All governance requirements remain unverified, and `completion_verified` is always false in this slice. A passing local command set is not producer authentication, freshness after the invocation, enforced host permissions, deployment approval or overall project readiness. Imported report validation and a current-evidence completion gate remain required under catalog #85 and CLI #55. Existing audit/gate meanings do not change.

The execution schema references the existing plan schema. Validators must register the exact pinned `checks.v1.schema.json` as a local resource; contract validation must not fetch schema URLs over the network. Structural fixtures are not execution outcomes. The CLI must separately execute synthetic success/failure, timeout/output-limit, preservation, changed-input and platform-cleanup scenarios.

## Primary API references

Implementation follows Rust's `std::process::Command` argument/environment behavior and Unix `CommandExt::process_group` semantics. Review against the project's pinned toolchain rather than assuming every current documentation API is available.

- https://doc.rust-lang.org/std/process/struct.Command.html
- https://doc.rust-lang.org/std/os/unix/process/trait.CommandExt.html

No new agent loop, automatic production access, host-wide enforcement claim, public internal-consumer reference, workflow redesign or release publication is authorized by this contract.
