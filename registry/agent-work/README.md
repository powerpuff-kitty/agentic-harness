# Agent Work Protocol

Agent Work is the provider-neutral, versioned contract for observable AI work.

It models execution as structured work rather than a chat transcript. Consumers can render plans, tasks, attempts, evidence, artifacts, evaluations and follow-up actions without requiring or storing private chain-of-thought.

## V1 contracts

- work-unit.v1.schema.json — WorkUnit, Run, Plan revision, Task and Attempt lifecycle.
- work-event.v1.schema.json — append-only execution event envelope.
- evaluation.v1.schema.json — evidence-backed metrics, confidence signals and findings.
- work-action.v1.schema.json — audit/fix/validate/reassess/custom actions and permissions.
- agent-connection.v1.schema.json — executable provider/model/auth/environment capabilities.

## Principles

1. Structured activity, not private reasoning.
2. Missing or unexecuted evidence never becomes a pass.
3. Progress is derived from task state rather than model-estimated percentages.
4. Replanning appends a new plan revision; it does not rewrite history.
5. Implementer and evaluator identities remain distinct.
6. Local, vendor-hosted, cloud-runner and API-backed execution use the same protocol.
7. Consequential writes require explicit permissions and, where policy requires, approval.
8. Provider-specific payloads remain adapter data rather than canonical state.

## Validation

Run:

    python3 .github/scripts/validate_agent_work_protocol.py

The validator checks the JSON Schemas and representative fixtures plus protocol invariants that JSON Schema alone cannot express, including DAG cycles, references, monotonic event sequence and score/evidence semantics.
