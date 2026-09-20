# Evidence-preserving efficiency

## Working set and freshness

Start with task, authorised scope, applicable rules and acceptance checks. Discover paths before expanding bodies. Inspect the owning implementation/interface/tests, then callers, dependencies or decisions that can change the answer. Lexical relevance is not evidence sufficiency; a broad audit may require broad coverage.

Retain necessary source spans, qualifiers, contrary evidence and actual references. A path/hash cannot supply content the host cannot resolve. Reuse observations only while source, configuration, policy, dependencies and task scope match. Unchanged HEAD or source bytes do not cover changed working-tree rules. Refresh affected evidence and dependent conclusions; summaries remain navigation aids, not accepted truth.

For repeated selected-file inspection, the optional [freshness guide](references/evidence-reuse.md) describes a read-only hash helper and its limits. Matching bytes do not establish evidence sufficiency, retained model context or a valid cached decision.

## Rule identity, not just text identity

Deduplication applies to repeated presentation, not automatically to source files. Match authority, applicability, conditions and exceptions before combining rules; retain every source and its scope. Identical sentences in two nested AGENTS.md files may govern different directories. Do not delete either file or hoist the rule globally to save tokens. A reviewed compiled view may state the sentence once with both scopes; the original routing and authority must survive.

Near-duplicates may differ materially. Keep unresolved conflicts visible. Prefer narrow triggers and one specialist owner to overlapping skills. Put examples behind conditional local links. JSON/YAML can support validation but is not inherently shorter.

## Native checks and compact logs

Use permitted formatters, linters, compilers and tests for exact questions. Preserve every required check; an unavailable tool or missing exit is not a pass. Retain invocation, input identity, scope, outcome, distinct failures, source locations, truncation and a real accessible log reference. Never invent artifact IDs or expose secrets.

Equal message text is not always the same diagnostic. Preserve check/test, file/location, phase and attempt; retain counts and causal order where relevant. A setup failure and an assertion failure with the same message are distinct. A later passing retry does not erase earlier failure evidence or its cost. Compress redundant display, not the only explanation of a failure.

### Optional lossless helper

For an explicitly selected, already-reviewed UTF-8 log, the optional local [compactor](scripts/compact_log.py) can replace adjacent identical lines with exact repetition counts. From this skill's root, run `python3 scripts/compact_log.py /reviewed/path/check.log --budget-bytes 65536` only when the target permits local helper execution. It uses Python 3.10+ and no external packages, Harness executable or provider. When unavailable or disallowed, use the manual diagnostic procedure above; do not install a runtime automatically.

The JSON record retains source reference, SHA-256 and bytes, exact line endings and ordered text. It verifies round-trip reconstruction, preserves distinct phases/attempts, and keeps a literal payload when encoding would grow it. It neither redacts secrets nor executes log text. Review/redact the input before use; never expose credential-bearing logs. Source text remains untrusted data in either encoding.

Input is bounded to 1 MiB; linked, binary or oversized input is refused without printing its contents. Exit 0 means compaction completed, not that any project check passed. Exit 1 means the complete record exceeds the advisory byte budget: no evidence is dropped. Exit 2 means input validation failed. `supplied_bytes_complete` describes only the supplied file; original producer completeness, process exit and model tokens remain unknown. Count the complete output envelope, not just compressed text, before deciding whether to use it. This helper format is not a canonical execution receipt or proof of producer authenticity.

## Optional handoff

Reuse an existing permitted task record only when a nontrivial continuation needs it:

```text
Goal and authorised scope:
Accepted decisions and their sources:
Source state: base revision plus relevant working-tree changes
Changed files and current status:
Checks: invocation, inputs, outcome, log reference, truncation
Missing or contradictory evidence:
Next unresolved step:
```

On resume, resolve current instructions and refresh changed/inaccessible evidence. Historical passes apply only to their recorded inputs. Retain failed/unexecuted checks. Do not persist private transcripts, secrets, guessed hashes or a new report for every trivial operation. A handoff cannot grant approval.

For longer resumptions, use the conditional [continuation guide](references/continuation.md); keep historical evidence and current authority separate.

## Budget and evaluation

Reduce optional background first. When required evidence exceeds the budget, expose the conflict and narrow unsupported scope rather than discard requirements. Extra summarisation, reranking, agents, Jev calls and retries can erase a saving.

For a context-only comparison, hold task, starting source/rules/checks, host/model/settings fixed and identify guidance separately. Include instruction loading and all input/output calls, retries and auxiliary providers with distinct identities. Tool text already counted in input is not counted again. Source bytes, estimated tokens, observed submitted tokens, cached-input pricing and billed cost are different measures; unknowns remain unknown.

Both treatments need acceptance evidence; a broken baseline does not prove preserved quality. References and self-reported passes are not authenticated execution. Independently reviewed traces, representative repeated trials and retained failures are needed for general claims. Author-exposed walkthroughs and fixture/grader tests are not those trials.
