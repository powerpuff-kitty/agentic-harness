import copy
import json
import unittest

from validate_context_profiles import ROOT, validate


class ContextProfiles(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "catalog/context/profiles.v1.json").read_text())

    def test_current_contract(self):
        self.assertEqual(validate(ROOT, self.data), [])

    def test_rejects_lost_core_and_unsafe_paths(self):
        for replacement in [".agentic/REFERENCE.md", "../outside", "/outside", "C:\\outside"]:
            with self.subTest(replacement=replacement):
                invalid = copy.deepcopy(self.data)
                invalid["minimal"]["core_files"][0] = replacement
                self.assertTrue(validate(ROOT, invalid))

    def test_rejects_unknown_references_and_duplicate_core(self):
        for key, value in [("design_variants", ["absent"]), ("design_packs", ["absent"]),
                           ("design_fallback_variant", "absent"), ("module_routers", {})]:
            with self.subTest(key=key):
                invalid = copy.deepcopy(self.data)
                invalid["minimal"][key] = value
                self.assertTrue(validate(ROOT, invalid))
        self.data["minimal"]["core_files"].append("README.md")
        self.assertTrue(validate(ROOT, self.data))


if __name__ == "__main__":
    unittest.main()
