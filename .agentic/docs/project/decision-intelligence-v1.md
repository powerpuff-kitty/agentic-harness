# Semantic Decision Intelligence v1

Status: experimental canonical contract for #106. Schema: `catalog/schema/decision.v1.schema.json`.

## Purpose

Semantic decisions fill the narrow gap between deterministic code and expensive open-ended generation. A provider evaluates one bounded state against small typed questions and returns probabilities or scores that ordinary code can compose.

The contract is provider-neutral. TypeSafe Jev is the first registered provider, not a new general chat/model profile.

## Boundaries

- Prefer deterministic parsing, validation, authorization and policy enforcement when those answers are mechanically knowable.
- Decision results are advisory evidence. They never grant authorization, establish test success, certify correctness or directly execute destructive, production, release or security-sensitive actions.
- Project-owned `.agentic/` truth and deterministic policies retain precedence.
- API keys and other credentials are environment/runtime inputs only. They never belong in manifests, locks, decision requests or committed evidence.
- Questions, criteria, thresholds and fallback policy should live together in project-owned configuration so a reviewer can inspect the actual decision surface.
- A provider/model alias can move. Evidence records the resolved model identity when the provider reports it.

## Contract records

### `decision-provider`

Describes a reviewed provider integration: provider ID, vendor, transport class, aliases, supported primitive classes, required secret environment variables and documentation provenance.

The initial profile lives at `registry/decisions/typesafe/jev.json`.

### `decision-policy`

Declares which semantic decision classes are allowed and the fallback mode. `consequential_actions` is fixed to `never-direct` in v1.

Allowed classes are routing, classification, scoring, verification triage and review triage.

### `decision-request`

Contains a bounded state, state digest, question-set digest, provider/model selection and one or more typed questions.

The canonical question types are:

- `boolean-probability`: yes/no probability. TypeSafe maps this to Jev `noul`.
- `choice`: select from a finite unordered option set with a distribution.
- `score`: place the state on an ordered rubric.

Provider adapters translate these canonical names to the provider API. Provider-specific wire fields must not leak into project policy.

### `decision-result`

Records status, requested and resolved model identity, input/question digests, typed answers, usage, latency and limitations. `authorization_granted` is always false.

A failed/timeout/unavailable/invalid response has no answers and carries an error. Success does not imply correctness; `not_checked` must retain that boundary.

## TypeSafe Jev mapping

Reviewed against TypeSafe's API documentation on 2026-09-18:

- HTTP endpoint: `POST https://api.typesafe.ai/v1/systemone`
- authentication: bearer token from `TYPESAFE_API_KEY`
- stable model alias: `jev-latest`
- canonical `boolean-probability` -> Jev `noul`
- canonical `choice` -> Jev `choice`
- canonical `score` -> Jev `score`

Jev evaluates multiple questions against the same state in one request. The adapter should preserve that batching rather than issuing one network call per question.

Live API documentation remains authoritative: https://docs.typesafe.ai/api

## Example

```json
{
  "format_version": 1,
  "kind": "decision-request",
  "request_id": "task-route-001",
  "decision_class": "routing",
  "provider": "typesafe/jev",
  "model": "jev-latest",
  "state": "Refactor the Rust parser and preserve the current public API.",
  "state_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "question_set_digest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "questions": {
    "route": {
      "type": "choice",
      "instructions": "Which execution lane fits this task?",
      "criteria": {
        "fast": "Small deterministic change",
        "coding": "Normal implementation work",
        "reasoning": "Complex architecture or multi-system reasoning",
        "human": "Requires explicit human review before execution"
      }
    },
    "needs_review": {
      "type": "boolean-probability",
      "instructions": "Does this task require explicit human review before consequential execution?"
    }
  }
}
```

Code interprets the distributions and applies the reviewed fallback/threshold policy. The provider never owns the workflow.
