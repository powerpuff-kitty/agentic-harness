#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from validate_public_surface import (
    END, START, MAX_TEXT_BYTES, PUBLIC_REPOSITORIES,
    quick_start_errors, reference_errors, safe_path, unapproved_references,
    validate_public_surface,
)

# Construct a synthetic identifier; never preserve actual internal names in tests.
SYNTHETIC = "agentic" + "-harness" + "-synthetic-consumer"
COMMANDS = [["ah", "init", "./my-app", "--boilerplate", "web-app"], ["ah", "validate", "./my-app"], ["ah", "audit", "./my-app"]]


class PublicSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("catalog/quick-start.json", json.dumps({"format_version": 1, "kind": "public-quick-start", "commands": COMMANDS}))
        self.write("README.md", f"# Fixture\n\n{START}\n```bash\n" + "\n".join(" ".join(args) for args in COMMANDS) + f"\n```\n{END}\n")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_clean_fixture(self):
        self.assertEqual(validate_public_surface(self.root), [])

    def test_approved_names_urls_and_git_extensions(self):
        for name in PUBLIC_REPOSITORIES:
            for value in (name, name.upper(), f"https://github.com/powerpuff-kitty/{name}.git"):
                self.assertFalse(unapproved_references(value))

    def test_unapproved_bare_name(self):
        self.assertTrue(unapproved_references(SYNTHETIC))

    def test_case_insensitive_name(self):
        self.assertTrue(unapproved_references(SYNTHETIC.upper()))

    def test_url_encoding(self):
        self.assertTrue(unapproved_references(SYNTHETIC.replace("-", "%2D")))

    def test_unknown_suffix_is_not_allowed_prefix(self):
        self.assertTrue(unapproved_references("agentic-harness-cli" + "-synthetic"))

    def test_target_application_language_is_allowed(self):
        self.write("sample.md", "A web app or backend-api target owns its product truth.\n")
        self.assertEqual(reference_errors(self.root), [])

    def test_nested_hidden_document_and_line_number(self):
        self.write(".agentic/docs/note.md", f"# Note\n\n{SYNTHETIC}\n")
        self.assertEqual(reference_errors(self.root), [".agentic/docs/note.md:3: unapproved repository reference"])

    def test_diagnostics_do_not_echo_content(self):
        self.write("note.md", "unrelated-secret-example " + SYNTHETIC)
        result = "\n".join(reference_errors(self.root))
        self.assertNotIn(SYNTHETIC, result)
        self.assertNotIn("unrelated-secret-example", result)

    def test_filename_is_scanned_and_redacted(self):
        self.write(SYNTHETIC + ".md", "neutral")
        result = "\n".join(reference_errors(self.root))
        self.assertIn("[unapproved-reference].md", result)
        self.assertNotIn(SYNTHETIC, result)

    def test_path_control_characters_are_escaped(self):
        self.assertNotIn("\n", safe_path("a\nb.md"))

    def test_symlink_is_rejected_without_reading_target(self):
        target = self.write("source.md", "ordinary")
        try:
            (self.root / "linked.md").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.assertIn("linked.md: non-regular file not scanned", reference_errors(self.root))

    def test_symlink_directory_reports_incomplete_scope(self):
        directory = self.root / "original"
        directory.mkdir()
        try:
            (self.root / "linked").symlink_to(directory, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.assertIn("linked: symlink not scanned", reference_errors(self.root))

    def test_git_internal_history_is_out_of_scope(self):
        self.write(".git/example", SYNTHETIC)
        self.assertEqual(reference_errors(self.root), [])

    def test_generated_dist_text_is_scanned(self):
        self.write("dist/docs.md", SYNTHETIC)
        self.assertTrue(reference_errors(self.root))

    def test_oversized_text_is_not_silently_successful(self):
        self.write("large.txt", "x" * (MAX_TEXT_BYTES + 1))
        self.assertTrue(reference_errors(self.root))

    def test_invalid_encoding_is_not_silently_successful(self):
        (self.root / "bad.txt").write_bytes(b"\xff")
        self.assertTrue(reference_errors(self.root))

    def test_binary_payload_is_out_of_text_scope(self):
        (self.root / "binary.dat").write_bytes(b"\x00" + SYNTHETIC.encode())
        self.assertEqual(reference_errors(self.root), [])

    def test_unreadable_file_has_redacted_diagnostic(self):
        original = Path.open
        def guarded(path, *args, **kwargs):
            if path.name == "blocked.md":
                raise PermissionError("sensitive exception detail")
            return original(path, *args, **kwargs)
        self.write("blocked.md", "neutral")
        with patch.object(Path, "open", guarded):
            result = "\n".join(reference_errors(self.root))
        self.assertIn("unreadable", result)
        self.assertNotIn("sensitive exception detail", result)

    def test_missing_root_is_error(self):
        self.assertTrue(reference_errors(self.root / "missing"))

    def test_unsupported_command_drift(self):
        readme = self.root / "README.md"
        self.write("README.md", readme.read_text().replace("ah validate", "ah doctor"))
        self.assertTrue(quick_start_errors(self.root))

    def test_missing_markers(self):
        self.write("README.md", "# No example\n")
        self.assertTrue(quick_start_errors(self.root))

    def test_duplicate_markers(self):
        readme = (self.root / "README.md").read_text()
        self.write("README.md", readme + START)
        self.assertTrue(quick_start_errors(self.root))

    def test_invalid_quoting(self):
        readme = (self.root / "README.md").read_text()
        self.write("README.md", readme.replace("./my-app", "'./my-app", 1))
        self.assertTrue(quick_start_errors(self.root))

    def test_malformed_fixture(self):
        self.write("catalog/quick-start.json", "{")
        self.assertTrue(quick_start_errors(self.root))

    def test_boolean_version_rejected(self):
        self.write("catalog/quick-start.json", json.dumps({"format_version": True, "kind": "public-quick-start", "commands": COMMANDS}))
        self.assertTrue(quick_start_errors(self.root))

    def test_empty_command_rejected(self):
        self.write("catalog/quick-start.json", json.dumps({"format_version": 1, "kind": "public-quick-start", "commands": [[]]}))
        self.assertTrue(quick_start_errors(self.root))

    def test_arbitrary_shell_in_document_is_never_executed(self):
        self.write("README.md", f"{START}\n```bash\ntouch should-not-exist\n```\n{END}")
        self.assertTrue(quick_start_errors(self.root))
        self.assertFalse((self.root / "should-not-exist").exists())


if __name__ == "__main__":
    unittest.main()
