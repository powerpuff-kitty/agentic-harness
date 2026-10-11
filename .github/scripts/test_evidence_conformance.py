#!/usr/bin/env python3
"""Mutation tests for shared-case integrity and truthful scope reporting."""
import copy
import json
import unittest
from unittest.mock import patch

import evidence_conformance as conformance
import strict_json


class EvidenceConformanceTests(unittest.TestCase):
    def setUp(self):
        self.raw = (conformance.ROOT / conformance.CORPUS).read_bytes()
        self.schema = (conformance.ROOT / conformance.SCHEMA).read_bytes()
        self.value = strict_json.loads(self.raw)

    def inspect(self, value):
        return conformance.inspect(strict_json.dumps(value), self.schema)

    def reject(self, value):
        with self.assertRaises(conformance.ConformanceError):
            self.inspect(value)

    def test_all_48_shared_cases_match(self):
        result = conformance.inspect(self.raw, self.schema)
        self.assertEqual(result["case_count"], 48)
        self.assertTrue(result["conformant_with_corpus"])
        self.assertFalse(result["completion_verified"])
        self.assertFalse(result["release_verified"])
        self.assertTrue(all(case["matches"] for case in result["results"]))

    def test_wrong_expectation_is_a_mismatch_not_a_pass(self):
        self.value["cases"][0]["expected"] = False
        result = self.inspect(self.value)
        self.assertFalse(result["conformant_with_corpus"])
        self.assertEqual(sum(not c["matches"] for c in result["results"]), 1)

    def test_rejection_at_wrong_stage_does_not_match(self):
        case = next(c for c in self.value["cases"] if c["id"] == "audit.score-bool")
        case["category"] = "transport"
        self.assertFalse(self.inspect(self.value)["conformant_with_corpus"])

    def test_input_drift_requires_exact_digest(self):
        self.value["cases"][0]["input"] += " "
        self.reject(self.value)

    def test_schema_drift_is_not_consumer_conformance(self):
        with self.assertRaisesRegex(conformance.ConformanceError, "schema-digest-mismatch"):
            conformance.inspect(self.raw, self.schema + b" ")

    def test_schema_path_cannot_select_another_file(self):
        for path in ("../schema.json", "https://example.invalid/schema.json", "other.json"):
            value = copy.deepcopy(self.value); value["schema"]["path"] = path
            self.reject(value)

    def test_duplicate_case_ids_rejected(self):
        self.value["cases"].append(copy.deepcopy(self.value["cases"][0]))
        self.reject(self.value)

    def test_unknown_family_and_fields_rejected(self):
        self.value["cases"][0]["family"] = "run-shell"
        self.reject(self.value)
        self.value = strict_json.loads(self.raw)
        self.value["cases"][0]["command"] = "must-not-execute"
        self.reject(self.value)

    def test_expectations_cannot_be_truthy_strings_or_numbers(self):
        for wrong in ("true", 1, None, {}):
            value = copy.deepcopy(self.value); value["cases"][0]["expected"] = wrong
            self.reject(value)

    def test_empty_corpus_or_missing_family_rejected(self):
        for cases in ([], [c for c in self.value["cases"] if c["family"] == "strict-json"]):
            value = copy.deepcopy(self.value); value["cases"] = cases
            self.reject(value)

    def test_metadata_version_limits_and_scope_are_explicit(self):
        for field, wrong in (("format_version", True), ("scope", "production-certified"),
                             ("limits", {"max_input_bytes": 999999}), ("not_checked", [])):
            value = copy.deepcopy(self.value); value[field] = wrong
            self.reject(value)

    def test_bad_hex_and_oversized_case_rejected(self):
        for text in ("ff0", "zz", "00 " * 5, "ff" * 4097):
            value = copy.deepcopy(self.value)
            value["cases"][0].update(encoding="hex", input=text)
            self.reject(value)

    def test_duplicate_keys_in_manifest_rejected(self):
        raw = self.raw.replace(b'"format_version": 1', b'"format_version": 1,"format_version": 1', 1)
        with self.assertRaises(conformance.ConformanceError):
            conformance.inspect(raw, self.schema)

    def test_stable_order_and_no_input_mutation(self):
        before = copy.deepcopy(self.value)
        a = self.inspect(self.value)
        self.assertEqual(self.value, before)
        self.value["cases"].reverse()
        b = self.inspect(self.value)
        self.assertEqual(a["results"], b["results"])
        self.assertNotEqual(a["corpus_sha256"], b["corpus_sha256"])

    def test_inspector_never_acquires_referenced_data(self):
        with patch("builtins.open", side_effect=AssertionError("unexpected acquisition")):
            result = conformance.inspect(self.raw, self.schema)
        self.assertTrue(result["conformant_with_corpus"])
        self.assertNotIn("input", result["results"][0])

    def test_unreadable_or_incomplete_evidence_not_completion(self):
        result = conformance.inspect(self.raw, self.schema)
        case = next(c for c in result["results"] if c["id"] == "audit.scan-incomplete-structurally-valid")
        self.assertTrue(case["actual"])
        self.assertFalse(result["completion_verified"])


if __name__ == "__main__":
    unittest.main()
