#!/usr/bin/env python3
"""Source-snapshot validation and generated documentation regression tests."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import capability_status as status


def fixture():
    return json.loads((status.ROOT / status.SOURCE).read_text(encoding="utf-8"))


class CapabilityStatusTests(unittest.TestCase):
    def reject(self, value):
        with self.assertRaises(status.StatusError):
            status.validate(value)

    def test_current_snapshot_and_generated_document_match(self):
        status.validate(fixture())
        status.check()

    def test_order_is_deterministic_and_inputs_preserved(self):
        value = fixture(); before = copy.deepcopy(value)
        expected = status.render(value)
        self.assertEqual(value, before)
        value["capabilities"].reverse()
        value["sources"] = dict(reversed(list(value["sources"].items())))
        for item in value["capabilities"]:
            item["issues"].reverse(); item["evidence"].reverse()
        self.assertEqual(status.render(value), expected)

    def test_duplicate_capability_rejected(self):
        value = fixture(); value["capabilities"].append(copy.deepcopy(value["capabilities"][0]))
        self.reject(value)

    def test_unsupported_verified_or_release_claim_rejected(self):
        for field, claim in (("verification", "host-tested"), ("consumer_compatibility", "passed"),
                             ("release_inclusion", "released"), ("implementation", "production-ready")):
            value = fixture(); value["capabilities"][0][field] = claim
            self.reject(value)

    def test_missing_evidence_cannot_be_source_reviewed(self):
        value = fixture(); value["capabilities"][0]["evidence"] = []
        self.reject(value)

    def test_evidence_cannot_only_describe_another_owner(self):
        value = fixture(); value["capabilities"][0]["evidence"] = [{"source": "cli", "path": "README.md"}]
        self.reject(value)

    def test_unreviewed_planned_item_is_explicit(self):
        value = fixture(); item = value["capabilities"][0]
        item.update(implementation="planned", verification="not-checked", evidence=[])
        status.validate(value)
        item["implementation"] = "implemented"
        self.reject(value)

    def test_unknown_fields_cannot_smuggle_claims(self):
        for location in ("top", "source", "capability", "pin", "evidence"):
            value = fixture()
            target = {"top": value, "source": value["sources"]["canonical"],
                      "capability": value["capabilities"][0], "pin": value["consumer_pins"][0],
                      "evidence": value["capabilities"][0]["evidence"][0]}[location]
            target["approved"] = True
            self.reject(value)

    def test_exact_revisions_required(self):
        for revision in ("main", "abc123", "g" * 40, "a" * 39, None, {}):
            value = fixture(); value["sources"]["canonical"]["revision"] = revision
            self.reject(value)
            value = fixture(); value["consumer_pins"][0]["revision"] = revision
            self.reject(value)

    def test_duplicate_and_missing_pins_rejected(self):
        value = fixture(); value["consumer_pins"].append(copy.deepcopy(value["consumer_pins"][0]))
        self.reject(value)
        value = fixture(); value["consumer_pins"][0]["consumer"] = "unreviewed"
        self.reject(value)

    def test_equal_pin_does_not_claim_compatibility(self):
        value = fixture()
        value["consumer_pins"][0]["revision"] = value["sources"]["canonical"]["revision"]
        output = status.render(value)
        self.assertIn("same recorded revision", output)
        self.assertIn("Compatibility is not checked by revision equality", output)
        self.assertTrue(all(c["consumer_compatibility"] == "not-checked" for c in value["capabilities"]))

    def test_unsafe_evidence_paths_rejected(self):
        for path in ("../file", "/file", "a//b", "a/./b", "a/../b", "a\\b", "https://example.org", "x%2Fy"):
            value = fixture(); value["capabilities"][0]["evidence"][0]["path"] = path
            self.reject(value)

    def test_unknown_or_malformed_repository_rejected(self):
        for repository in ("example/unreviewed", [], {}):
            value = fixture(); value["sources"]["canonical"]["repository"] = repository
            self.reject(value)

    def test_duplicate_sources_and_evidence_rejected(self):
        value = fixture(); value["sources"]["other"] = copy.deepcopy(value["sources"]["canonical"])
        self.reject(value)
        value = fixture(); item = value["capabilities"][0]
        item["evidence"].append(copy.deepcopy(item["evidence"][0]))
        self.reject(value)

    def test_issue_numbers_must_be_unique_positive_integers(self):
        for issues in ([], [True], [-1], [1, 1], ["87"]):
            value = fixture(); value["capabilities"][0]["issues"] = issues
            self.reject(value)

    def test_dates_versions_and_limits(self):
        for day in ("2026-02-30", "20261011", "2026-1-1", None):
            value = fixture(); value["reviewed_at"] = day
            self.reject(value)
        value = fixture(); value["format_version"] = True; self.reject(value)
        value = fixture(); value["capabilities"] *= 129; self.reject(value)

    def test_nonfinite_inputs_and_control_text_rejected(self):
        value = fixture(); value["format_version"] = float("nan"); self.reject(value)
        value = fixture(); value["capabilities"][0]["name"] = "foo\nbar"; self.reject(value)

    def test_render_escapes_injected_markup(self):
        value = fixture(); item = value["capabilities"][0]
        item["name"] = "<script>|[link]`"
        output = status.render(value)
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;&#124;&#91;link&#93;&#96;", output)

    def test_render_does_not_read_referenced_files(self):
        value = fixture()
        with patch("builtins.open", side_effect=AssertionError("no evidence acquisition")):
            status.render(value)

    def test_fixed_path_check_detects_drift_and_write_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / status.SOURCE; source.parent.mkdir(parents=True)
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            output = root / status.OUTPUT; output.parent.mkdir(parents=True)
            status.check(root, write=True); status.check(root)
            output.write_bytes(output.read_bytes() + b"unreviewed")
            before = output.read_bytes()
            with self.assertRaisesRegex(status.StatusError, "^generated-status-drift$"):
                status.check(root)
            self.assertEqual(output.read_bytes(), before)

    def test_source_and_output_symlinks_are_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside.json"; outside.write_text(json.dumps(fixture()))
            source = root / status.SOURCE; source.parent.mkdir(parents=True)
            source.symlink_to(outside)
            with self.assertRaisesRegex(status.StatusError, "^symlinked-status-path$"):
                status.check(root, write=True)
            source.unlink(); source.write_text(json.dumps(fixture()))
            output = root / status.OUTPUT; output.parent.mkdir(parents=True)
            output.symlink_to(outside)
            before = outside.read_bytes()
            with self.assertRaisesRegex(status.StatusError, "^symlinked-status-path$"):
                status.check(root, write=True)
            self.assertEqual(outside.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
