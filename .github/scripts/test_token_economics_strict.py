#!/usr/bin/env python3
"""Strict-input regressions; no external evidence, models or commands are acquired."""
import copy
import hashlib
import json
import unittest

import token_economics as economics
from test_token_economics import D, E, evaluation, routing


def measured_route():
    value = routing()
    value.update(evidence_status="project-evaluated", measured_quality=0.95,
                 model_registry_ref={"reference": "fixture:registry", "digest": D},
                 evaluation_refs=[{"reference": "fixture:eval", "digest": E}])
    return value


class StrictEvidenceInputs(unittest.TestCase):
    def test_nonfinite_quality_never_becomes_evidence_backed(self):
        for number in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(number=str(number)):
                value = measured_route()
                value["measured_quality"] = number
                with self.assertRaises(economics.EvaluationError):
                    economics.inspect_routing(value)

    def test_nonfinite_nested_usage_rejected_before_schema(self):
        for side in ("baseline", "candidate"):
            for channel in ("estimated", "observed"):
                for field in ("input_tokens", "tool_output_tokens", "output_tokens"):
                    with self.subTest(side=side, channel=channel, field=field):
                        value = evaluation()
                        value[side]["usage"][channel][field] = float("nan")
                        with self.assertRaises(economics.EvaluationError):
                            economics.inspect_evaluation(value)

    def test_rejects_cycles_non_string_keys_and_invalid_unicode(self):
        cycle = []; cycle.append(cycle)
        for bad in (cycle, {1: "x"}, {"x": "\ud800"}, {"x": object()}):
            with self.subTest(kind=type(bad).__name__):
                for inspect in (economics.inspect_routing, economics.inspect_evaluation):
                    with self.assertRaises(economics.EvaluationError):
                        inspect(bad)

    def test_bound_error_preserved(self):
        value = routing(); value["reason"] = "x" * 140000
        with self.assertRaisesRegex(economics.EvaluationError, "^record-size-limit-exceeded$"):
            economics.inspect_routing(value)

    def test_finite_endpoints_remain_valid_and_non_authorizing(self):
        for number in (0, 0.0, -0.0, 0.5, 1, 1.0):
            value = measured_route(); value["measured_quality"] = number
            previous = copy.deepcopy(value)
            report = economics.inspect_routing(value)
            self.assertTrue(report["valid"])
            self.assertTrue(report["evidence_backed"])
            self.assertFalse(report["execution_authorized"])
            self.assertFalse(report["consequence_authorized"])
            json.dumps(report, allow_nan=False)
            self.assertEqual(value, previous)

    def test_finite_out_of_range_and_boolean_still_invalid(self):
        for number in (-0.1, 1.1, True, False):
            value = measured_route(); value["measured_quality"] = number
            self.assertFalse(economics.inspect_routing(value)["valid"])

    def test_decode_rejects_duplicates_constants_and_exponent_overflow(self):
        for raw in (b'{"quality":0,"quality":1}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":-Infinity}', b'{"x":1e9999}', b'{"x":-1e9999}'):
            with self.subTest(raw=raw):
                with self.assertRaises(economics.EvaluationError):
                    economics.decode(raw)

    def test_decode_preserves_finite_record(self):
        value = measured_route()
        self.assertEqual(economics.decode(json.dumps(value).encode()), value)

    def test_finite_reports_match_pre_fix_corpus(self):
        # Captured against Git blob 8965872db97e7157e9d04eca4c820950b04ade0b.
        reports = []
        for i in range(128):
            route = measured_route()
            route["measured_quality"] = i / 127
            route["measured_cost_microunits"] = i * 100
            value = evaluation()
            value["candidate"]["usage"]["observed"]["input_tokens"] = i
            reports.extend([economics.inspect_routing(route), economics.inspect_evaluation(value)])
        raw = json.dumps(reports, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "49b2526d46bc279fdaadb8d2a98ee88c76392e0520af5e5f70edc11bbdbd24a5")

    def test_strict_errors_do_not_echo_input(self):
        for raw in (b'{"private-key":1,"private-key":2}', b'{"private-data":NaN}'):
            with self.assertRaises(economics.EvaluationError) as error:
                economics.decode(raw)
            self.assertNotIn("private", str(error.exception))


if __name__ == "__main__":
    unittest.main()
