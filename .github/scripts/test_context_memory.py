#!/usr/bin/env python3
"""Contract tests for #117; supplied-record consistency is not runtime memory or cache proof."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import context_memory as memory

ROOT = Path(__file__).resolve().parents[2]
D = "sha256:" + "a" * 64

def sha(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()

def source(source_id="src"):
    return {"id": source_id, "role": "source", "reference": "src/service.ts",
            "digest": D, "revision": "abc123", "required": True}

def summary():
    text = "Service owns outbound HTTP; callers use the service boundary."
    return {
        "format_version": 1, "kind": "context-summary", "id": "service.summary",
        "authority": "generated-non-canonical", "created_at": "2026-09-21T00:00:00Z",
        "producer": {"kind": "deterministic", "id": "fixture", "version": "1"},
        "scope": {"level": "file", "identity": "src/service.ts",
                  "ancestry": [{"level": "repository", "identity": "fixture"},
                               {"level": "module", "identity": "src"}]},
        "sources": [source()], "coverage": {"status": "complete", "missing": [], "not_checked": []},
        "summary": text, "summary_sha256": sha(text)
    }

def cache():
    value = {
        "format_version": 1, "kind": "context-cache-entry", "id": "analysis.service",
        "authority": "generated-non-canonical", "created_at": "2026-09-21T00:00:00Z",
        "artifact_type": "architecture-analysis",
        "repository": {"id": "fixture", "revision": "abc123"},
        "producer": {"kind": "deterministic", "id": "architecture-check", "version": "1"},
        "inputs": [{"id": "service", "kind": "source", "reference": "src/service.ts",
                    "digest": D, "revision": "abc123"}],
        "result": {"reference": "artifact:analysis/service", "digest": "sha256:" + "b" * 64},
        "identity_sha256": D
    }
    value["identity_sha256"] = memory.cache_identity(value)
    return value

def event(seq=1, event_id="event.1"):
    return {
        "format_version": 1, "kind": "context-event", "id": event_id,
        "authority": "historical-navigation-only", "sequence": seq,
        "occurred_at": f"2026-09-21T00:00:0{seq}Z",
        "producer": {"kind": "human", "id": "reviewer", "version": "recorded"},
        "event_type": "decision", "subject": "service boundary",
        "statement": "ADR-001 remains the accepted boundary.",
        "canonical_refs": [{"kind": "adr", "reference": ".agentic/decisions/ADR-001.md",
                            "digest": D, "revision": "abc123"}],
        "evidence_refs": [], "supersedes": []
    }

class SummaryContracts(unittest.TestCase):
    def test_valid_generated_summary(self):
        result = memory.inspect_summary(summary())
        self.assertTrue(result["valid"])
        self.assertTrue(result["summary_identity_matches"])
        self.assertFalse(result["canonical_truth"])
        self.assertFalse(result["source_authenticity_verified"])

    def test_summary_hash_change_is_detected(self):
        value = summary(); value["summary"] += " changed"
        self.assertIn("summary-identity-mismatch", memory.inspect_summary(value)["errors"])

    def test_duplicate_source_id_fails(self):
        value = summary(); value["sources"].append(copy.deepcopy(value["sources"][0]))
        self.assertIn("duplicate-source-id", memory.inspect_summary(value)["errors"])

    def test_partial_or_unknown_coverage_requires_gap(self):
        for state in ("partial", "unknown"):
            value = summary(); value["coverage"]["status"] = state
            self.assertIn("incomplete-summary-without-explicit-gap", memory.inspect_summary(value)["errors"])
            value["coverage"]["not_checked"] = ["generated code excluded"]
            self.assertTrue(memory.inspect_summary(value)["valid"])

    def test_complete_summary_cannot_hide_gap(self):
        value = summary(); value["coverage"]["missing"] = ["src/other.ts"]
        self.assertIn("complete-summary-has-gaps", memory.inspect_summary(value)["errors"])

    def test_scope_ancestry_order_and_repository_root(self):
        value = summary()
        value["scope"]["ancestry"] = [{"level":"module","identity":"src"},{"level":"repository","identity":"fixture"}]
        self.assertIn("invalid-scope-ancestry", memory.inspect_summary(value)["errors"])
        value = summary(); value["scope"] = {"level":"repository","identity":"fixture","ancestry":[{"level":"repository","identity":"fixture"}]}
        self.assertIn("repository-summary-has-ancestry", memory.inspect_summary(value)["errors"])

    def test_no_transcript_field_or_authority_promotion(self):
        for key, val in (("transcript", "private chat"), ("authority", "project-truth")):
            value = summary(); value[key] = val
            self.assertFalse(memory.inspect_summary(value)["valid"])

class CacheContracts(unittest.TestCase):
    def test_identity_is_stable_for_input_order(self):
        value = cache()
        second = {"id":"rules","kind":"rule","reference":"AGENTS.md","digest":"sha256:"+"c"*64,"revision":"abc123"}
        value["inputs"].append(second)
        left = memory.cache_identity(value)
        value["inputs"].reverse()
        self.assertEqual(left, memory.cache_identity(value))

    def test_matching_inputs_never_authorize_reuse(self):
        value = cache()
        current = {"repository": copy.deepcopy(value["repository"]), "inputs": copy.deepcopy(value["inputs"])}
        result = memory.inspect_cache(value, current)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "matching-recorded-inputs")
        self.assertFalse(result["reuse_authorized"])
        self.assertFalse(result["provider_call_authorized"])

    def test_changed_source_is_stale(self):
        value = cache()
        current = {"repository": copy.deepcopy(value["repository"]), "inputs": copy.deepcopy(value["inputs"])}
        current["inputs"][0]["digest"] = "sha256:" + "d" * 64
        result = memory.inspect_cache(value, current)
        self.assertEqual(result["status"], "stale-or-different-inputs")
        self.assertEqual(result["changed"], ["service"])

    def test_config_rule_and_repository_changes_are_detectable(self):
        value = cache()
        value["inputs"].extend([
            {"id":"config","kind":"configuration","reference":"tsconfig.json","digest":"sha256:"+"c"*64,"revision":"abc123"},
            {"id":"rules","kind":"rule","reference":"AGENTS.md","digest":"sha256:"+"d"*64,"revision":"abc123"}])
        value["identity_sha256"] = memory.cache_identity(value)
        current = {"repository": {"id":"fixture","revision":"def456"}, "inputs": copy.deepcopy(value["inputs"])}
        current["inputs"][1]["digest"] = "sha256:" + "e" * 64
        current["inputs"].pop()
        result = memory.inspect_cache(value, current)
        self.assertEqual(result["status"], "stale-or-different-inputs")
        self.assertIn("repository", result["changed"])
        self.assertIn("config", result["changed"])
        self.assertEqual(result["missing"], ["rules"])

    def test_extra_input_and_identity_tampering_are_detected(self):
        value = cache()
        current = {"repository": copy.deepcopy(value["repository"]), "inputs": copy.deepcopy(value["inputs"])}
        current["inputs"].append({"id":"new","kind":"source","reference":"new.ts","digest":"sha256:"+"f"*64,"revision":"abc123"})
        self.assertEqual(memory.inspect_cache(value, current)["extra"], ["new"])
        value["identity_sha256"] = D
        self.assertIn("cache-identity-mismatch", memory.inspect_cache(value)["errors"])

    def test_duplicate_cache_input_is_rejected(self):
        value = cache(); value["inputs"].append(copy.deepcopy(value["inputs"][0]))
        value["identity_sha256"] = memory.cache_identity(value)
        self.assertIn("duplicate-input-id", memory.inspect_cache(value)["errors"])

class EventContracts(unittest.TestCase):
    def test_valid_append_only_history(self):
        first, second = event(), event(2, "event.2")
        second["event_type"] = "change"; second["supersedes"] = ["event.1"]
        result = memory.inspect_events([first, second])
        self.assertTrue(result["valid"])
        self.assertFalse(result["canonical_truth_replaced"])
        self.assertFalse(result["authorization_granted"])

    def test_sequence_and_time_regressions_fail(self):
        first, second = event(), event(2, "event.2")
        second["sequence"] = 1
        second["occurred_at"] = "2026-09-20T23:59:59Z"
        errors = memory.inspect_events([first, second])["errors"]
        self.assertTrue(any("sequence" in item for item in errors))
        self.assertTrue(any("time-regression" in item for item in errors))

    def test_duplicate_id_and_unknown_supersedes_fail(self):
        first, second = event(), event(2, "event.1")
        second["supersedes"] = ["missing"]
        errors = memory.inspect_events([first, second])["errors"]
        self.assertIn("duplicate-event-id", errors)
        self.assertTrue(any("unknown-superseded-event" in item for item in errors))

    def test_event_requires_canonical_reference(self):
        value = event(); value["canonical_refs"] = []
        self.assertFalse(memory.inspect_events([value])["valid"])

    def test_event_cannot_embed_transcript_or_authority_upgrade(self):
        for key, val in (("transcript","private"),("authority","project-truth")):
            value = event(); value[key] = val
            self.assertFalse(memory.inspect_events([value])["valid"])

class Bounds(unittest.TestCase):
    def test_empty_events_and_oversized_records_refused(self):
        with self.assertRaises(memory.ContextMemoryError):
            memory.inspect_events([])
        value = summary(); value["summary"] = "x" * 70000; value["summary_sha256"] = sha(value["summary"])
        with self.assertRaises(memory.ContextMemoryError):
            memory.inspect_summary(value)

if __name__ == "__main__":
    unittest.main()
