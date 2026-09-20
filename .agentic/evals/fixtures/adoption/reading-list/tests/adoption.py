"""Bounded fixture regression tests; not a project check executor or completion ledger.

Usage: python3 tests/adoption.py /absolute/path/to/ah
Every mutation runs in a temporary copy. A missing binary is an error, not a skip.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

FIXTURE = Path(__file__).resolve().parents[1]
if len(sys.argv) != 2:
    raise SystemExit("usage: python3 tests/adoption.py /absolute/path/to/ah")
BINARY = Path(sys.argv.pop()).resolve(strict=True)
if not BINARY.is_file():
    raise SystemExit("ah must be a regular executable file")


class Adoption(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ah-reading-list-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(FIXTURE, self.root, ignore=shutil.ignore_patterns(
            "node_modules", "dist", "test-results", "playwright-report", "evidence", "__pycache__"))

    def call(self, *args, code=0):
        result = subprocess.run([str(BINARY), *args], cwd=self.root, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stderr if code == 2 else result.stdout)

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def config(self, path, update):
        value = json.loads((self.root / path).read_text())
        update(value)
        self.write(path, json.dumps(value, indent=2) + "\n")

    def seed_boundary(self):
        self.write("src/domain/violation.ts", "import Button from '../presentation/components/Button.vue';\nexport const outerControl = Button;\n")

    def architecture_gate(self, passed):
        audit = self.call("audit", ".", code=1)
        self.write("evidence/audit.json", json.dumps(audit))
        result = self.call("gate", "evidence/audit.json", "--fail-on-architecture-error", code=0 if passed else 1)
        self.assertEqual(result["passed"], passed)

    def test_clean_configuration_and_source_graph(self):
        result = self.call("architecture", "analyze", ".")
        self.assertEqual(result["compliance"], {"complete": True, "passed": True, "deterministic_errors": 0, "warnings": 0})
        self.assertIn("pattern/layered/1", result["profiles"])
        self.assertTrue(any(edge["from"].endswith("ReadingList.vue") and edge["to"].endswith("readingList.ts") for edge in result["graph"]["edges"]))
        design = self.call("audit", ".", code=1)["design_system"]
        self.assertTrue(design["active"])
        self.assertEqual(design["violations"], [])
        self.assertEqual(design["missing_components"], [])
        self.architecture_gate(True)

    def test_wrong_direction_has_exact_rule_and_path(self):
        self.seed_boundary()
        result = self.call("architecture", "analyze", ".")
        self.assertFalse(result["compliance"]["passed"])
        findings = [f for f in result["findings"] if f["rule_id"] == "layered.domain-independent"]
        self.assertEqual(len(findings), 1)
        self.assertIn("src/domain/violation.ts", json.dumps(findings[0]))
        self.assertIn("src/presentation/components/Button.vue", json.dumps(findings[0]))
        self.architecture_gate(False)

    def test_narrow_exception_and_expiry(self):
        self.seed_boundary()
        self.config(".agentic/architecture.json", lambda c: c.update(exceptions=[{
            "rule_id": "layered.domain-independent", "path": "src/domain/violation.ts",
            "rationale": "Synthetic compatibility bridge to exercise exception expiry only.", "expires": "2026-09-18",
        }]))
        allowed = self.call("architecture", "analyze", ".", "--as-of", "2026-09-18")
        self.assertTrue(allowed["compliance"]["passed"])
        self.assertTrue(allowed["suppressed_findings"])
        expired = self.call("architecture", "analyze", ".", "--as-of", "2026-09-19")
        self.assertFalse(expired["compliance"]["passed"])
        self.assertEqual(len(expired["expired_exceptions"]), 1)

    def test_raw_control_and_literal_color_and_explicit_exception(self):
        path = "src/presentation/views/Bypass.vue"
        self.write(path, '<template><button>Bypass</button></template>\n<style>button { color: #ff0000; }</style>\n')
        design = self.call("audit", ".", code=1)["design_system"]
        for rule in ["raw-control-bypass", "hardcoded-visual-value"]:
            found = [v for v in design["violations"] if v["type"] == rule]
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["evidence"][0]["path"], path)
        self.config(".agentic/design-system.json", lambda c: c.update(exceptions=[path]))
        self.assertEqual(self.call("audit", ".", code=1)["design_system"]["violations"], [])

    def test_dynamic_import_is_explicitly_incomplete(self):
        self.write("src/application/services/dynamic.ts", "export const load = (name: string) => import(name);\n")
        result = self.call("architecture", "analyze", ".")
        self.assertFalse(result["compliance"]["complete"])
        self.assertTrue(result["graph"]["unresolved_local_imports"])
        self.architecture_gate(False)

    def test_plan_is_read_only_and_invalidated_by_code_and_policy_drift(self):
        args = ("checks", "plan", ".", "--config", ".agentic/checks.json")
        before = self.call(*args)
        source = self.root / "src/domain/entry.ts"
        original = source.read_text()
        source.write_text(original + "\n// synthetic implementation change\n")
        self.assertNotEqual(before["review_digest"], self.call(*args)["review_digest"])
        source.write_text(original)
        self.assertEqual(before["review_digest"], self.call(*args)["review_digest"])
        self.config(".agentic/checks.json", lambda c: c.update(max_age_ms=1800000))
        self.assertNotEqual(before["review_digest"], self.call(*args)["review_digest"])
        self.assertFalse((self.root / "dist").exists())

    def test_repeated_install_upgrade_and_adapter_sync_preserve_authored_content(self):
        # Establish real CLI provenance before overlaying authored application
        # content. The committed fixture's unresolved lock is not an install.
        source = self.root
        self.root = Path(self.temp.name) / "installed"
        self.root.mkdir()
        self.call("init", ".", "--boilerplate", "web-app", "--context-profile", "minimal")
        for path in source.rglob("*"):
            if path.is_file() and path.name not in {"manifest.yaml", "lock.json"}:
                target = self.root / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        tracked = [p for p in self.root.rglob("*") if p.is_file() and p.name not in {"manifest.yaml", "lock.json"}]
        before = {p.relative_to(self.root): p.read_bytes() for p in tracked}
        pins = json.loads(subprocess.run([str(BINARY), "--version"], capture_output=True,
                                        text=True, check=True, timeout=15).stdout)["sources"]
        # init/upgrade may report conflicts for authored docs. Content must survive.
        for command in ["init", "init", "upgrade", "upgrade"]:
            extra = ["--allow-existing"] if command == "init" else []
            result = subprocess.run([str(BINARY), command, ".", "--boilerplate", "web-app", "--context-profile", "minimal", *extra],
                                    cwd=self.root, capture_output=True, text=True, timeout=45)
            self.assertIn(result.returncode, [0, 1], result.stdout + result.stderr)
            installed = json.loads((self.root / ".agentic/lock.json").read_text())
            self.assertEqual(installed["canonical_source"], pins["canonical"])
            self.assertEqual(installed["agents_source"], pins["agents"])
        for host, profile in [("codex", "base"), ("claude", "typed-ui")]:
            for _ in range(2):
                args = ("adapters", "sync", ".", "--host", host, "--profile", profile)
                plan = self.call(*args)
                result = self.call(*args, "--apply", "--review", plan["plan_digest"])
                self.assertEqual(result["status"], "applied")
        for path, data in before.items():
            self.assertEqual((self.root / path).read_bytes(), data, str(path))
        self.assertTrue((self.root / ".agents/adapters/LICENSE").exists())
        self.assertTrue((self.root / ".claude/rules/agentic-typed-ui.md").exists())


if __name__ == "__main__":
    version = subprocess.run([str(BINARY), "--version"], capture_output=True, text=True, check=True, timeout=15)
    print(version.stdout.strip(), flush=True)
    print("binary_sha256=" + hashlib.sha256(BINARY.read_bytes()).hexdigest(), flush=True)
    unittest.main(verbosity=2)
