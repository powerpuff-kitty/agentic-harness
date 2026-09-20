#!/usr/bin/env python3
"""Validate supplied workflow shapes and timelines. No project commands execute."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'catalog/schema/workflow-graph.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
D = 'sha256:' + 'a' * 64


def workflow():
    def task(task_id, kind, depends_on=(), required=True):
        return {'id': task_id, 'kind': kind, 'depends_on': list(depends_on), 'required': required,
                'read_only': True, 'isolation': 'shared-read-only', 'max_attempts': 1,
                'inputs': [], 'outputs': [task_id + '.result']}
    return {'format_version': 1, 'kind': 'workflow-graph', 'id': 'repo-audit',
            'description': 'Synthetic read-only repository audit fixture.',
            'limits': {'max_active_workers': 3, 'max_total_tasks': 8, 'max_elapsed_ms': 60000,
                       'max_token_budget': None, 'max_cost_microunits': None},
            'tasks': [task('architecture', 'analysis'), task('security', 'analysis'),
                      task('design', 'analysis'),
                      task('verify', 'verification', ('architecture', 'security', 'design')),
                      task('aggregate', 'aggregation', ('verify',))],
            'execution_permitted': False, 'verification_complete': False}


def run():
    results = []
    for task in workflow()['tasks']:
        start = {'verify': 1, 'aggregate': 2}.get(task['id'], 0)
        results.append({'id': task['id'], 'required': task['required'], 'status': 'passed',
                        'attempts': 1, 'started_at_ms': start, 'ended_at_ms': start + 1,
                        'evidence_refs': [], 'reason': None})
    return {'format_version': 1, 'kind': 'workflow-run', 'workflow_id': 'repo-audit',
            'workflow_digest': D, 'source_digest': D, 'started_at_ms': 0, 'ended_at_ms': 3,
            'complete': True, 'results': results,
            'coverage': {'total': 5, 'required': 5, 'executed': 5, 'passed': 5, 'failed': 0,
                         'skipped': 0, 'blocked': 0, 'unsupported': 0,
                         'execution_error': 0, 'unverified': 0}, 'not_checked': []}


def timing_errors(definition, result):
    """Compare supplied intervals, not process isolation or actual resource use."""
    errors = []
    start, end = result['started_at_ms'], result['ended_at_ms']
    if end < start:
        errors.append('run end precedes start')
    if end - start > definition['limits']['max_elapsed_ms']:
        errors.append('run exceeds elapsed-time limit')
    rows = {item['id']: item for item in result['results']}
    tasks = {task['id']: task for task in definition['tasks']}
    events = []
    for item in result['results']:
        task_id = item['id']
        left, right = item['started_at_ms'], item['ended_at_ms']
        if item['attempts'] == 0:
            if item['status'] in ('passed', 'failed', 'execution-error'):
                errors.append('execution status without attempt: ' + task_id)
            if left is not None or right is not None:
                errors.append('unexecuted task has timing: ' + task_id)
            continue
        if left is None or right is None:
            errors.append('execution timing missing: ' + task_id)
            continue
        if right < left:
            errors.append('task end precedes start: ' + task_id)
            continue
        if left < start or right > end:
            errors.append('task outside run interval: ' + task_id)
        if left < right:
            events.extend(((left, 1), (right, -1)))
        for dep in tasks.get(task_id, {}).get('depends_on', []):
            previous = rows.get(dep)
            if previous is None or previous['ended_at_ms'] is None:
                errors.append('dependency timing unavailable: ' + task_id)
            elif previous['ended_at_ms'] > left:
                errors.append('task starts before dependency ends: ' + task_id)
    active = peak = 0
    for _, delta in sorted(events):
        active += delta
        peak = max(peak, active)
    if peak > definition['limits']['max_active_workers']:
        errors.append('run exceeds active-worker limit')
    return errors


def semantic_errors(definition, result=None):
    if not VALIDATOR.is_valid(definition) or definition.get('kind') != 'workflow-graph':
        return ['invalid workflow shape']
    if result is not None and (not VALIDATOR.is_valid(result) or result.get('kind') != 'workflow-run'):
        return ['invalid run shape']
    errors = []
    tasks = definition['tasks']
    ids = [task['id'] for task in tasks]
    if len(ids) != len(set(ids)):
        errors.append('duplicate task id')
    known = set(ids)
    graph = {task['id']: task['depends_on'] for task in tasks}
    for task_id, deps in graph.items():
        for dep in deps:
            if dep not in known:
                errors.append(f'unknown dependency: {dep}')
            if dep == task_id:
                errors.append(f'self dependency: {task_id}')
    state = {}
    def visit(node):
        if state.get(node) == 1:
            errors.append('cycle')
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for dep in graph.get(node, []):
            if dep in known:
                visit(dep)
        state[node] = 2
    for node in ids:
        visit(node)
    if len(tasks) > definition['limits']['max_total_tasks']:
        errors.append('task count exceeds max_total_tasks')
    if result is None:
        return errors
    if result['workflow_id'] != definition['id']:
        errors.append('workflow identity mismatch')
    by_id = {task['id']: task for task in tasks}
    result_ids = [item['id'] for item in result['results']]
    if len(result_ids) != len(set(result_ids)):
        errors.append('duplicate result id')
    if known - set(result_ids):
        errors.append('missing task results')
    for item in result['results']:
        task = by_id.get(item['id'])
        if task is None:
            errors.append(f'unknown result task: {item["id"]}')
            continue
        if item['required'] != task['required']:
            errors.append(f'required mismatch: {item["id"]}')
        if item['attempts'] > task['max_attempts']:
            errors.append(f'attempt limit exceeded: {item["id"]}')
    required_ids = {task['id'] for task in tasks if task['required']}
    status_by_id = {item['id']: item['status'] for item in result['results']}
    if result['complete'] and any(status_by_id.get(task_id) != 'passed' for task_id in required_ids):
        errors.append('complete with incomplete required task')
    counts = {'total': len(result['results']), 'required': sum(1 for item in result['results'] if item['required']),
              'executed': sum(1 for item in result['results'] if item['attempts'] > 0),
              'passed': 0, 'failed': 0, 'skipped': 0, 'blocked': 0, 'unsupported': 0,
              'execution_error': 0, 'unverified': 0}
    for item in result['results']:
        key = 'execution_error' if item['status'] == 'execution-error' else item['status']
        counts[key] += 1
    if result['coverage'] != counts:
        errors.append('coverage mismatch')
    errors.extend(timing_errors(definition, result))
    return errors


class WorkflowGraphContracts(unittest.TestCase):
    def test_positive_shapes_and_semantics(self):
        definition = workflow()
        result = run()
        VALIDATOR.validate(definition)
        VALIDATOR.validate(result)
        self.assertEqual([], semantic_errors(definition, result))

    def test_definition_never_claims_execution_or_verification(self):
        for key in ['execution_permitted', 'verification_complete']:
            value = workflow()
            value[key] = True
            self.assertFalse(VALIDATOR.is_valid(value), key)

    def test_v1_is_read_only_and_bounded(self):
        value = workflow()
        value['tasks'][0]['read_only'] = False
        self.assertFalse(VALIDATOR.is_valid(value))
        value = workflow()
        value['limits']['max_active_workers'] = 17
        self.assertFalse(VALIDATOR.is_valid(value))
        value = workflow()
        value['tasks'][0]['max_attempts'] = 5
        self.assertFalse(VALIDATOR.is_valid(value))

    def test_unknown_dependency_duplicate_and_cycle_fail_semantics(self):
        value = workflow()
        value['tasks'][0]['depends_on'] = ['missing']
        self.assertIn('unknown dependency: missing', semantic_errors(value))
        value = workflow()
        value['tasks'][1]['id'] = 'architecture'
        self.assertIn('duplicate task id', semantic_errors(value))
        value = workflow()
        value['tasks'][0]['depends_on'] = ['aggregate']
        self.assertIn('cycle', semantic_errors(value))

    def test_required_nonpass_prevents_complete(self):
        definition = workflow()
        for status in ['failed', 'skipped', 'blocked', 'unsupported', 'execution-error', 'unverified']:
            result = run()
            result['results'][0]['status'] = status
            key = 'execution_error' if status == 'execution-error' else status
            result['coverage']['passed'] -= 1
            result['coverage'][key] += 1
            self.assertIn('complete with incomplete required task', semantic_errors(definition, result), status)
            result['complete'] = False
            self.assertEqual([], semantic_errors(definition, result), status)

    def test_missing_required_result_and_coverage_mismatch_fail(self):
        definition = workflow()
        result = run()
        result['results'].pop(0)
        self.assertIn('complete with incomplete required task', semantic_errors(definition, result))
        self.assertIn('coverage mismatch', semantic_errors(definition, result))

    def test_attempt_limit_and_required_identity_are_enforced(self):
        definition = workflow()
        result = run()
        result['results'][0]['attempts'] = 2
        self.assertIn('attempt limit exceeded: architecture', semantic_errors(definition, result))
        result = run()
        result['results'][0]['required'] = False
        self.assertIn('required mismatch: architecture', semantic_errors(definition, result))


class WorkflowTimelineContracts(unittest.TestCase):
    def test_workflow_identity(self):
        result = run()
        result['workflow_id'] = 'different-workflow'
        self.assertIn('workflow identity mismatch', semantic_errors(workflow(), result))

    def test_omitted_optional_result_is_still_visible(self):
        definition, result = workflow(), run()
        definition['tasks'][0]['required'] = False
        result['results'].pop(0)
        self.assertIn('missing task results', semantic_errors(definition, result))

    def test_pass_without_execution_attempt_is_rejected(self):
        result = run()
        result['results'][0].update(attempts=0, started_at_ms=None, ended_at_ms=None)
        result['coverage']['executed'] -= 1
        self.assertIn('execution status without attempt: architecture', semantic_errors(workflow(), result))

    def test_reversed_run_interval(self):
        result = run()
        result.update(started_at_ms=4, ended_at_ms=3)
        self.assertIn('run end precedes start', semantic_errors(workflow(), result))

    def test_reversed_task_interval(self):
        result = run()
        result['results'][0].update(started_at_ms=2, ended_at_ms=1)
        self.assertIn('task end precedes start: architecture', semantic_errors(workflow(), result))

    def test_missing_execution_timing(self):
        for key in ('started_at_ms', 'ended_at_ms'):
            result = run()
            result['results'][0][key] = None
            self.assertIn('execution timing missing: architecture', semantic_errors(workflow(), result))

    def test_task_is_within_run_interval(self):
        result = run()
        result['results'][-1]['ended_at_ms'] = 4
        self.assertIn('task outside run interval: aggregate', semantic_errors(workflow(), result))

    def test_elapsed_budget(self):
        definition = workflow()
        definition['limits']['max_elapsed_ms'] = 2
        self.assertIn('run exceeds elapsed-time limit', semantic_errors(definition, run()))

    def test_dependencies_must_finish_before_start(self):
        result = run()
        result['results'][3]['started_at_ms'] = 0
        self.assertIn('task starts before dependency ends: verify', semantic_errors(workflow(), result))

    def test_concurrency_is_checked(self):
        definition = workflow()
        definition['limits']['max_active_workers'] = 2
        self.assertIn('run exceeds active-worker limit', semantic_errors(definition, run()))

    def test_touching_and_zero_duration_intervals_do_not_double_count(self):
        definition, result = workflow(), run()
        definition['limits']['max_active_workers'] = 1
        for index, item in enumerate(result['results']):
            item.update(started_at_ms=index, ended_at_ms=index + 1)
        result['ended_at_ms'] = 5
        original = copy.deepcopy((definition, result))
        self.assertEqual([], semantic_errors(definition, result))
        self.assertEqual(original, (definition, result))
        for item in result['results']:
            item.update(started_at_ms=0, ended_at_ms=0)
        result['ended_at_ms'] = 0
        self.assertEqual([], semantic_errors(definition, result))

    def test_unexecuted_blocked_graph_can_report_incomplete(self):
        result = run()
        result['complete'] = False
        for item in result['results']:
            item.update(status='blocked', attempts=0, started_at_ms=None, ended_at_ms=None)
        result['coverage'].update(executed=0, passed=0, blocked=5)
        self.assertEqual([], semantic_errors(workflow(), result))


if __name__ == '__main__':
    unittest.main()
