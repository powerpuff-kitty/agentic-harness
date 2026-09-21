#!/usr/bin/env python3
"""Inspect supplied token-efficiency and stage-routing records; no models or checks execute."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 131_072

def _validator(name):
    schema = json.loads((ROOT / "catalog/schema" / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())

EVAL = _validator("token-efficiency-evaluation.v1.schema.json")
ROUTING = _validator("stage-routing-evidence.v1.schema.json")

class EvaluationError(ValueError):
    pass

def _size(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    if len(raw) > MAX_BYTES:
        raise EvaluationError("record-size-limit-exceeded")

def _missing_required(value, treatment):
    required = set(value["required_evidence"])
    present = set(treatment["evidence_present"])
    return sorted(required - present)

def _missing_checks(value, treatment):
    required = set(value["task"]["required_checks"])
    passed = set(treatment["outcome"]["checks_passed"])
    failed = set(treatment["outcome"]["checks_failed"])
    return sorted(required - passed - failed)

def _usage_delta(left, right, key):
    a = left["usage"]["observed"][key]
    b = right["usage"]["observed"][key]
    return None if a is None or b is None else a - b

def inspect_evaluation(value):
    _size(value)
    shape = sorted(error.message for error in EVAL.iter_errors(value))
    if shape:
        return {"valid": False, "errors": shape, "comparison_status": "invalid"}
    errors = []
    baseline_missing = _missing_required(value, value["baseline"])
    candidate_missing = _missing_required(value, value["candidate"])
    baseline_checks_missing = _missing_checks(value, value["baseline"])
    candidate_checks_missing = _missing_checks(value, value["candidate"])
    for label, treatment in (("baseline", value["baseline"]), ("candidate", value["candidate"])):
        estimated = treatment["usage"]["estimated"]
        estimate_fields = ("input_tokens", "tool_output_tokens", "output_tokens")
        if estimated["estimator"] is None and any(estimated[field] is not None for field in estimate_fields):
            errors.append(label + "-estimated-usage-without-estimator")
        observed = treatment["usage"]["observed"]
        token_fields = ("input_tokens", "tool_output_tokens", "output_tokens", "retries")
        if observed["token_usage_complete"] and any(observed[field] is None for field in token_fields):
            errors.append(label + "-complete-usage-has-null-token-field")
        if observed["evidence_ref"] is None and any(observed[field] is not None for field in (*token_fields, "latency_ms", "cost_microunits")):
            errors.append(label + "-observed-measurement-without-evidence-ref")
        if treatment["outcome"]["acceptance"] == "passed" and (treatment["outcome"]["checks_failed"] or _missing_checks(value, treatment)):
            errors.append(label + "-acceptance-passed-with-incomplete-required-checks")
    regression_reasons = []
    if candidate_missing:
        regression_reasons.append("candidate-missing-required-evidence")
    if candidate_checks_missing or value["candidate"]["outcome"]["checks_failed"]:
        regression_reasons.append("candidate-required-check-regression")
    if value["candidate"]["outcome"]["acceptance"] != "passed":
        regression_reasons.append("candidate-acceptance-not-passed")
    if value["candidate"]["outcome"]["verification"] != "passed":
        regression_reasons.append("candidate-verification-not-passed")
    baseline_ready = (not baseline_missing and not baseline_checks_missing
                      and not value["baseline"]["outcome"]["checks_failed"]
                      and value["baseline"]["outcome"]["acceptance"] == "passed"
                      and value["baseline"]["outcome"]["verification"] == "passed")
    candidate_ready = not regression_reasons
    if errors:
        status = "invalid"
    elif not baseline_ready:
        status = "inconclusive-baseline"
    elif candidate_ready:
        status = "quality-preserved"
    else:
        status = "regression"
    complete_usage = (value["baseline"]["usage"]["observed"]["token_usage_complete"]
                      and value["candidate"]["usage"]["observed"]["token_usage_complete"])
    deltas = {
        key: _usage_delta(value["baseline"], value["candidate"], key)
        for key in ("input_tokens", "tool_output_tokens", "output_tokens", "retries", "latency_ms", "cost_microunits")
    }
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "comparison_status": status,
        "baseline_missing_evidence": baseline_missing,
        "candidate_missing_evidence": candidate_missing,
        "baseline_missing_checks": baseline_checks_missing,
        "candidate_missing_checks": candidate_checks_missing,
        "regression_reasons": regression_reasons,
        "quality_preserved": True if status == "quality-preserved" else (False if status == "regression" else None),
        "observed_token_usage_comparable": complete_usage,
        "observed_deltas_baseline_minus_candidate": deltas if complete_usage else {key: None for key in deltas},
        "cost_measured": (value["baseline"]["usage"]["observed"]["cost_microunits"] is not None
                          and value["candidate"]["usage"]["observed"]["cost_microunits"] is not None),
        "token_savings_verified": False,
    }

def inspect_routing(value):
    _size(value)
    shape = sorted(error.message for error in ROUTING.iter_errors(value))
    if shape:
        return {"valid": False, "errors": shape, "evidence_backed": False}
    errors = []
    if value["deterministic_exact_answer_available"] and value["selected"]["kind"] != "deterministic-tool":
        errors.append("deterministic-exact-answer-not-preferred")
    if value["stage_class"] == "deterministic-tool" and value["selected"]["kind"] != "deterministic-tool":
        errors.append("deterministic-stage-routed-to-nondeterministic-mechanism")
    if value["evidence_status"] == "unmeasured":
        if value["evaluation_refs"] or value["measured_quality"] is not None or value["measured_cost_microunits"] is not None:
            errors.append("unmeasured-route-has-measured-claims")
    else:
        if not value["evaluation_refs"]:
            errors.append("project-evaluated-route-missing-evaluation-reference")
        if value["selected"]["kind"] in ("model", "provider") and value["model_registry_ref"] is None:
            errors.append("project-evaluated-model-route-missing-registry-reference")
        if value["measured_quality"] is None:
            errors.append("project-evaluated-route-missing-quality")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "evidence_backed": value["evidence_status"] == "project-evaluated" and not errors,
        "advisory": True,
        "execution_authorized": False,
        "consequence_authorized": False,
    }
