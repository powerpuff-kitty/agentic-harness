# Agent Work → OpenTelemetry mapping v1

OpenTelemetry is an optional observability projection of canonical Agent Work state. An OTLP exporter, collector, backend, sampling decision, dropped span, or missing telemetry must never create, delete, complete, fail, approve or otherwise mutate a canonical WorkUnit, Run, Task, Attempt, Action, Evaluation, Finding, Metric or WorkEvent.

This mapping follows OpenTelemetry semantic-convention 1.44.0 as the reviewed baseline. The separate OpenTelemetry GenAI semantic-conventions repository still marks GenAI and agent conventions as Development. OpenTelemetry treats operations with meaningful duration as spans and point-in-time occurrences such as state changes as events. Span links may connect related operations without inventing a parent/child relationship. The `otel.*` namespace is reserved by OpenTelemetry, so Agent Work uses the custom `agent.work.*` namespace.

References:
- https://opentelemetry.io/docs/specs/semconv/
- https://opentelemetry.io/docs/specs/semconv/general/events/
- https://opentelemetry.io/docs/specs/otel/trace/api/
- https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
- https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/README.md
- https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
- https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md

## Canonical entity mapping

| Canonical entity | Default OTel projection | Required Agent Work correlation |
| --- | --- | --- |
| WorkUnit | root INTERNAL span | `agent.work.work_unit.id`, entity kind/id |
| Run | child INTERNAL span | work-unit id, run id, entity kind/id |
| Task | child INTERNAL span | work-unit id, run id, task id, entity kind/id |
| Attempt | child INTERNAL span | work-unit/run/task/attempt ids, entity kind/id |
| WorkAction | INTERNAL span when it has an execution duration; otherwise a WorkEvent-style event | work-unit id when known, action id, entity kind/id |
| WorkEvent | span event on the closest owning span | canonical event id/type and exact timestamp |
| model/tool operation | child span under the owning Attempt/Action | provider/tool/model metadata when observed; input/output identities rather than content |

WorkUnit, Run, Task and Attempt spans are Agent Work's custom observability projection; they are not relabeled as standard GenAI agent spans merely because an AI agent performed the work. When the instrumented operation really is a GenAI agent invocation, workflow invocation, planning phase or tool execution, producers may additionally apply the reviewed `gen_ai.operation.name` values such as `invoke_agent`, `invoke_workflow`, `plan` and `execute_tool` according to the Development conventions.

A producer may choose additional spans, attributes, resources, metrics or logs. Those extensions must not change the canonical entity IDs or reinterpret missing telemetry as missing work.

## Required custom attributes

Every Agent Work entity span carries:

- `agent.work.protocol.version`
- `agent.work.work_unit.id`
- `agent.work.entity.kind`
- `agent.work.entity.id`

Add the nearest applicable identifiers such as `agent.work.run.id`, `agent.work.task.id`, `agent.work.attempt.id` and `agent.work.action.id`. The entity object in the conformance envelope and the attributes must agree exactly so a telemetry record can be correlated back to canonical state without parsing span names.

For a mapped WorkEvent, the event attributes carry `agent.work.event.id` and `agent.work.event.type`. A state-transition event additionally carries `agent.work.state.previous` and `agent.work.state.next`, which must match the canonical projection delta.

## Model, tool, token and cost observations

Provider/model/version, token usage and cost are observations. Record them only when the producer actually has them. Agent Work identity attributes remain stable even when GenAI semantic conventions evolve.

When an implementation supports the reviewed GenAI conventions, it may emit current attributes such as `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.tool.name`, `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens`. For example, a local tool execution may use `gen_ai.operation.name=execute_tool` only when the operation is actually a GenAI tool call; an ordinary shell command need not be relabeled. The GenAI conventions are currently Development and live in their dedicated semantic-conventions repository, so producers must retain the reviewed semantic-convention version/status in the export envelope and must not fabricate missing usage.

Use Agent Work metadata such as `agent.work.model.version`, `agent.work.input.identity`, `agent.work.output.identity`, `agent.work.cost.amount`, `agent.work.cost.currency` and `agent.work.cost.source` when needed to preserve provider-neutral provenance. Input/output identity is a digest/reference, never the raw model content.

## Links and retries

Parent/child spans represent execution nesting. Use OTel span links for causal relationships that are not nesting, including prior actions, reassessments, reflections, or cross-trace retry ancestry. A link records trace/span context and a relationship label; it does not replace canonical Agent Work lineage.

## Content and redaction

The v1 conformance envelope is metadata-only. It intentionally has no model-input, model-output or tool-payload field. Do not emit prompt/response bodies, message content, secrets or authorization material through arbitrary attributes. Preserve structural telemetry with IDs, hashes, timing, state, provider/model/tool labels and canonical redaction references instead.

OpenTelemetry Baggage is not used as a required Agent Work correlation mechanism. Baggage propagates across process/network boundaries and OpenTelemetry explicitly warns that sensitive baggage may reach unintended resources. Correlation belongs in allowlisted telemetry attributes emitted by the instrumented producer.

## Missing telemetry

`status: not_collected` with an empty span set is a valid export state. Canonical WorkUnit validation remains independent. A producer or UI must display telemetry coverage separately from work completion/evaluation state.

## Conformance

Run:

```bash
python registry/agent-work/conformance/validate_otel_export.py \
  registry/agent-work/fixtures/otel-export-collected.v1.json \
  --canonical-work-unit registry/agent-work/fixtures/replay-expected-work-unit.v1.json \
  --canonical-events registry/agent-work/fixtures/replay-events.v1.json \
  --canonical-redactions registry/agent-work/fixtures/redactions.v1.json
```

The validator checks schema validity, parent-span structure, entity correlation, canonical event/time/state correlation, metadata-only sensitive-key restrictions, timestamps, redaction references and optional canonical entity membership. This is conformance evidence for the supplied export bytes, not proof that a live exporter or backend always behaves correctly.
