#!/usr/bin/env python3
"""Scoped completion shapes; these fixtures are not trusted runtime evidence."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
root = Path(__file__).resolve().parents[2]
schema = json.loads((root / 'catalog/schema/check-completion.v1.schema.json').read_text())
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)
d = 'sha256:' + 'a' * 64
manifest = {'format_version': 1, 'kind': 'check-evidence-manifest', 'run': {'path': 'evidence/run.json', 'digest': d}, 'governance': [], 'references': []}
verdict = {'format_version': 1, 'kind': 'check-completion', 'completion_verified': True, 'scope': 'declared-checks-and-required-controls', 'trust': 'caller-approved-exact-evidence', 'evidence_digest': d, 'run_digest': d, 'policy_digest': d, 'source_digest': d, 'evaluated_at_ms': 1, 'checks_passed': True, 'required_controls_satisfied': True, 'producer_authenticated': False, 'not_checked': ['signed producer authentication']}
for value in (manifest, verdict):
    v.validate(value)
    for field in value:
        invalid = copy.deepcopy(value)
        del invalid[field]
        assert not v.is_valid(invalid), field
for field, value in [('scope', 'whole-project'), ('producer_authenticated', True), ('trust', 'automatic'), ('checks_passed', False), ('evaluated_at_ms', -1), ('evidence_digest', 'unknown')]:
    invalid = dict(verdict, **{field: value})
    assert not v.is_valid(invalid), field
invalid = dict(manifest, approval=True)
assert not v.is_valid(invalid)
invalid = dict(manifest, governance=[{'path':'evidence/control.json','digest':d}])
assert not v.is_valid(invalid)
print('Completion manifest/verdict schema and rejection fixtures passed')
