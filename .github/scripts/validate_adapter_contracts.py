#!/usr/bin/env python3
"""Structural fixtures, not filesystem/host execution evidence."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'catalog/schema/adapter-sync.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


def example():
    d = 'sha256:' + 'a'*64
    return {'format_version':1,'kind':'adapter-sync','operation':'preview','host':'claude',
            'profile':'base','target':'/synthetic/project',
            'source':{'repository':'powerpuff-kitty/agentic-harness-agents','commit':'b'*40},
            'inventory_sha256':d,'router_sha256':d,'plan_digest':d,
            'entries':[{'source':'claude/files/CLAUDE.md','target':'CLAUDE.md','profile':'base',
                        'desired_sha256':d,'existing_sha256':None,'action':'create'}],
            'status':'ready','created_files':[],'created_directories':[],'error':None,
            'host_delivery_verified':False,'enforcement_verified':False,
            'limitations':['Synthetic fixture; no host execution.']}


class AdapterContracts(unittest.TestCase):
    def test_ready_preview(self):
        VALIDATOR.validate(example())

    def test_applied_is_not_host_evidence(self):
        value = example()
        value.update(operation='apply', status='applied', created_files=['CLAUDE.md'])
        VALIDATOR.validate(value)
        for key in ['host_delivery_verified','enforcement_verified']:
            bad = copy.deepcopy(value)
            bad[key] = True
            self.assertFalse(VALIDATOR.is_valid(bad))

    def test_conflict_never_claims_writes(self):
        value = example()
        value['status'] = 'conflict'
        value['entries'][0].update(action='conflict', existing_sha256='sha256:'+'b'*64)
        VALIDATOR.validate(value)
        value['created_files'] = ['CLAUDE.md']
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_partial_requires_error_and_apply(self):
        value = example()
        value.update(operation='apply', status='partial', error='synthetic failure', created_files=['CLAUDE.md'])
        VALIDATOR.validate(value)
        value['error'] = None
        self.assertFalse(VALIDATOR.is_valid(value))
        value.update(error='failure', operation='preview')
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_preview_cannot_create_files_or_directories(self):
        for key, value in [('created_files',['CLAUDE.md']),('created_directories',['.claude']),('status','applied')]:
            bad = example()
            bad[key] = value
            self.assertFalse(VALIDATOR.is_valid(bad))

    def test_invalid_targets_sources_and_digests(self):
        for key, value in [('target','.claude/settings.json'),('desired_sha256','unknown'),('existing_sha256','bad')]:
            bad = example()
            bad['entries'][0][key] = value
            self.assertFalse(VALIDATOR.is_valid(bad))
        bad = example()
        bad['source']['commit'] = 'main'
        self.assertFalse(VALIDATOR.is_valid(bad))

    def test_create_and_existing_state_are_distinct(self):
        for action, digest in [('create','sha256:'+'a'*64),('unchanged',None),('conflict',None)]:
            bad = example()
            bad['entries'][0].update(action=action,existing_sha256=digest)
            self.assertFalse(VALIDATOR.is_valid(bad))

    def test_native_no_op(self):
        value = example()
        value.update(host='codex',entries=[])
        VALIDATOR.validate(value)
        value['profile'] = 'typed-ui'
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_unknown_missing_and_duplicate_fields(self):
        bad = example()
        bad['extra'] = True
        self.assertFalse(VALIDATOR.is_valid(bad))
        del bad['extra']
        del bad['plan_digest']
        self.assertFalse(VALIDATOR.is_valid(bad))
        bad = example()
        bad.update(operation='apply', status='applied', created_files=['CLAUDE.md','CLAUDE.md'])
        self.assertFalse(VALIDATOR.is_valid(bad))


if __name__ == '__main__':
    unittest.main()
