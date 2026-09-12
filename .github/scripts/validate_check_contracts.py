#!/usr/bin/env python3
"""Structural contract regressions. No model, host or application checks execute."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'catalog/schema/checks.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


def fixture(name):
    return json.loads((ROOT / '.agentic/evals/fixtures' / name).read_text())


class CheckContracts(unittest.TestCase):
    def setUp(self):
        self.policy = fixture('check-policy.v1.json')
        self.evidence = fixture('governance-evidence.v1.json')

    def test_policy_valid(self):
        VALIDATOR.validate(self.policy)

    def test_independent_claims(self):
        VALIDATOR.validate(self.evidence)
        statuses = {c['capability']: c['status'] for c in self.evidence['claims']}
        self.assertEqual(statuses['declared'], 'verified')
        self.assertEqual(statuses['enforced'], 'unverified')

    def test_policy_negative_matrix(self):
        mutations = [
            ('format_version', 2), ('inputs', []), ('checks', []),
            ('max_age_ms', 0), ('max_age_ms', 86400001),
            ('unknown', True), ('inputs', ['src', 'src']),
        ]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                bad = copy.deepcopy(self.policy)
                bad[key] = value
                self.assertFalse(VALIDATOR.is_valid(bad))

    def test_command_negative_matrix(self):
        for key, value in [('argv', 'npm test'), ('argv', []), ('argv', ['sh -c']),
                           ('argv', ['../shell']), ('required', 'yes'),
                           ('timeout_ms', 0), ('timeout_ms', 300001),
                           ('max_output_bytes', -1), ('max_output_bytes', 1048577)]:
            with self.subTest(key=key, value=value):
                bad = copy.deepcopy(self.policy)
                bad['checks'][0][key] = value
                self.assertFalse(VALIDATOR.is_valid(bad))

    def test_all_optional_rejected(self):
        self.policy['checks'][0]['required'] = False
        self.assertFalse(VALIDATOR.is_valid(self.policy))

    def test_verified_requires_evidence_and_mechanism(self):
        for key, value in [('evidence_refs', []), ('mechanism', None)]:
            with self.subTest(key=key):
                bad = copy.deepcopy(self.evidence)
                bad['claims'][0][key] = value
                self.assertFalse(VALIDATOR.is_valid(bad))

    def test_verified_enforcement_requires_host_identity(self):
        claim = self.evidence['claims'][3]
        claim.update(status='verified', mechanism='synthetic host rule', evidence_refs=['fixture:blocked'])
        self.assertFalse(VALIDATOR.is_valid(self.evidence))
        self.evidence['host'] = {'id': 'synthetic-host', 'version': '1'}
        VALIDATOR.validate(self.evidence)
        self.assertEqual(self.evidence['claims'][1]['status'], 'unverified')

    def test_unsupported_and_failed_are_not_verified(self):
        for status in ['unsupported', 'failed']:
            with self.subTest(status=status):
                self.evidence['claims'][3]['status'] = status
                VALIDATOR.validate(self.evidence)

    def test_empty_or_unknown_evidence_rejected(self):
        for key, value in [('claims', []), ('source_digest', 'unknown'),
                           ('observed_at_ms', -1), ('host', {'id':'host'}),
                           ('extra', 'ignored')]:
            with self.subTest(key=key):
                bad = copy.deepcopy(self.evidence)
                bad[key] = value
                self.assertFalse(VALIDATOR.is_valid(bad))

    def test_stale_evidence_is_structurally_valid_not_trusted(self):
        # Freshness/authenticity require an evaluator and current inputs, not JSON Schema.
        self.evidence['observed_at_ms'] = 0
        VALIDATOR.validate(self.evidence)
        self.assertTrue(self.evidence['not_checked'])

    def test_plan_cannot_grant_execution(self):
        plan = {'format_version':1,'kind':'check-plan','policy':self.policy,
                'generator':{'format_version':1,'kind':'version','version':'fixture','sources':{}},
                'inputs':[{'path':'src','kind':'directory','digest':None}],
                'control_requirements':[{'rule_id':'architecture.boundaries','capability':'checked','status':'unverified'}],
                'execution_permitted':False,'checks_executed':False,'executable_identity_verified':False,
                'not_checked':['command execution'],
                'limits':{'max_file_bytes':2000000,'max_total_bytes':64000000,'max_entries':10000,'max_depth':64}}
        for key in ['policy_digest','source_digest','planner_digest','review_digest']:
            plan[key] = 'sha256:' + 'a'*64
        VALIDATOR.validate(plan)
        for key in ['execution_permitted','checks_executed','executable_identity_verified']:
            bad = copy.deepcopy(plan)
            bad[key] = True
            self.assertFalse(VALIDATOR.is_valid(bad))


if __name__ == '__main__':
    unittest.main()
