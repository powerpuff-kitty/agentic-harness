"""Exercise supplied-record refresh planning; no model or source-authentication claims."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import context_checkpoint as checkpoint


def digest(text):
    return 'sha256:' + hashlib.sha256(text.encode()).hexdigest()


def source(name, role='source', text=None, reference=None):
    return {'id': name, 'reference': reference or 'fixture://' + name, 'role': role,
            'availability': 'recorded', 'sha256': digest(text or name)}


def record():
    return {'format_version': 1, 'kind': 'context-checkpoint', 'id': 'refresh-fixture',
            'authority': 'navigation-only', 'created_at': '2026-09-20T00:00:00Z',
            'producer': 'synthetic test; no model session',
            'task': {'id': 'task', 'goal': 'Inspect two independent modules.',
                     'scope': 'fixture repository; local review only; criteria v1',
                     'base_revision': 'base-a', 'status': 'in-progress'},
            'sources': [source('rules', 'instruction'), source('criteria', 'criterion'),
                        source('a'), source('b'), source('log', 'diagnostic')],
            'notes': [{'id': name + '-note', 'kind': 'observation',
                       'statement': 'PRIVATE_NOTE_BODY', 'source_ids': [name]} for name in ('a', 'b')],
            'checks': [{'id': 'unit-1', 'name': 'unit', 'attempt': 1, 'command': 'PRIVATE_COMMAND',
                        'status': 'passed', 'input_source_ids': ['a'],
                        'evidence_source_ids': ['log'], 'output_complete': True}],
            'open_items': [], 'next_steps': ['Review current evidence; do not inherit approval.']}


class CheckpointRefresh(unittest.TestCase):
    def setUp(self):
        self.previous = record()
        self.current = copy.deepcopy(self.previous)
        self.selection = [item['id'] for item in self.current['sources']]

    def plan(self, **kwargs):
        return checkpoint.plan_refresh(self.previous, self.current,
                                       current_source_ids=kwargs.get('selection', self.selection))

    def new_version(self, name, *, available=True):
        item = copy.deepcopy(next(s for s in self.current['sources'] if s['id'] == name))
        item['id'] += '-current'
        item['sha256'] = digest(name + '-changed') if available else None
        item['availability'] = 'recorded' if available else 'unavailable'
        self.current['sources'].append(item)
        self.selection = [item['id'] if old == name else old for old in self.selection]
        return item

    def note(self, result, name):
        return next(n for n in result['notes'] if n['id'] == name + '-note')

    def test_unchanged_declared_dependencies_do_not_certify_reuse(self):
        result = self.plan()
        self.assertEqual(result['dependency_state'], 'matching-recorded-inputs')
        self.assertEqual(result['global_review_reasons'], [])
        for key in ('source_freshness_verified', 'automatic_reuse_authorized',
                    'same_target_authenticated', 'check_success_verified', 'approval_transferred'):
            self.assertFalse(result['limits'][key])
        self.assertIsNone(result['limits']['model_tokens'])

    def test_source_change_is_selective_and_retains_historical_check(self):
        self.new_version('a')
        result = self.plan()
        self.assertEqual(self.note(result, 'a')['affected_source_ids'], ['a'])
        self.assertEqual(self.note(result, 'b')['dependency_state'], 'matching-recorded-inputs')
        self.assertEqual(result['checks'][0]['historical_status'], 'passed')
        self.assertEqual(result['checks'][0]['dependency_state'], 'review-required')
        self.assertEqual(result['history'], {'missing_check_ids': [], 'changed_check_ids': []})

    def test_policy_only_change_invalidates_notes_without_explicit_policy_link(self):
        self.new_version('rules')
        result = self.plan()
        self.assertIn('recorded-context-changed-or-unavailable', result['global_review_reasons'])
        self.assertTrue(all(n['dependency_state'] == 'review-required' for n in result['notes']))

    def test_criteria_only_change_requires_global_review(self):
        self.new_version('criteria')
        self.assertIn('recorded-context-changed-or-unavailable', self.plan()['global_review_reasons'])

    def test_added_context_requires_review_even_when_not_selected(self):
        self.current['sources'].append(source('nested-rules', 'instruction'))
        result = self.plan()
        self.assertIn('current-context-not-selected', result['global_review_reasons'])
        self.assertEqual(result['unselected_context_source_ids'], ['nested-rules'])
        self.selection.append('nested-rules')
        self.assertIn('new-selected-context', self.plan()['global_review_reasons'])

    def test_new_ordinary_source_is_visible_not_automatically_assumed_irrelevant(self):
        self.current['sources'].append(source('new-dependency'))
        self.selection.append('new-dependency')
        result = self.plan()
        self.assertTrue(result['selection_review_required'])
        self.assertEqual(result['new_selected_source_ids'], ['new-dependency'])
        self.assertEqual(result['dependency_state'], 'review-required')

    def test_unselected_source_is_not_a_cache_hit(self):
        result = self.plan(selection=[name for name in self.selection if name != 'a'])
        self.assertEqual(self.note(result, 'a')['affected_source_ids'], ['a'])
        self.assertEqual(next(s for s in result['sources'] if s['previous_id'] == 'a')['state'],
                         'not-selected')

    def test_unavailable_selected_source_is_not_a_cache_hit(self):
        self.new_version('a', available=False)
        result = self.plan()
        self.assertEqual(next(s for s in result['sources'] if s['previous_id'] == 'a')['state'],
                         'currently-unavailable')

    def test_previously_unknown_hash_does_not_become_matching(self):
        unknown = source('missing')
        unknown.update(availability='unavailable', sha256=None)
        self.previous['sources'].append(unknown)
        self.current['sources'].append(source('missing'))
        self.selection.append('missing')
        result = self.plan()
        self.assertEqual(next(s for s in result['sources'] if s['previous_id'] == 'missing')['state'],
                         'previously-unavailable')

    def test_ambiguous_current_versions_are_rejected_even_when_hashes_match(self):
        duplicate = copy.deepcopy(self.current['sources'][0])
        duplicate['id'] = 'other-rules'
        self.current['sources'].append(duplicate)
        self.selection.append('other-rules')
        with self.assertRaisesRegex(ValueError, '^ambiguous-current-source-version$'):
            self.plan()

    def test_explicit_selection_resolves_same_reference_versions(self):
        item = self.new_version('a')
        result = self.plan()
        self.assertEqual(next(s for s in result['sources'] if s['previous_id'] == 'a')['current_id'],
                         item['id'])

    def test_source_id_rename_does_not_hide_matching_reference_and_bytes(self):
        renamed = copy.deepcopy(self.current['sources'][3])  # b is not a check input.
        renamed['id'] = 'renamed-b'
        self.current['sources'].append(renamed)
        self.selection[self.selection.index('b')] = 'renamed-b'
        self.assertEqual(self.note(self.plan(), 'b')['dependency_state'], 'matching-recorded-inputs')

    def test_different_path_or_role_cannot_substitute_matching_content(self):
        for field, value in (('reference', 'fixture://different'), ('role', 'criterion')):
            with self.subTest(field=field):
                self.setUp()
                item = self.new_version('a')
                item['sha256'] = self.previous['sources'][2]['sha256']
                item[field] = value
                row = next(s for s in self.plan()['sources'] if s['previous_id'] == 'a')
                self.assertEqual(row['state'], 'not-selected')

    def test_task_identity_scope_goal_and_base_revision_changes_are_global(self):
        for field in ('id', 'goal', 'scope', 'base_revision'):
            with self.subTest(field=field):
                self.setUp()
                self.current['task'][field] = 'changed'
                result = self.plan()
                self.assertIn('task-' + field + '-changed', result['global_review_reasons'])
                self.assertTrue(all(n['dependency_state'] == 'review-required' for n in result['notes']))

    def test_unknown_base_revision_requires_review_but_status_change_is_not_scope_drift(self):
        self.current['task']['status'] = 'review-ready'
        self.assertEqual(self.plan()['global_review_reasons'], [])
        self.previous['task']['base_revision'] = self.current['task']['base_revision'] = None
        self.assertIn('unknown-base-revision', self.plan()['global_review_reasons'])

    def test_missing_log_affects_check_not_unrelated_note(self):
        self.new_version('log', available=False)
        result = self.plan()
        self.assertEqual(result['checks'][0]['affected_source_ids'], ['log'])
        self.assertEqual(self.note(result, 'b')['dependency_state'], 'matching-recorded-inputs')

    def test_failed_then_passing_history_and_capture_limits_survive(self):
        first = self.previous['checks'][0]
        first.update(status='failed', output_complete=False)
        second = copy.deepcopy(first)
        second.update(id='unit-2', attempt=2, status='passed', output_complete=None)
        self.previous['checks'].append(second)
        self.current = copy.deepcopy(self.previous)
        result = self.plan()
        self.assertEqual([(c['attempt'], c['historical_status'], c['historical_output_complete'])
                          for c in result['checks']], [(1, 'failed', False), (2, 'passed', None)])
        self.assertFalse(result['limits']['check_success_verified'])

    def test_removed_or_rewritten_attempt_is_exposed_not_erased(self):
        self.current['checks'] = []
        result = self.plan()
        self.assertEqual(result['history']['missing_check_ids'], ['unit-1'])
        self.assertEqual(len(result['checks']), 1)
        self.current = copy.deepcopy(self.previous)
        self.current['checks'][0]['status'] = 'failed'
        self.assertEqual(self.plan()['history']['changed_check_ids'], ['unit-1'])

    def test_changing_source_behind_old_check_id_cannot_rebind_history(self):
        self.current['sources'][2]['sha256'] = digest('new bytes behind same historical id')
        result = self.plan()
        self.assertEqual(result['history']['changed_check_ids'], ['unit-1'])
        self.assertIn('historical-check-records-diverged', result['global_review_reasons'])

    def test_blocking_items_remain_blocking_despite_matching_inputs(self):
        self.previous['open_items'] = [{'id': 'blocked', 'description': 'PRIVATE_BLOCKER',
                                       'blocking': True, 'source_ids': ['a']}]
        self.previous['task']['status'] = 'blocked'
        self.current = copy.deepcopy(self.previous)
        result = self.plan()
        self.assertTrue(result['open_items'][0]['blocking'])
        self.assertFalse(result['limits']['blocking_items_resolved'])

    def test_empty_dependency_list_stays_unknown(self):
        self.previous['open_items'] = [{'id': 'question', 'description': 'Unresolved question',
                                       'blocking': False, 'source_ids': []}]
        self.current = copy.deepcopy(self.previous)
        self.assertEqual(self.plan()['open_items'][0]['dependency_state'], 'no-recorded-inputs')

    def test_bad_selection_rejected_without_partial_plan(self):
        for selection in (None, [], {}, 'a', [True], [['a']], ['unknown'], ['a', 'a'], ['a'] * 257):
            with self.subTest(selection=str(selection)[:40]), self.assertRaises(ValueError):
                self.plan(selection=selection)

    def test_inconsistent_checkpoint_is_rejected(self):
        self.current['authority'] = 'approved'
        with self.assertRaisesRegex(ValueError, '^inconsistent-current-checkpoint$'):
            self.plan()
        self.current = copy.deepcopy(self.previous)
        self.previous['notes'][0]['source_ids'] = ['unknown']
        with self.assertRaisesRegex(ValueError, '^inconsistent-previous-checkpoint$'):
            self.plan()

    def test_current_record_cannot_predate_baseline_and_timezones_are_compared(self):
        self.current['created_at'] = '2026-09-20T01:00:00+02:00'
        with self.assertRaisesRegex(ValueError, '^current-checkpoint-predates-previous$'):
            self.plan()
        self.current['created_at'] = '2026-09-20T02:00:00+02:00'
        self.assertEqual(self.plan()['dependency_state'], 'matching-recorded-inputs')

    def test_deterministic_order_and_no_input_mutation_or_payload_replay(self):
        before = copy.deepcopy((self.previous, self.current, self.selection))
        result = self.plan()
        self.assertEqual((self.previous, self.current, self.selection), before)
        self.current['sources'].reverse()
        self.previous['sources'].reverse()
        self.previous['notes'].reverse()
        self.selection.reverse()
        self.assertEqual(self.plan(), result)
        output = json.dumps(result)
        for forbidden in ('PRIVATE_NOTE_BODY', 'PRIVATE_COMMAND', 'fixture://', 'sha256:'):
            self.assertNotIn(forbidden, output)

    def test_no_reference_resolution_or_filesystem_access_during_planning(self):
        with patch('builtins.open', side_effect=AssertionError('no reads')),\
             patch.object(Path, 'open', side_effect=AssertionError('no reads')):
            self.assertEqual(self.plan()['limits']['provider_calls'], 0)

    def test_real_changed_file_hashes_drive_only_dependent_refresh(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'evidence.txt'
            path.write_text('before', encoding='utf-8')
            old_hash = 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest()
            self.previous['sources'][2]['sha256'] = old_hash
            self.current = copy.deepcopy(self.previous)
            path.write_text('after!', encoding='utf-8')
            item = self.new_version('a')
            item['sha256'] = 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest()
            result = self.plan()
            self.assertEqual(self.note(result, 'a')['dependency_state'], 'review-required')
            self.assertEqual(self.note(result, 'b')['dependency_state'], 'matching-recorded-inputs')
            self.assertEqual(path.read_text(encoding='utf-8'), 'after!')


if __name__ == '__main__':
    unittest.main()
