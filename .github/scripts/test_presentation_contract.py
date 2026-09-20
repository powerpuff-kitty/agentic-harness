"""Structural cases for the portable visual schema; no real project assets."""
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from validate_presentation_contract import validate_contract
ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "catalog/packs/project-presentation"
SCHEMA = json.loads((ROOT / "catalog/schema/project-visuals.schema.json").read_text())
EXAMPLE = json.loads((PACK / "examples/visuals.json").read_text())
VOCAB = json.loads((PACK / "layouts.json").read_text())

class PresentationContractTests(unittest.TestCase):
    def test_schema_and_example(self):
        Draft202012Validator.check_schema(SCHEMA)
        Draft202012Validator(SCHEMA).validate(EXAMPLE)
    def test_coherence(self):
        validate_contract(ROOT)
    def test_every_layout(self):
        for name, layout in VOCAB["layouts"].items():
            with self.subTest(layout=name):
                value=copy.deepcopy(EXAMPLE)
                value["sections"][0]["layout"]=name
                value["sections"][0]["items"]=[copy.deepcopy(value["sections"][0]["items"][0]) for _ in range(layout["items"])]
                Draft202012Validator(SCHEMA).validate(value)
    def test_reject_invalid_structures(self):
        mutations = [
            lambda d:d.update(private_notes="not public"),
            lambda d:d.update(schemaVersion=2),
            lambda d:d.update(projectId="../secret"),
            lambda d:d["assets"]["desktop"].update(file="https://example.com/a.png"),
            lambda d:d["assets"]["desktop"].update(file="../private.png"),
            lambda d:d["assets"]["desktop"].update(file="vector.svg"),
            lambda d:d["assets"]["desktop"].update(width=0),
            lambda d:d["assets"]["desktop"].update(width=1.5),
            lambda d:d["assets"]["desktop"].update(height=20000),
            lambda d:d["assets"]["desktop"].update(sha256="bad"),
            lambda d:d["assets"]["desktop"].update(alt=""),
            lambda d:d["assets"]["desktop"]["rights"].update(status="pending"),
            lambda d:d["assets"]["desktop"]["rights"].update(basis="unknown"),
            lambda d:d["sections"][0].update(layout="arbitrary"),
            lambda d:d["sections"][0].update(style="display:none"),
            lambda d:d["sections"][0].update(modes=["overview","overview"]),
            lambda d:d["sections"][0].update(type="script"),
            lambda d:d["sections"][0].update(items=[]),
            lambda d:d["sections"][0]["items"][0].update(caption=""),
            lambda d:d["sections"][0]["items"][0].update(fit="stretch"),
            lambda d:d["sections"][0]["items"][0].update(ratio="calc(1/0)"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                value=copy.deepcopy(EXAMPLE);mutate(value)
                self.assertTrue(list(Draft202012Validator(SCHEMA).iter_errors(value)))
    def test_correct_item_count_required_for_all_layouts(self):
        for name, layout in VOCAB["layouts"].items():
            with self.subTest(layout=name):
                value=copy.deepcopy(EXAMPLE);value["sections"][0]["layout"]=name
                value["sections"][0]["items"]=[value["sections"][0]["items"][0]]*(layout["items"]+1)
                self.assertTrue(list(Draft202012Validator(SCHEMA).iter_errors(value)))

if __name__ == "__main__":
    unittest.main()
