#!/usr/bin/env python3
"""Validate public CLI contracts and positive/negative fixtures."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
root = Path(__file__).resolve().parents[2]
for path in (root / 'catalog/schema').glob('*.schema.json'):
    Draft202012Validator.check_schema(json.loads(path.read_text()))
schema = json.loads((root / 'catalog/schema/codebase-audit.v2.schema.json').read_text())
validator = Draft202012Validator(schema)
fixture = json.loads((root / '.agentic/evals/fixtures/codebase-audit.v2.json').read_text())
validator.validate(fixture)
for key, value in [('overall', 101), ('scores', {}), ('scores', {'testing': 'good'}),
                   ('format_version', 3), ('findings', [{}]), ('checks', {}),
                   ('architecture', {'compliance': {'deterministic_errors': -1, 'passed': True}})]:
    invalid = copy.deepcopy(fixture)
    invalid[key] = value
    assert not validator.is_valid(invalid), (key, value)
assert not validator.is_valid({})
print('CLI schemas and audit compatibility fixtures passed')
