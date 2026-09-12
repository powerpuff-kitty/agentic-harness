#!/usr/bin/env python3
"""Execution artifact shapes only; synthetic fixtures never execute a project command."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
CORE = json.loads((ROOT / 'catalog/schema/checks.v1.schema.json').read_text())
SCHEMA = json.loads((ROOT / 'catalog/schema/check-execution.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
REGISTRY = Registry().with_resource(CORE['$id'], Resource.from_contents(CORE))
VALIDATOR = Draft202012Validator(SCHEMA, registry=REGISTRY)
D = 'sha256:' + 'a' * 64


def review():
    policy = json.loads((ROOT / '.agentic/evals/fixtures/check-policy.v1.json').read_text())
    plan = {'format_version': 1, 'kind': 'check-plan', 'policy': policy,
            'policy_digest': D, 'source_digest': D, 'planner_digest': D, 'review_digest': D,
            'generator': {'format_version': 1, 'kind': 'version', 'version': 'fixture', 'sources': {}},
            'inputs': [{'path': 'src', 'kind': 'directory', 'digest': None}],
            'control_requirements': [], 'execution_permitted': False, 'checks_executed': False,
            'executable_identity_verified': False, 'not_checked': ['execution'],
            'limits': {'max_file_bytes': 2000000, 'max_total_bytes': 64000000, 'max_entries': 10000, 'max_depth': 64}}
    return {'format_version': 1, 'kind': 'check-execution-review', 'plan': plan,
            'config_path': '.agentic/checks.json', 'settings_path': '.agentic/check-execution.json',
            'settings_digest': D, 'target': '/synthetic/project', 'host': {'os': 'linux', 'arch': 'x86_64'},
            'tools': {'npm': {'path': '/synthetic/tool', 'canonical_path': '/synthetic/tool',
                              'sha256': D, 'size_bytes': 4, 'mode': 493, 'runtime_version': None}},
            'executor_sha256': D, 'environment': {'PATH': ''}, 'inherit_environment': False,
            'max_total_ms': 10000, 'approval_digest': D, 'execution_supported': True,
            'execution_permitted': False, 'checks_executed': False, 'not_checked': ['sandboxing']}


def result():
    stream = {'observed_bytes': 0, 'sha256': D, 'complete': True, 'hash_scope': 'complete-stream'}
    outcome = {'status': 'passed', 'started_at_ms': 0, 'ended_at_ms': 1, 'duration_ms': 1,
               'exit_code': 0, 'signal': None, 'spawned': True, 'direct_child_reaped': True,
               'process_group_cleanup': 'signal-sent-or-group-absent', 'output_disclosure': 'omitted',
               'stdout': stream, 'stderr': copy.deepcopy(stream)}
    return {'format_version': 1, 'kind': 'check-run', 'review': review(), 'approval_matched': True,
            'unsandboxed_acknowledged': True, 'checks_executed': True, 'checks_passed': True,
            'inputs_current': True, 'completion_verified': False, 'started_at_ms': 0,
            'ended_at_ms': 1, 'duration_ms': 1,
            'results': [{'id': 'unit', 'required': True, 'argv': ['npm', 'test'], 'cwd': '.',
                         'reason': None, 'outcome': outcome}], 'governance_controls': [],
            'not_checked': ['trusted evidence and global completion']}


class ExecutionContracts(unittest.TestCase):
    def test_positive_shapes_and_offline_plan_resolution(self):
        VALIDATOR.validate(review())
        VALIDATOR.validate(result())
        VALIDATOR.validate({'format_version': 1, 'kind': 'check-execution-settings',
                            'tools': {'npm': '/synthetic/tool'}, 'environment': {'PATH': ''}, 'max_total_ms': 1000})

    def test_preview_never_grants_execution(self):
        for key in ['checks_executed', 'execution_permitted', 'inherit_environment']:
            value = review()
            value[key] = True
            self.assertFalse(VALIDATOR.is_valid(value), key)

    def test_environment_and_unknown_fields_fail(self):
        for env in [{}, {'PATH': 12}, {'PATH': '', 'bad-key': 'x'}, {'PATH': '', 'TOKEN': 'a\nb'}]:
            value = review()
            value['environment'] = env
            self.assertFalse(VALIDATOR.is_valid(value))
        value = review()
        value['secret_extra'] = 'not allowed'
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_passed_checks_do_not_mean_verified_completion(self):
        value = result()
        value['completion_verified'] = True
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_invalidated_inputs_cannot_pass(self):
        value = result()
        value['inputs_current'] = False
        self.assertFalse(VALIDATOR.is_valid(value))
        value['checks_passed'] = False
        VALIDATOR.validate(value)

    def test_required_failure_cannot_be_reported_as_pass(self):
        for status in ['failed', 'timeout', 'output-limit', 'execution-error', 'skipped', 'unsupported']:
            value = result()
            value['results'][0]['outcome']['status'] = status
            self.assertFalse(VALIDATOR.is_valid(value), status)
            value['checks_passed'] = False
            VALIDATOR.validate(value)

    def test_pass_requires_execution_reaping_and_complete_output(self):
        for key, replacement in [('spawned', False), ('direct_child_reaped', False), ('exit_code', 7), ('stdout', None)]:
            value = result()
            value['results'][0]['outcome'][key] = replacement
            self.assertFalse(VALIDATOR.is_valid(value), key)

    def test_output_and_controls_do_not_publish_or_promote(self):
        value = result()
        value['results'][0]['outcome']['raw_output'] = 'must not be included'
        self.assertFalse(VALIDATOR.is_valid(value))
        value = result()
        value['governance_controls'] = [{'rule_id': 'rule', 'capability': 'enforced', 'status': 'verified'}]
        self.assertFalse(VALIDATOR.is_valid(value))


if __name__ == '__main__':
    unittest.main()
