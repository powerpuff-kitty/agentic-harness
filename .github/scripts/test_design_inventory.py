"""Fixture coherence only; no rendered UI, source authenticity or publication approval."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'catalog/schema/design-system-inventory.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


def fixture():
    return {'format_version': 1, 'kind': 'design-system-inventory', 'catalogue_version': 1,
            'project': {'id': 'synthetic-project', 'profile': 'headless', 'revision': 'fixture'},
            'items': [{'id': 'button', 'kind': 'component', 'catalogue_id': 'button',
                       'applicability': 'optional', 'implementation': 'missing',
                       'verification': 'not-run', 'publication': 'private'}]}


class DesignInventory(unittest.TestCase):
    def test_implemented_items_require_nonempty_sources(self):
        for state in ('recipe-only', 'app-local', 'shared'):
            with self.subTest(state=state):
                value = fixture()
                item = value['items'][0]
                item['implementation'] = state
                self.assertFalse(VALIDATOR.is_valid(value))
                item['sources'] = []
                self.assertFalse(VALIDATOR.is_valid(value))
                item['sources'] = [{'path': 'fixture/component.ts'}]
                self.assertTrue(VALIDATOR.is_valid(value))

    def test_missing_implementation_can_explicitly_have_no_sources(self):
        value = fixture()
        VALIDATOR.validate(value)
        value['items'][0]['sources'] = []
        VALIDATOR.validate(value)

    def test_sources_require_a_nonempty_path(self):
        value = fixture()
        value['items'][0]['implementation'] = 'shared'
        for source in ({}, {'path': ''}, {'path': 42}):
            value['items'][0]['sources'] = [source]
            self.assertFalse(VALIDATOR.is_valid(value))

    def test_not_applicable_needs_reason(self):
        value = fixture()
        value['items'][0]['applicability'] = 'not-applicable'
        self.assertFalse(VALIDATOR.is_valid(value))
        value['items'][0]['reason'] = 'Synthetic non-visual capability.'
        self.assertTrue(VALIDATOR.is_valid(value))

    def test_unknown_catalogue_id_is_not_accepted(self):
        value = fixture()
        value['items'][0]['catalogue_id'] = 'invented-component'
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_publication_does_not_imply_implementation_or_verification(self):
        for publication in ('private', 'approved', 'published'):
            value = fixture()
            value['items'][0]['publication'] = publication
            original = copy.deepcopy(value)
            VALIDATOR.validate(value)
            self.assertEqual(value, original)
            self.assertEqual(value['items'][0]['verification'], 'not-run')

    def test_profile_requirements_use_known_vocabulary_and_acyclic_inheritance(self):
        data = json.loads((ROOT / 'catalog/packs/design-system/profiles.json').read_text())
        profiles = data['profiles']
        self.assertEqual(set(profiles), set(SCHEMA['properties']['project']['properties']['profile']['enum']))
        known = set(SCHEMA['$defs']['catalogueId']['enum'])
        for name, profile in profiles.items():
            self.assertEqual(len(profile['required']), len(set(profile['required'])))
            self.assertLessEqual(set(profile['required']), known)
            visited = set()
            current = name
            while current is not None:
                self.assertIn(current, profiles)
                self.assertNotIn(current, visited)
                visited.add(current)
                current = profiles[current].get('extends')


if __name__ == '__main__':
    unittest.main()
