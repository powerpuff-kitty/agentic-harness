import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


codebase = load("codebase_audit", ROOT / "scripts" / "codebase_audit.py")


class CodebaseAuditTests(unittest.TestCase):
    def test_minimal_repo_reports_missing_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            result = codebase.audit(root)
            self.assertIn("scores", result)
            self.assertTrue(any(f["dimension"] == "testing" for f in result["findings"]))

    def test_well_structured_fixture_detects_ci_tests_and_security(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "tests").mkdir()
            (root / "docs").mkdir()
            (root / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")
            (root / "tests" / "test_app.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
            (root / "SECURITY.md").write_text("# Security\n", encoding="utf-8")
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            result = codebase.audit(root)
            self.assertGreaterEqual(result["scores"]["testing"], 70)
            self.assertGreaterEqual(result["scores"]["security"], 70)


if __name__ == "__main__":
    unittest.main()
