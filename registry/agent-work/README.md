# Agent Work Protocol

Agent Work is the provider-neutral, versioned contract for observable AI work.

It models execution as structured work rather than a chat transcript. Consumers can render plans, tasks, attempts, evidence, artifacts, evaluations, reflections and follow-up actions without requiring or storing private chain-of-thought.

## V1 contracts

- work-unit.v1.schema.json — WorkUnit, Run, Plan revision, Task and Attempt lifecycle.
- work-event.v1.schema.json — append-only execution event envelope with optional replay deltas.
- evidence.v1.schema.json — captured facts, derived results and explicit unavailable evidence with provenance.
- artifact.v1.schema.json — content-addressed produced artifacts linked to their producing run/task/attempt.
- redaction.v1.schema.json — explicit redaction records so sensitive payload removal remains auditable.
- evaluation.v1.schema.json — evidence-backed metrics, confidence signals and findings.
- work-action.v1.schema.json — execute/audit/reflect/fix/validate/reassess/custom actions and permissions.
- agent-connection.v1.schema.json — executable provider/model/auth/environment capabilities.
- reflection.v1.schema.json — bounded post-attempt reflection with evidence, uncertainty, corrections and lineage.
- reflection-policy.v1.schema.json — deterministic/provider-neutral policy for deciding when reflection is worth invoking.
- reflection-trigger-decision.v1.schema.json — replayable result of applying a reflection policy to a trigger.

## Concept boundaries

| Concept | Purpose | Canonical? | May feed model context? |
| --- | --- | --- | --- |
| Project truth | Version-controlled rules, architecture and explicit decisions | Yes | Yes, when in task scope |
| Execution history | Append-only observable work/events/evidence | Yes for recorded execution facts | Selectively |
| Evaluation | Measures/checks the result and records findings | Yes for the evaluation artifact | Selectively |
| Reflection | Bounded post-attempt analysis used to choose a correction | No: inspectable derived artifact | Selectively |
| Memory candidate | Evidence-backed reusable lesson proposed by reflection or observation | No until separately validated/promoted | No by default |
| Project memory | Validated reusable knowledge with provenance/lifecycle | Separate subsystem | Only through bounded context retrieval |
| Context | Task-specific compiled view shown to a model | Ephemeral projection | It is the model input |

Reflection is not memory. A reflection may emit only memory candidate references; promotion, consolidation, supersession and remote-storage policy belong to the Project Memory subsystem. Reflection is also not hidden reasoning capture: it stores concise inspectable conclusions, uncertainty, evidence and proposed corrective actions.

## Evidence, artifacts and replay

Evidence is not a generic success flag. v1 distinguishes captured facts, derived results and unavailable evidence; verification status remains explicit. Derived evidence references its inputs rather than replacing them.

Artifacts are content-addressed outputs with producer lineage. Small structured snapshots may be stored inline for deterministic replay; larger files/logs/reports normally use external content references. Artifact metadata is canonical, while storage location may be provider-specific.

Sensitive content is never silently deleted. A redacted payload carries a `redaction_ref` to a WorkRedaction record identifying the affected evidence/artifact, fields, reason, policy/actor and optional redacted digest. A redaction record must not contain the removed secret itself.

WorkEvent remains append-only. Optional `projection_delta` records deterministic state transitions, entity creation snapshots, plan revisions and evidence/artifact links. Replaying a seed WorkUnit plus ordered events and referenced structured snapshots must rebuild the same current WorkUnit projection. Replay data captures observable state changes, not private chain-of-thought.

## Reflection lifecycle

    attempt
      -> evaluation/finding/evidence
      -> reflection trigger policy
      -> reflect OR deterministic skip
      -> structured reflection
      -> corrective action / revised plan
      -> next attempt
      -> verification

A known deterministic failure can skip model reflection when policy conditions are satisfied. Missing evidence can produce insufficient_evidence; a model/human may explicitly abstain. Neither state may silently create corrective actions or memory candidates. Re-reflection creates a new artifact linked with prior_reflection_ref; earlier reflections are never overwritten.

## Principles

1. Structured activity, not private reasoning.
2. Missing or unexecuted evidence never becomes a pass.
3. Progress is derived from task state rather than model-estimated percentages.
4. Replanning appends a new plan revision; it does not rewrite history.
5. Implementer and evaluator identities remain distinct.
6. Local, vendor-hosted, cloud-runner and API-backed execution use the same protocol.
7. Consequential writes require explicit permissions and, where policy requires, approval.
8. Provider-specific payloads remain adapter data rather than canonical state.
9. Reflection is optional and policy-triggered; deterministic fixes should not pay an unnecessary model/reflection cost.
10. Reflection conclusions remain evidence-linked and never become canonical project truth or durable memory without an explicit later promotion step.

## Validation

Run:

    python3 .github/scripts/validate_agent_work_protocol.py

The validator checks the JSON Schemas and representative fixtures plus protocol invariants that JSON Schema alone cannot express, including DAG cycles, references, monotonic event sequence, evidence/artifact/redaction provenance, deterministic WorkUnit replay, score/evidence semantics, reflection abstention rules, deterministic trigger ordering and correction lineage.
