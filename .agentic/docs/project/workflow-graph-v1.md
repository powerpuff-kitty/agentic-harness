# Bounded workflow graph v1

Status: experimental, additive contract for #96. Canonical schema: `catalog/schema/workflow-graph.v1.schema.json`.

## Purpose

This contract describes a bounded DAG of read-only work and the truthful result of attempting that work. It sits above the existing check planning, reviewed check execution and governance-evidence contracts; it does not replace them.

A workflow definition is **not** execution permission, proof of isolation, evidence authentication or verified completion. Structural schema validation is necessary but insufficient.

## Design principles

- Independent tasks may run concurrently only when their dependencies are satisfied.
- Concurrency, total task count, retries and elapsed time are bounded by the workflow.
- The first version is read-only. Mutation tasks are invalid.
- Deterministic checks should reference existing check/evidence artifacts instead of inventing another command-execution contract.
- LLM/model/provider identity is runtime metadata, not canonical workflow truth.
- Missing work remains visible. A report must include audit coverage, not only findings.
- Aggregation must preserve disagreement, blocked work and missing evidence.

## Task kinds

- `deterministic-check`: consumes a reviewed deterministic check contract/result.
- `analysis`: performs a scoped review such as architecture, security or design-system analysis.
- `verification`: independently challenges findings and validates evidence references.
- `aggregation`: deduplicates and combines upstream results without hiding conflict or incompleteness.

Every task has a stable `id`, explicit `depends_on`, `required`, `read_only`, declared `isolation`, bounded `max_attempts`, and explicit input/output artifact identities.

## Isolation semantics

`shared-read-only`, `isolated-worktree` and `sandboxed` are execution declarations. They do not prove containment.

A Git worktree is workspace separation, not a security boundary: repository data and references are still shared. A runtime may claim `sandboxed` only when an external mechanism actually provides and records that isolation. The workflow contract itself never upgrades an isolation declaration into verified enforcement.

## Semantic validation

Consumers must reject workflows that are structurally valid but semantically invalid, including:

- duplicate task IDs;
- dependencies on unknown task IDs;
- self-dependencies or cycles;
- task count greater than `limits.max_total_tasks`;
- results that omit or duplicate task IDs;
- result `required` flags that disagree with the workflow;
- coverage counters that do not match the result set;
- `complete=true` when a required task is anything other than `passed`;
- `complete=true` when any required task is absent;
- attempts greater than the task's `max_attempts`;
- execution beyond declared concurrency or elapsed-time bounds.

The repository validator compares the supplied workflow ID, checks every declared task has a result, and checks recorded task intervals against run bounds, dependency completion and peak worker count. Executed tasks require a start/end pair; a zero-attempt result cannot claim a pass. Intervals are half-open: a task ending at a timestamp releases its slot before another starts there. Zero-duration intervals do not occupy a measurable slot. The task interval spans its recorded attempts; retry timing is not separately authenticated.

These checks establish supplied-record consistency, not actual scheduling, trusted clocks, isolation or executed evidence. Workflow/source digests are opaque recorded identities, not recomputed here. Optional token/cost limits have no corresponding measured usage in this v1 run shape and are not enforced by this validator; runtime evidence must establish them separately. A consumer should fail closed when it cannot establish required properties.

## Completion and coverage

Task states are:

- `passed`
- `failed`
- `skipped`
- `blocked`
- `unsupported`
- `execution-error`
- `unverified`

`complete=true` means every required task in the exact workflow completed with status `passed`, every result maps to a declared task, the run stayed within supported semantics, and coverage has been validated. It does **not** mean the repository is globally correct or that every governance capability is enforced.

Coverage records total, required, executed, passed, failed, skipped, blocked, unsupported, execution-error and unverified counts. Consumers must derive and verify these values from results rather than trusting counters blindly.

## Reference read-only audit graph

```text
architecture-review ─┐
security-review ─────┼─> verify-evidence ─> aggregate-report
design-system-review ┘
```

The three reviews can run concurrently. `verify-evidence` starts only after all declared upstream dependencies reach terminal states. If a required upstream task fails or is unavailable, downstream behavior must be explicit (`blocked`, `unsupported`, etc.) and the run cannot be complete.

## Runtime relationship

The CLI implementation is tracked separately. A scheduler is expected to enforce dependency ordering and budgets, while command checks continue to use the existing reviewed check-execution contract. Provider-specific agents may be adapters above this graph; they must not redefine the graph semantics.

## Non-goals

- unbounded agent swarms;
- automatic code mutation or patch merging in v1;
- visual workflow authoring;
- model/provider lock-in;
- treating reviewer agreement as executable verification;
- claiming a worktree or process group is a sandbox.