#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "catalog/schema/decision.v1.schema.json").read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)

D1 = "sha256:" + "a" * 64
D2 = "sha256:" + "b" * 64

provider = json.loads((ROOT / "registry/decisions/typesafe/jev.json").read_text())
policy = {
    "format_version": 1,
    "kind": "decision-policy",
    "default_provider": "typesafe/jev",
    "allowed_classes": ["routing", "classification", "scoring", "verification-triage", "review-triage"],
    "consequential_actions": "never-direct",
    "failure_mode": "stronger-model-review",
    "limits": {"max_questions": 16, "max_input_tokens": 32000, "timeout_ms": 5000},
}
request = {
    "format_version": 1,
    "kind": "decision-request",
    "request_id": "route-1",
    "decision_class": "routing",
    "provider": "typesafe/jev",
    "model": "jev-latest",
    "state": "Refactor a Rust parser with failing tests.",
    "state_digest": D1,
    "question_set_digest": D2,
    "questions": {
        "route": {
            "type": "choice",
            "instructions": "Which execution lane fits this task?",
            "criteria": {
                "fast": "Small deterministic change",
                "coding": "Normal implementation work",
                "reasoning": "Complex architecture or multi-system reasoning",
                "human": "Requires explicit human review",
            },
        },
        "needs_review": {
            "type": "boolean-probability",
            "instructions": "Does this task require explicit human review?",
        },
        "complexity": {
            "type": "score",
            "instructions": "How complex is the implementation?",
            "criteria": ["Small/localized", "Multi-file", "Cross-system"],
        },
    },
}
result = {
    "format_version": 1,
    "kind": "decision-result",
    "request_id": "route-1",
    "status": "succeeded",
    "provider": "typesafe/jev",
    "requested_model": "jev-latest",
    "resolved_model": "jev-1.13.0",
    "state_digest": D1,
    "question_set_digest": D2,
    "answers": {
        "route": {
            "type": "choice",
            "choice": "reasoning",
            "probabilities": {"fast": 0.01, "coding": 0.20, "reasoning": 0.78, "human": 0.01},
            "confidence": 0.74,
        },
        "needs_review": {"type": "boolean-probability", "probability": 0.12},
        "complexity": {
            "type": "score",
            "score": 1.70,
            "legend": {"0": "Small/localized", "1": "Multi-file", "2": "Cross-system"},
            "probabilities": {"0": 0.02, "1": 0.26, "2": 0.72},
            "confidence": 0.70,
        },
    },
    "usage": {"input_tokens": 420, "output_tokens": 64},
    "observed_at_ms": 1,
    "latency_ms": 150,
    "authorization_granted": False,
    "not_checked": ["Whether the selected route is correct for this repository."],
    "error": None,
}

for name, value in [("provider", provider), ("policy", policy), ("request", request), ("result", result)]:
    errors = sorted(VALIDATOR.iter_errors(value), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{name} should validate: {errors[0].message}")

bad_secret = copy.deepcopy(request)
bad_secret["api_key"] = "must-never-be-stored"
if not list(VALIDATOR.iter_errors(bad_secret)):
    raise SystemExit("request unexpectedly accepts persisted secrets")

bad_auth = copy.deepcopy(result)
bad_auth["authorization_granted"] = True
if not list(VALIDATOR.iter_errors(bad_auth)):
    raise SystemExit("result unexpectedly grants authorization")

failed_with_answer = copy.deepcopy(result)
failed_with_answer["status"] = "timeout"
failed_with_answer["resolved_model"] = None
failed_with_answer["usage"] = None
failed_with_answer["error"] = "provider timeout"
if not list(VALIDATOR.iter_errors(failed_with_answer)):
    raise SystemExit("failed result unexpectedly accepts decision answers")

too_many_score_levels = copy.deepcopy(request)
too_many_score_levels["questions"]["complexity"]["criteria"] = [str(i) for i in range(11)]
if not list(VALIDATOR.iter_errors(too_many_score_levels)):
    raise SystemExit("score unexpectedly accepts more than 10 levels")

print("Semantic decision contract valid: provider, policy, request/result and safety regressions passed")
