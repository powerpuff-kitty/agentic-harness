# Skills-first delivery and evidence gates

Applies to the P0 decision-guidance and context-efficiency workstreams (#105/#114). This is an acceptance guide, not a new manifest, mandatory per-task artifact or runtime dependency. Procedures and evaluator implementation remain owned by `agentic-harness-agents`; canonical Decision Kernel schemas are unchanged.

## Gate 1: usable standalone guidance

A user must be able to copy the whole reviewed skill directory and retain its required references without the full collection or a Harness executable. Applicable project instructions remain required inputs, not embedded replacements. The current-agent path must not require TypeSafe credentials or claim to be Jev inference. A task explicitly requiring a real unavailable provider must abstain instead of substituting silently.

The selected procedure must have a narrow trigger, bounded default body, conditional local guides and explicit completion/approval limits. For nontrivial resumed work, a compact handoff may retain task scope, accepted decisions, actual source identities (including changed working-tree files), observed checks, unresolved evidence and next steps. It is optional and never grants approval or makes stale evidence current.

Efficiency must also work inside ordinary planning, documentation and review skills. Do not require every task to load a separate optimisation or decision skill first. Preserve each procedure's trigger and specialist boundaries, and put its relevant freshness, diagnostic and handoff rules directly in its concise entrypoint. Changed shared definitions may require dependent callers, screens or tests even when the diff is small. A narrower working set must not hide a wider impact.

## Gate 2: portable bytes and preservation

The companion repository's documentation-bundle validator must preserve required files and the MIT notice, reject missing/undeclared documents and detect byte changes. Verify sealed archives without reading the original source checkout. Record exact candidate commit and archive digest; a digest is not a signature or trusted-author proof.

No test or packaging run authorises a release or replaces an existing local installation. Project-local and device-global scopes are separate. Review diffs, preserve custom content, and verify host discovery/loading independently. Keep downstream source pins and implementation deferred during this slice.

## Gate 3: comparable observations

Freeze the task, starting source bytes, accepted policies, check implementations and expected outcomes before running either treatment. Hold host/model/settings constant for a context-only experiment; identify changed skill/instruction content separately. Fresh/reset trials avoid prior-answer and conversation contamination. Unknown identity prevents a controlled comparison rather than being guessed.

Retain appropriate raw redacted trace references and independent outcome labels. Record every required check and any additional observed failure, including unexecuted/unsupported states. Missing contrary evidence, an unexecuted check or a failure must prevent a successful optimisation claim even if fewer tokens were reported.

The companion `guidance_comparison.py` helper compares supplied records only. It validates exact specification and source identities, evidence-reference shapes, expected observation fields, check states and complete usage before emitting token arithmetic. It does not open trace references, authenticate a run, prove a source was read, discover omitted calls or execute an agent. Its `optimisation_verified`, `trace_authenticated`, `model_quality_verified` and `billing_savings_verified` fields stay false.

## Gate 4: measured outcomes, not just smaller sources

Count all submitted input/output across retries and auxiliary providers. Tool results already included in model input are not added twice. Count the instruction/skill-loading and reference-disclosure overhead, not only the final prompt. Missing or incomplete usage stays unknown. Source bytes, estimated tokens, observed submitted tokens and billed price are different measurements.

Do not aggregate synthetic grader records with recorded sessions or use a broken baseline as proof of preserved quality. Repeated representative trials, reviewed traces, observed task success and retained failures/variance are required before claiming general quality or token-efficiency improvements. Changing the provider/model is a separately labelled experiment, not evidence for a context-only change.

Source-byte ceilings and unchanged trigger digests can prevent unreviewed entrypoint growth or routing changes in repository validation. They do not test semantic equivalence or model adherence. Record source-size comparisons by exact baseline revision and selected files; a sum across alternative skills is not a per-session token saving or a reason to load all of them. Supporting guides, required checks and counterevidence must not be deleted merely to meet a smaller byte ceiling.

## Current implementation ownership

- Agents #32: decision-intelligence and independently optional TypeSafe guidance.
- Agents #36: agentic-improvement, ordinary skill adoption, source-preserving handoffs and portable documentation bundles.
- Agents #26: supplied-record comparisons now; representative independently reviewed host observations remain separate.

Candidate implementation lives in agents PR #37 and canonical guidance in PR #120. Passing repository validation establishes content/test/packaging properties, not deployment, host enforcement, paid inference or empirical savings. Leave broader roadmap issues open until their actual accepted gates are met.
