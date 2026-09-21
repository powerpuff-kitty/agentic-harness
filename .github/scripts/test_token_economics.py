#!/usr/bin/env python3
"""Token-economics contract tests; fixtures are not measured model trials."""
import copy
import unittest

import token_economics as economics

D = "sha256:" + "a" * 64
E = "sha256:" + "b" * 64

def usage(input_tokens=100, tool_tokens=20, output_tokens=10, complete=True, cost=None):
    return {
        "estimated": {"input_tokens": input_tokens, "tool_output_tokens": tool_tokens,
                      "output_tokens": output_tokens, "estimator": "fixture-estimator-v1"},
        "observed": {"token_usage_complete": complete, "input_tokens": input_tokens,
                     "tool_output_tokens": tool_tokens, "output_tokens": output_tokens,
                     "retries": 0, "latency_ms": 1000, "cost_microunits": cost,
                     "evidence_ref": "fixture:usage"}
    }

def outcome(acceptance="passed", verification="passed", passed=("tests",), failed=()):
    return {"acceptance": acceptance, "verification": verification,
            "checks_passed": list(passed), "checks_failed": list(failed), "errors": []}

def evaluation():
    treatment = lambda kind, ident, tokens: {
        "context_kind": kind, "context_identity": ident,
        "evidence_present": ["rules", "source"], "usage": usage(tokens),
        "outcome": outcome()
    }
    return {
        "format_version": 1, "kind": "token-efficiency-evaluation", "id": "fixture.compare",
        "created_at": "2026-09-21T00:00:00Z",
        "task": {"id": "fixture.task", "fixture_digest": D, "source_revision": "abc123",
                 "required_checks": ["tests"]},
        "required_evidence": ["rules", "source"],
        "baseline": treatment("full", D, 200),
        "candidate": treatment("compiled", E, 100)
    }

def routing():
    return {
        "format_version": 1, "kind": "stage-routing-evidence", "id": "fixture.route",
        "created_at": "2026-09-21T00:00:00Z", "stage_class": "reasoning-implementation",
        "deterministic_exact_answer_available": False,
        "selected": {"kind": "model", "id": "model-a", "version": "1"},
        "evidence_status": "unmeasured", "model_registry_ref": None, "evaluation_refs": [],
        "measured_quality": None, "measured_cost_microunits": None,
        "advisory": True, "execution_authorized": False, "reason": "No project eval yet; exploratory route only."
    }

class EvaluationContracts(unittest.TestCase):
    def test_same_task_quality_preserved_and_channel_deltas(self):
        result = economics.inspect_evaluation(evaluation())
        self.assertTrue(result["valid"])
        self.assertEqual(result["comparison_status"], "quality-preserved")
        self.assertTrue(result["quality_preserved"])
        self.assertEqual(result["observed_deltas_baseline_minus_candidate"]["input_tokens"], 100)
        self.assertEqual(result["observed_deltas_baseline_minus_candidate"]["tool_output_tokens"], 0)
        self.assertFalse(result["token_savings_verified"])

    def test_missing_required_evidence_is_regression_even_with_lower_tokens(self):
        value = evaluation()
        value["candidate"]["usage"] = usage(10, 1, 1)
        value["candidate"]["evidence_present"].remove("rules")
        result = economics.inspect_evaluation(value)
        self.assertEqual(result["comparison_status"], "regression")
        self.assertIn("candidate-missing-required-evidence", result["regression_reasons"])
        self.assertFalse(result["quality_preserved"])

    def test_failed_or_missing_required_check_is_regression(self):
        value = evaluation()
        value["candidate"]["outcome"] = outcome(acceptance="failed", verification="failed", passed=(), failed=("tests",))
        result = economics.inspect_evaluation(value)
        self.assertEqual(result["comparison_status"], "regression")
        self.assertIn("candidate-required-check-regression", result["regression_reasons"])

    def test_passing_acceptance_cannot_hide_missing_required_check(self):
        value = evaluation()
        value["candidate"]["outcome"]["checks_passed"] = []
        result = economics.inspect_evaluation(value)
        self.assertFalse(result["valid"])
        self.assertIn("candidate-acceptance-passed-with-incomplete-required-checks", result["errors"])

    def test_broken_baseline_is_inconclusive_not_candidate_win(self):
        value = evaluation()
        value["baseline"]["outcome"]["acceptance"] = "failed"
        result = economics.inspect_evaluation(value)
        self.assertEqual(result["comparison_status"], "inconclusive-baseline")
        self.assertIsNone(result["quality_preserved"])

    def test_incomplete_usage_withholds_all_observed_deltas(self):
        value = evaluation()
        value["candidate"]["usage"]["observed"].update(token_usage_complete=False, tool_output_tokens=None)
        result = economics.inspect_evaluation(value)
        self.assertFalse(result["observed_token_usage_comparable"])
        self.assertTrue(all(v is None for v in result["observed_deltas_baseline_minus_candidate"].values()))

    def test_complete_usage_requires_all_token_channels_and_retries(self):
        for field in ("input_tokens", "tool_output_tokens", "output_tokens", "retries"):
            value = evaluation()
            value["candidate"]["usage"]["observed"][field] = None
            result = economics.inspect_evaluation(value)
            self.assertIn("candidate-complete-usage-has-null-token-field", result["errors"])

    def test_estimated_usage_requires_estimator_identity(self):
        value = evaluation()
        value["candidate"]["usage"]["estimated"]["estimator"] = None
        self.assertIn("candidate-estimated-usage-without-estimator",
                      economics.inspect_evaluation(value)["errors"])

    def test_observed_measurement_requires_evidence_reference(self):
        value = evaluation()
        value["candidate"]["usage"]["observed"]["evidence_ref"] = None
        self.assertIn("candidate-observed-measurement-without-evidence-ref",
                      economics.inspect_evaluation(value)["errors"])

    def test_cost_remains_unmeasured_when_null(self):
        result = economics.inspect_evaluation(evaluation())
        self.assertFalse(result["cost_measured"])
        self.assertIsNone(result["observed_deltas_baseline_minus_candidate"]["cost_microunits"])

    def test_measured_cost_delta_is_descriptive_only(self):
        value = evaluation()
        value["baseline"]["usage"]["observed"]["cost_microunits"] = 500
        value["candidate"]["usage"]["observed"]["cost_microunits"] = 300
        result = economics.inspect_evaluation(value)
        self.assertTrue(result["cost_measured"])
        self.assertEqual(result["observed_deltas_baseline_minus_candidate"]["cost_microunits"], 200)
        self.assertFalse(result["token_savings_verified"])

    def test_context_roles_are_fixed_full_vs_compiled(self):
        value = evaluation(); value["baseline"]["context_kind"] = "compiled"
        self.assertFalse(economics.inspect_evaluation(value)["valid"])

class RoutingContracts(unittest.TestCase):
    def test_unmeasured_model_route_is_valid_but_not_evidence_backed(self):
        result = economics.inspect_routing(routing())
        self.assertTrue(result["valid"])
        self.assertFalse(result["evidence_backed"])
        self.assertTrue(result["advisory"])
        self.assertFalse(result["execution_authorized"])

    def test_deterministic_exact_answer_is_preferred(self):
        value = routing()
        value["deterministic_exact_answer_available"] = True
        result = economics.inspect_routing(value)
        self.assertIn("deterministic-exact-answer-not-preferred", result["errors"])
        value["selected"] = {"kind": "deterministic-tool", "id": "parser", "version": "1"}
        self.assertTrue(economics.inspect_routing(value)["valid"])

    def test_deterministic_stage_cannot_select_model(self):
        value = routing()
        value["stage_class"] = "deterministic-tool"
        self.assertIn("deterministic-stage-routed-to-nondeterministic-mechanism",
                      economics.inspect_routing(value)["errors"])

    def test_unmeasured_route_cannot_claim_quality_or_cost(self):
        for field, val in (("measured_quality", .9), ("measured_cost_microunits", 100)):
            value = routing(); value[field] = val
            self.assertIn("unmeasured-route-has-measured-claims", economics.inspect_routing(value)["errors"])
        value = routing(); value["evaluation_refs"] = [{"reference":"eval:1","digest":D}]
        self.assertIn("unmeasured-route-has-measured-claims", economics.inspect_routing(value)["errors"])

    def test_project_evaluated_model_route_requires_eval_and_registry(self):
        value = routing(); value["evidence_status"] = "project-evaluated"
        result = economics.inspect_routing(value)
        self.assertIn("project-evaluated-route-missing-evaluation-reference", result["errors"])
        self.assertIn("project-evaluated-model-route-missing-registry-reference", result["errors"])
        self.assertIn("project-evaluated-route-missing-quality", result["errors"])

    def test_project_evaluated_route_becomes_evidence_backed_not_executable(self):
        value = routing(); value.update(
            evidence_status="project-evaluated",
            model_registry_ref={"reference":"catalog:model-a","digest":D},
            evaluation_refs=[{"reference":"eval:fixture","digest":E}],
            measured_quality=.95, measured_cost_microunits=300)
        result = economics.inspect_routing(value)
        self.assertTrue(result["valid"])
        self.assertTrue(result["evidence_backed"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["consequence_authorized"])

    def test_schema_fixes_advisory_and_execution_authority(self):
        for field, val in (("advisory", False), ("execution_authorized", True)):
            value = routing(); value[field] = val
            self.assertFalse(economics.inspect_routing(value)["valid"])

class Bounds(unittest.TestCase):
    def test_oversized_record_refused(self):
        value = routing(); value["reason"] = "x" * 140000
        with self.assertRaises(economics.EvaluationError):
            economics.inspect_routing(value)

if __name__ == "__main__":
    unittest.main()
