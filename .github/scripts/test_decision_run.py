#!/usr/bin/env python3
"""DecisionRun contract regressions; supplied timing/provenance is not runtime execution proof."""
import copy
import unittest

import decision_run as run

D = "sha256:" + "a" * 64
E = "sha256:" + "b" * 64

def node(node_id, deps=(), source="provider", status="produced", start=0, end=1):
    produced = status == "produced"
    reason = {
        "produced": "none", "unknown": "unknown",
        "insufficient-evidence": "insufficient-evidence",
        "conflicting-evidence": "conflicting-evidence",
        "out-of-distribution": "out-of-distribution",
        "abstained": "policy-fallback",
        "provider-failure": "provider-failure",
        "timeout": "timeout", "budget-exceeded": "budget-exceeded",
        "cancelled": "cancelled", "blocked": "dependency-unavailable"
    }[status]
    return {
        "id": node_id, "spec_id": "fixture." + node_id, "spec_revision": 1,
        "depends_on": list(deps), "status": status, "source": source,
        "receipt_ref": "receipt:" + node_id if produced else None,
        "receipt_digest": D if produced else None,
        "source_run_ref": None, "source_identity_sha256": None,
        "started_at_ms": start, "ended_at_ms": end, "reason_code": reason
    }

def value():
    result = {
        "format_version": 1, "kind": "decision-run", "id": "fixture.run", "mode": "live",
        "identity": {
            "state": {"schema_id": "fixture.state", "schema_version": 1, "fingerprint": "sha256:state"},
            "question_set": {"id": "fixture.graph", "revision": 1, "digest": D},
            "provider": {"type": "jev", "id": "provider.fixture", "model": "fixture-model", "version": "1"}
        },
        "identity_sha256": D,
        "limits": {"max_parallel": 2, "timeout_ms": 10000, "max_cost_microunits": None},
        "fallback": "review", "provider_calls": 1,
        "nodes": [node("a", start=0, end=2), node("b", start=0, end=2),
                  node("c", ("a","b"), start=2, end=3)],
        "reducers": [], "side_effects": False, "consequence_authorized": False
    }
    result["identity_sha256"] = run.identity_sha256(result)
    reducer = {
        "id": "summary", "version": "1",
        "inputs": [{"node_id": n["id"], "status": n["status"],
                    "receipt_ref": n["receipt_ref"], "receipt_digest": n["receipt_digest"]}
                   for n in result["nodes"]],
        "input_digest": D, "output_digest": E, "pure": True,
        "side_effects": False, "consequence_authorized": False, "fallback_used": None
    }
    reducer["input_digest"] = run.reducer_input_digest(reducer)
    result["reducers"] = [reducer]
    return result

class IdentityAndGraph(unittest.TestCase):
    def test_valid_parallel_run_and_pure_reducer(self):
        result = run.inspect_run(value())
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["peak_parallel"], 2)
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["consequence_authorized"])
        self.assertFalse(result["reducer_execution_performed"])

    def test_identity_binds_state_question_set_and_provider(self):
        for path in ("state", "question_set", "provider"):
            current = value()
            if path == "state": current["identity"][path]["fingerprint"] = "changed-state"
            elif path == "question_set": current["identity"][path]["revision"] = 2
            else: current["identity"][path]["version"] = "2"
            self.assertIn("run-identity-mismatch", run.inspect_run(current)["errors"])

    def test_duplicate_unknown_dependency_and_cycle_fail(self):
        current = value(); current["nodes"][1]["id"] = "a"
        self.assertIn("duplicate-node-id", run.inspect_run(current)["errors"])
        current = value(); current["nodes"][0]["depends_on"] = ["missing"]
        self.assertIn("unknown-dependency:missing", run.inspect_run(current)["errors"])
        current = value(); current["nodes"][0]["depends_on"] = ["c"]
        self.assertIn("cycle", run.inspect_run(current)["errors"])

    def test_dependency_cannot_overlap_transitively(self):
        current = value()
        current["nodes"][2].update(started_at_ms=1, ended_at_ms=3)
        self.assertIn("dependency-overlap:c", run.inspect_run(current)["errors"])

    def test_concurrency_limit_is_enforced(self):
        current = value(); current["limits"]["max_parallel"] = 1
        self.assertIn("max-parallel-exceeded", run.inspect_run(current)["errors"])

class ProvenanceAndReplay(unittest.TestCase):
    def test_cache_result_requires_same_identity_and_origin(self):
        current = value()
        current["nodes"][0].update(source="cache", source_run_ref="run:old",
                                   source_identity_sha256=current["identity_sha256"])
        self.assertTrue(run.inspect_run(current)["valid"])
        current["nodes"][0]["source_identity_sha256"] = E
        self.assertIn("cache-identity-mismatch:a", run.inspect_run(current)["errors"])

    def test_replay_has_zero_provider_calls_and_no_provider_sources(self):
        current = value()
        current["mode"] = "replay"; current["provider_calls"] = 0
        for n in current["nodes"]:
            n.update(source="replay", source_run_ref="run:old",
                     source_identity_sha256=current["identity_sha256"])
        result = run.inspect_run(current)
        self.assertTrue(result["valid"], result)
        self.assertTrue(result["replay_without_provider"])
        self.assertFalse(result["provider_call_authorized"])

    def test_replay_refuses_provider_call_or_provider_source(self):
        current = value(); current["mode"] = "replay"
        self.assertIn("replay-has-provider-calls", run.inspect_run(current)["errors"])
        current["provider_calls"] = 0
        self.assertIn("replay-has-provider-sourced-node", run.inspect_run(current)["errors"])

    def test_provider_source_needs_recorded_provider_call(self):
        current = value(); current["provider_calls"] = 0
        self.assertIn("provider-sourced-results-without-provider-call", run.inspect_run(current)["errors"])

    def test_cache_never_authorizes_reuse(self):
        current = value()
        current["nodes"][0].update(source="cache", source_run_ref="run:old",
                                   source_identity_sha256=current["identity_sha256"])
        result = run.inspect_run(current)
        self.assertFalse(result["cache_reuse_authorized"])
        self.assertFalse(result["execution_authorized"])

class StatesAndBudgets(unittest.TestCase):
    def test_non_success_states_are_preserved_with_explicit_reasons(self):
        for status in ("insufficient-evidence","conflicting-evidence","out-of-distribution",
                       "provider-failure","timeout","budget-exceeded","cancelled","blocked"):
            current = value()
            current["nodes"][0] = node("a", source="none", status=status, start=0, end=1)
            current["reducers"] = []  # Isolate node-state semantics; reducer binding has separate tests.
            self.assertTrue(run.inspect_run(current)["valid"], status)

    def test_status_reason_mismatch_is_rejected(self):
        current = value()
        current["nodes"][0] = node("a", source="none", status="timeout")
        current["nodes"][0]["reason_code"] = "unknown"
        self.assertIn("status-reason-mismatch:a", run.inspect_run(current)["errors"])

    def test_produced_receipt_is_required_and_nonproduced_receipt_forbidden(self):
        current = value(); current["nodes"][0]["receipt_ref"] = None
        self.assertIn("produced-without-receipt:a", run.inspect_run(current)["errors"])
        current = value(); current["nodes"][0] = node("a", source="none", status="timeout")
        current["nodes"][0]["receipt_ref"] = "receipt:bad"; current["nodes"][0]["receipt_digest"] = D
        self.assertIn("nonproduced-with-receipt:a", run.inspect_run(current)["errors"])

    def test_partial_or_reversed_timing_is_rejected(self):
        current = value(); current["nodes"][0]["ended_at_ms"] = None
        self.assertIn("partial-timing:a", run.inspect_run(current)["errors"])
        current = value(); current["nodes"][0].update(started_at_ms=2, ended_at_ms=1)
        self.assertIn("reversed-timing:a", run.inspect_run(current)["errors"])

class ReducerContracts(unittest.TestCase):
    def test_reducer_input_digest_is_recomputed(self):
        current = value(); current["reducers"][0]["input_digest"] = D
        self.assertIn("reducer-input-digest-mismatch:summary", run.inspect_run(current)["errors"])

    def test_reducer_input_must_match_recorded_receipt(self):
        current = value(); current["reducers"][0]["inputs"][0]["receipt_digest"] = E
        self.assertIn("reducer-input-mismatch:summary:a", run.inspect_run(current)["errors"])

    def test_unknown_and_duplicate_reducer_inputs_fail(self):
        current = value()
        current["reducers"][0]["inputs"].append(copy.deepcopy(current["reducers"][0]["inputs"][0]))
        current["reducers"][0]["input_digest"] = run.reducer_input_digest(current["reducers"][0])
        self.assertIn("duplicate-reducer-input:summary", run.inspect_run(current)["errors"])
        current = value()
        current["reducers"][0]["inputs"][0]["node_id"] = "missing"
        current["reducers"][0]["input_digest"] = run.reducer_input_digest(current["reducers"][0])
        self.assertIn("unknown-reducer-input:summary", run.inspect_run(current)["errors"])

    def test_schema_prevents_reducer_side_effects_and_consequence_authority(self):
        for field in ("pure","side_effects","consequence_authorized"):
            current = value()
            current["reducers"][0][field] = not current["reducers"][0][field]
            self.assertFalse(run.inspect_run(current)["valid"])

class Bounds(unittest.TestCase):
    def test_record_size_bound(self):
        current = value()
        current["id"] = "x" * 140000
        with self.assertRaises(run.DecisionRunError):
            run.inspect_run(current)

if __name__ == "__main__":
    unittest.main()
