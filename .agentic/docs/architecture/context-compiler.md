# Context Compiler contract

The Context Compiler turns a task plus current repository evidence into a bounded, explainable **plan** for model context. It is a selection layer, not a new source of project truth and not proof that an AI task will succeed.

The public machine contract is `catalog/schema/compiled-context-plan.v1.schema.json`.

## Boundary

A compiler may use deterministic repository indexes, current project routes, rules, diffs, summaries, diagnostics, events and selected context packs. The plan records the exact source path and SHA-256 digest of every candidate item that it ranks. Generated summaries and analysis remain generated evidence unless the project explicitly promotes a decision into canonical truth.

The first supported disclosure levels are router, summary, symbol, file and artifact reference. A planner can begin with compact summaries and progressively disclose a symbol or full file only when the task requires it.

## Authority and budgets

Authority is independent from relevance. Project policy and accepted project truth can be mandatory even when lexical or semantic relevance is low. A budget optimizer must not silently remove a mandatory item. If required context alone exceeds the input budget, the plan stays explicit and reports `over_budget: true`; callers decide whether to raise the budget, reduce the task, or stop.

Input, tool-output and model-output budgets are separate. `estimated-tokens` are estimates unless a later evidence artifact records observed provider usage. The v1 contract does not equate a portable estimate with provider billing.

## Selection signals

Each item can expose relevance score and scoring method, confidence when meaningful, freshness (`current`, `stale`, or `unknown`), dependency distance when available, and estimated token cost. Unavailable signals remain null or unknown rather than being invented. Different scoring methods are not directly comparable merely because both produce numbers.

## Stable and volatile context

Stable context is expected to change relatively infrequently, such as project policy or accepted architecture truth. Volatile context includes current source, diffs and diagnostics. This classification supports cache design and progressive disclosure; it does not grant authority.

## Context packs

`active_context_packs` lists packs activated for the task. An item may reference only an active pack. Installing a pack does not make every pack relevant to every task.

## Coverage and completion

Coverage records discovered, supported, unsupported and unreadable files plus unavailable required context and scan errors. Missing required context or scan errors prevents complete coverage. A complete context plan still means only that the planner completed its declared selection procedure; it does not establish code correctness, test success, security or production readiness.

## Determinism and provenance

For a deterministic compiler, the same task, source bytes, rules, configuration, budget and compiler version should yield the same ordered plan. Cache keys and future hierarchical summaries must include the source/configuration identities necessary to detect staleness. Provider/model metadata may be attached by downstream execution evidence, but it does not redefine the canonical selection contract.
