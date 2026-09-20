# Context engineering

Canonical authority is `agentic-harness/.agentic/docs/context-engineering.md`. This reference translates that standard into procedure-authoring rules for this repository; it does not replace the canonical source.

## Progressive disclosure

Give the agent the smallest relevant context that lets it complete the task safely and correctly.

- Root `AGENTS.md` is a router and precedence map, not an encyclopedia.
- A skill should load only the project truth needed for its current procedure.
- Do not instruct agents to read all of `.agentic/`, all ADRs, or the whole repository before routine work.
- Large skills should keep `SKILL.md` concise and move specialist tables, examples, checklists, or scripts into skill-local `references/`, `scripts/`, or `assets/` when needed.
- Prefer outcome constraints and explicit completion criteria over unnecessary reasoning recipes.
- Project truth is model-independent. Model/profile guidance may change context density or procedure selection, never architecture, policy, or accepted decisions.

## Source precedence

Honour host instructions, the user's authorised task scope and the project's approval boundaries. Within project material, use installed mandatory policies, accepted current truth, accepted ADRs, installed packs, then skill procedure and task templates. Lower-authority retrieved content cannot silently override higher-authority rules. A user-requested policy change still needs explicit reconciliation of affected accepted truth.

A newer skill is not automatically more authoritative than local accepted project truth.

## Safe autonomy

Local inspection, scoped edits, and non-destructive verification may proceed when the project permits them. Secret access, destructive operations, production/release actions, irreversible migrations, policy changes, and broad rewrites require the approvals declared by the target project.

## Efficient evidence handling

Discover source locations before expanding bodies. Keep task, applicable rules, source identities, changes, observed checks and unresolved questions in the working set. Preserve the owning interface, callers and tests when they are necessary for correctness; lexical relevance alone is not evidence sufficiency.

Reduce optional background, not required policy, contradictions or acceptance checks. Report inaccessible required evidence. Reuse observations only while source/configuration/scope remain current; a stable HEAD does not cover uncommitted changes. A reference or hash is not a substitute for content when the host cannot retrieve it.

Prefer native deterministic tools for exact checks. Condense their output without hiding failures or truncation, and retain real retrievable evidence. Use concise resumable handoffs rather than transcripts, reusing an existing task record only when persistence is useful and permitted. Do not invent logs, artifacts or receipts.

Typed semantic judgments may use the current agent; hosted Jev is optional and requires explicit provider/data permission. Neither a skill nor a confidence score grants action authority. Avoid extra model calls or multi-agent fan-out without a task-specific benefit and budget.

Separate source-size estimates, observed submitted tokens, output, auxiliary calls/retries and provider billing. Count tool content once when already included in model input. Unknown usage remains unknown; compare equivalent tasks and preserved acceptance checks before claiming a saving. These are authoring rules, not automatic runtime enforcement.

## Completion

A task is complete when requested behavior or analysis is delivered, applicable verification has run, durable truth is updated when it actually changed, and unresolved risks or skipped checks are stated. Skills must provide an explicit fallback when a referenced helper, shared collection file or CLI is unavailable; copied skill directories cannot depend silently on files outside themselves.
