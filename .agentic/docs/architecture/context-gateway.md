# Context Gateway architecture

The Context Gateway extends the Context Compiler into the provider-neutral boundary between potentially large retained project knowledge and the small task-specific context shown to a model.

It does not replace the compiled-context plan from `catalog/schema/compiled-context-plan.v1.schema.json`. The gateway produces an explainable selection trace, and the existing compiled plan remains the final model-input projection.

## Pipeline

```text
Task
  |
  v
mandatory project truth + deterministic scope filters
  |
  v
repository + Project Memory + execution-evidence retrieval
  |
  v
cheap lexical / metadata ranking
  |
  v
optional semantic retrieval
  |
  v
optional typed Decision Kernel gating / reranking
  |
  v
budget + progressive disclosure
  |
  v
compiled-context-plan
```

Cheap deterministic filters should run first. Semantic search is used only when deterministic retrieval is insufficient. Typed decisions are optional and advisory. Bounded generative compression is the last expensive stage and must never silently turn generated analysis into project truth.

## Public contracts

- `context-gateway-request.v1.schema.json` — immutable task/scope/input identities, target execution environment, allowed stages, sensitivity policy and token budgets.
- `context-selection-trace.v1.schema.json` — every candidate, retrieval provenance, stage history, scores, typed-decision provenance, final disposition and budget accounting.
- `compiled-context-plan.v1.schema.json` — the existing #114 final projection, extended additively for Project Memory and execution-evidence sources.
- `context-gateway-benchmark.v1.schema.json` — full-context versus gateway-selected comparison with separate estimated/observed input, tool-output and output usage plus verified outcomes.

Project Memory remains defined under `registry/project-memory/`. Decision semantics remain owned by the Decision Kernel. The gateway references those systems; it does not absorb them.

## Mandatory truth

Authority and relevance remain separate. Mandatory project-authored context is selected before relevance scoring and cannot be removed by semantic search, Jev, another decision provider, compression or the token budget.

If mandatory context alone exceeds the input limit, it remains included and the trace/compiled plan reports `over_budget: true`. The caller may increase the budget, narrow the task or stop; silently dropping required truth is forbidden.

## Project Memory

Memory retrieval is task- and scope-aware. A memory candidate retains:

- memory identity;
- provider identity;
- query identity;
- exact retrieval-result digest;
- memory content digest/revision;
- freshness and sensitivity;
- stage-by-stage inclusion/defer/reject reasons.

The compiled plan uses a `memory://...` stable locator plus the same memory/provider/query/result identities. Storage size never implies context size.

Stale, invalidated, superseded, conflicting or otherwise non-current memory is not silently treated as current truth. Conflict resolution is policy work; semantic relevance scores alone do not resolve contradictions.

## Decision Kernel / Jev boundary

A typed decision may answer relevance or routing questions when deterministic signals are insufficient. A decision stage records the immutable DecisionReceipt reference plus provider type/id/model/version, status, provider confidence and any provider distribution.

Those values are advisory evidence. Provider confidence is not project truth, verification, authorization or an outcome probability. Decision policy remains outside the provider. A mandatory context item cannot be excluded by a decision receipt.

The gateway is not a memory store and Jev/equivalent is not a generative summarizer.

## Sensitivity and remote handoff

Sensitivity is enforced before content reaches a remote target model. A remote ContextGatewayRequest declares allowed sensitivity levels. `local_only` memory cannot be selected for remote handoff unless an explicit future policy contract authorizes a different disclosure path; v1 conformance rejects it.

A local or hybrid retrieval provider may know a local-only memory exists without disclosing its contents to a remote target. Selection traces should record a sensitivity rejection without copying secret content.

## Budgets and usage

Input, tool-output and output budgets are separate. Estimates are planner values, not provider billing. Observed usage remains null until an authoritative provider/runtime usage artifact exists.

Allocation accounting identifies how much selected context is consumed by mandatory truth, repository evidence, Project Memory, execution evidence and generated compression. Mandatory truth is not capped by an allocation.

## Cache and replay

Replay is valid only when request and input provenance identities remain valid. A deterministic selector operating on the same request, source bytes/digests, policy, budgets and provider-independent deterministic signals must produce the same selection fingerprint and candidate dispositions.

A cached semantic decision is reusable only when its DecisionReceipt state/spec/provider identity still matches the current candidate state. Cache hits never waive sensitivity or mandatory-context policy.

## Benchmarking

Token reduction is not a quality result by itself. Gateway benchmarks compare:

1. a full-context baseline;
2. a gateway-selected context;
3. separately estimated and observed input/tool/output usage;
4. mandatory-context coverage;
5. independently verified task outcome.

A benchmark may claim reduced observed input only when measured provider usage is present. Equivalent verified outcomes are required before treating the reduction as a non-regression result.

## Non-goals

The gateway does not:

- persist arbitrary chat history or private chain-of-thought;
- promote memory to project truth;
- let a model authorize consequential actions;
- make all semantic search mandatory;
- hide missing evidence or budget overflow;
- claim a fixture is a production performance benchmark.
