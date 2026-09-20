"""Contract/semantic regressions, not a model trial or evidence authentication."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import context_checkpoint as checkpoint

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / '.agentic/evals/fixtures/context-checkpoint.v1.json').read_text())


class ContextCheckpoint(unittest.TestCase):
    def setUp(self):
        self.value = copy.deepcopy(FIXTURE)

    def reject(self, expected=None):
        result = checkpoint.inspect(self.value)
        self.assertFalse(result['consistent'], result)
        if expected:
            self.assertIn(expected, result['errors'])
        return result

    def test_synthetic_checkpoint_retains_failure_retry_and_blocker(self):
        result = checkpoint.inspect(self.value)
        self.assertTrue(result['consistent'], result)
        self.assertEqual([c['status'] for c in self.value['checks']], ['failed', 'passed', 'not-run'])
        for field in ('source_freshness_verified', 'claims_authenticated', 'checks_executed',
                      'approval_transferred', 'token_savings_verified'):
            self.assertIs(result[field], False)
        self.assertEqual(result['model_execution'], 'not-performed')

    def test_completed_and_authorizing_states_are_not_accepted(self):
        for field, value in [('authority', 'approved-policy'), ('task', {
            **self.value['task'], 'status': 'completed'
        }), ('approval_transferred', True), ('token_savings_verified', True)]:
            with self.subTest(field=field):
                self.value = copy.deepcopy(FIXTURE)
                self.value[field] = value
                self.reject('schema-invalid')

    def test_duplicate_id_in_every_section(self):
        for section in ('sources', 'notes', 'checks', 'open_items'):
            with self.subTest(section=section):
                self.value = copy.deepcopy(FIXTURE)
                self.value[section].append(copy.deepcopy(self.value[section][0]))
                self.reject('duplicate-id:' + section)

    def test_all_source_reference_types_are_bound(self):
        for section, key in [('notes', 'source_ids'), ('checks', 'input_source_ids'),
                             ('checks', 'evidence_source_ids'), ('open_items', 'source_ids')]:
            with self.subTest(section=section, key=key):
                self.value = copy.deepcopy(FIXTURE)
                self.value[section][0][key] = ['invented']
                self.reject('unknown-source-reference')

    def test_recorded_source_requires_digest(self):
        self.value['sources'][0]['sha256'] = None
        self.reject('schema-invalid')

    def test_unavailable_source_does_not_invent_digest(self):
        self.value['sources'][-1]['sha256'] = 'sha256:' + 'a' * 64
        self.reject('schema-invalid')

    def test_unavailable_source_cannot_support_observation(self):
        self.value['notes'][0]['source_ids'] = ['browser-log']
        self.reject('unavailable-supporting-source')

    def test_unavailable_input_or_log_cannot_support_pass(self):
        for key in ('input_source_ids', 'evidence_source_ids'):
            with self.subTest(key=key):
                self.value = copy.deepcopy(FIXTURE)
                self.value['checks'][1][key] = ['browser-log']
                self.reject('unavailable-supporting-source')

    def test_decision_note_requires_decision_source(self):
        self.value['notes'][0]['kind'] = 'decision-reference'
        self.reject('decision-source-required')
        self.value['sources'][2]['role'] = 'decision'
        self.assertTrue(checkpoint.inspect(self.value)['consistent'])

    def test_source_path_is_not_diagnostic_evidence(self):
        self.value['checks'][0]['evidence_source_ids'] = ['before']
        self.reject('incorrect-source-role')

    def test_executed_checks_require_command_inputs_and_log(self):
        for key, value in [('command', None), ('input_source_ids', []), ('evidence_source_ids', [])]:
            with self.subTest(key=key):
                self.value = copy.deepcopy(FIXTURE)
                self.value['checks'][1][key] = value
                self.reject('executed-check-provenance-required')

    def test_unexecuted_check_cannot_claim_execution_log(self):
        self.value['checks'][2]['evidence_source_ids'] = ['passing-log']
        self.reject('unexecuted-check-has-execution-evidence')

    def test_dropped_failed_first_attempt_is_visible(self):
        self.value['checks'].pop(0)
        self.reject('incomplete-or-duplicate-attempt-history')

    def test_attempt_gap_and_duplicate_are_rejected(self):
        for attempt in (1, 3):
            with self.subTest(attempt=attempt):
                self.value = copy.deepcopy(FIXTURE)
                self.value['checks'][1]['attempt'] = attempt
                self.reject('incomplete-or-duplicate-attempt-history')

    def test_changed_check_command_is_not_a_retry_of_same_check(self):
        self.value['checks'][1]['command'] = 'synthetic-test a-different-check'
        self.reject('check-command-changed-within-history')

    def test_unknown_unexecuted_command_does_not_invent_a_run(self):
        self.value['checks'][0].update(status='not-run', command=None, evidence_source_ids=[], output_complete=None)
        self.assertTrue(checkpoint.inspect(self.value)['consistent'])

    def test_blocking_item_requires_blocked_status(self):
        for status in ('in-progress', 'review-ready'):
            self.value['task']['status'] = status
            self.reject('blocking-item-status-mismatch')

    def test_nonblocking_question_does_not_block_review_state(self):
        self.value['open_items'][0]['blocking'] = False
        self.value['task']['status'] = 'review-ready'
        result = checkpoint.inspect(self.value)
        self.assertTrue(result['consistent'])
        self.assertFalse(result['checks_executed'])

    def test_multiple_versions_of_same_path_keep_distinct_source_ids(self):
        self.value['sources'][1]['reference'] = 'src/counter.py'
        self.value['sources'][2]['reference'] = 'src/counter.py'
        self.assertNotEqual(self.value['sources'][1]['sha256'], self.value['sources'][2]['sha256'])
        self.assertTrue(checkpoint.inspect(self.value)['consistent'])

    def test_no_reference_resolution_or_execution(self):
        self.value['sources'][0]['reference'] = 'https://invalid.example/do-not-fetch'
        self.value['checks'][0]['command'] = self.value['checks'][1]['command'] = 'DO NOT EXECUTE'
        with patch.object(Path, 'open', side_effect=AssertionError('must not open references')):
            self.assertTrue(checkpoint.inspect(self.value)['consistent'])

    def test_explicit_unknown_base_revision_is_supported(self):
        self.assertIsNone(self.value['task']['base_revision'])
        self.assertTrue(checkpoint.inspect(self.value)['consistent'])

    def test_zero_false_and_float_versions_attempts_are_rejected(self):
        for version in (True, 1.0, 0):
            with self.subTest(version=version):
                self.value = copy.deepcopy(FIXTURE)
                self.value['format_version'] = version
                self.reject('schema-invalid')
        for attempt in (True, 1.0, 0):
            with self.subTest(attempt=attempt):
                self.value = copy.deepcopy(FIXTURE)
                self.value['checks'][0]['attempt'] = attempt
                self.reject()

    def test_recorded_time_requires_valid_date_seconds_and_timezone(self):
        for value in ('2026-02-30T01:02:03Z', '2026-09-20', '2026-09-20T01:02:03',
                      '2026-09-20T01:02:03+25:00', 'not-a-time'):
            with self.subTest(value=value):
                self.value['created_at'] = value
                self.reject()
        for value in ('2026-09-20T01:02:03Z', '2026-09-20T01:02:03.123456+02:00'):
            self.value['created_at'] = value
            self.assertTrue(checkpoint.inspect(self.value)['consistent'])

    def test_invalid_and_nonfinite_json_fail_closed(self):
        for raw in (b'{"kind":1,"kind":2}', b'{"v":NaN}', b'\xff', b'[', b'[]'*40000):
            with self.subTest(raw=raw[:20]), self.assertRaises(ValueError):
                checkpoint.decode(raw)
        for value in (None, [], {}, {'v': float('inf')}):
            self.assertFalse(checkpoint.inspect(value)['consistent'])

    def test_bounded_input_and_serialized_record(self):
        with self.assertRaises(ValueError):
            checkpoint.decode(b' ' * (checkpoint.MAX_BYTES + 1))
        with patch.object(checkpoint, 'MAX_BYTES', 100):
            self.reject('checkpoint-size-limit')
        self.value['notes'][0]['statement'] = 'x' * 2049
        self.reject('schema-invalid')

    def test_errors_do_not_echo_source_or_task_text(self):
        self.value['notes'][0]['statement'] = 'private marker'
        self.value['notes'][0]['source_ids'] = ['missing']
        result = self.reject()
        self.assertNotIn('private marker', json.dumps(result))

    def test_unknown_prior_attempt_is_explicit_not_a_fabricated_pass(self):
        self.value['checks'][0].update(status='unknown', command=None,
                                       input_source_ids=[], evidence_source_ids=[])
        result = checkpoint.inspect(self.value)
        self.assertTrue(result['consistent'])
        self.assertFalse(result['claims_authenticated'])

    def test_controls_and_trailing_newlines_are_rejected(self):
        for path, value in [(('id',), 'id\n'), (('producer',), 'actor\n'),
                            (('sources', 0, 'sha256'), 'sha256:' + 'a' * 64 + '\n')]:
            with self.subTest(path=path):
                self.value = copy.deepcopy(FIXTURE)
                parent = self.value
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = value
                self.reject('schema-invalid')

    def test_output_completeness_is_explicit_and_not_a_verification_claim(self):
        for complete in (True, False, None):
            self.value['checks'][1]['output_complete'] = complete
            result = checkpoint.inspect(self.value)
            self.assertTrue(result['consistent'])
            self.assertFalse(result['claims_authenticated'])
        self.value['checks'][1].pop('output_complete')
        self.reject('schema-invalid')
        self.value = copy.deepcopy(FIXTURE)
        self.value['checks'][2]['output_complete'] = True
        self.reject('unexecuted-check-has-execution-evidence')

    def test_json_roundtrip_and_deterministic_inspection(self):
        encoded = json.dumps(self.value).encode()
        self.assertEqual(checkpoint.decode(encoded), self.value)
        self.assertEqual(checkpoint.inspect(self.value), checkpoint.inspect(checkpoint.decode(encoded)))


if __name__ == '__main__':
    unittest.main()
