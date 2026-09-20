"""Cross-document fixture tests, not provider execution or model-quality evidence."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import decision_binding as binding


def fixtures():
    spec = {'format_version': 1, 'kind': 'decision-spec', 'id': 'review.support', 'revision': 2,
            'decision_kind': 'boolean', 'description': 'Synthetic evidence support judgment.',
            'input': {'schema_id': 'review.state', 'schema_version': 1},
            'evidence': {'requirements': [
                {'id': 'policy', 'required': True, 'description': 'Applicable instructions.'},
                {'id': 'source', 'required': True, 'description': 'Current selected evidence.'},
                {'id': 'background', 'required': False, 'description': 'Optional context.'}]},
            'policy': {'risk': 'low', 'consequential_action': 'review-required'}}
    request = {'format_version': 1, 'kind': 'decision-request', 'request_id': 'synthetic-request',
               'state': {'schema_id': 'review.state', 'schema_version': 1,
                         'fingerprint': 'sha256:' + hashlib.sha256(b'fixture state').hexdigest(),
                         'snapshot_ref': 'fixture://not-resolved'},
               'questions': [{'spec_id': spec['id'], 'spec_revision': spec['revision']}],
               'mode': 'evaluation'}
    receipt = {'format_version': 1, 'kind': 'decision-receipt', 'id': 'synthetic-receipt',
               'spec': {'id': spec['id'], 'revision': spec['revision']},
               'state': {k: request['state'][k] for k in ('schema_id', 'schema_version', 'fingerprint')},
               'status': 'produced', 'result': {'value': True, 'distribution': {'false': 0.1, 'true': 0.9}},
               'provider': {'type': 'custom', 'id': 'synthetic-fixture-no-provider'},
               'uncertainty': {'provider_confidence': None, 'calibration': {'status': 'unknown'},
                               'evidence_coverage': {'value': 1.0, 'required_present': 2,
                                                     'required_total': 2, 'missing': []},
                               'evidence_reliability': None, 'decision_certainty': None},
               'evidence': {'used': ['fixture:policy', 'fixture:source'], 'missing': []},
               'policy': {'id': 'synthetic-review', 'revision': 1, 'disposition': 'review', 'reasons': []},
               'timing': {'decided_at': '2026-09-20T00:00:00Z'}}
    return spec, request, receipt


class DecisionBinding(unittest.TestCase):
    def setUp(self):
        self.spec, self.request, self.receipt = fixtures()

    def report(self):
        return binding.inspect_binding(self.spec, self.request, self.receipt)

    def error(self, name):
        result = self.report()
        self.assertFalse(result['consistent'], result)
        self.assertIn(name, result['errors'])
        return result

    def assert_shapes_valid(self):
        for name, value in zip(('spec', 'request', 'receipt'), (self.spec, self.request, self.receipt)):
            binding.SCHEMAS[name].validate(value)

    def test_valid_boolean_is_only_consistency(self):
        self.assert_shapes_valid()
        result = self.report()
        self.assertTrue(result['consistent'])
        self.assertTrue(result['result_domain_checked'])
        for key in ('claims_authenticated', 'current_evidence_verified', 'cache_reuse_authorized',
                    'decision_accepted', 'consequence_authorized'):
            self.assertIs(result[key], False)
        self.assertEqual(result['provider_calls'], 0)
        self.assertIsNone(result['model_tokens'])

    def test_schema_valid_receipt_from_different_state_is_rejected(self):
        self.receipt['state']['fingerprint'] = 'sha256:' + hashlib.sha256(b'other state').hexdigest()
        self.assert_shapes_valid()
        self.error('state-fingerprint-mismatch')

    def test_other_spec_revision_and_id_rejected(self):
        for key, value in [('revision', 3), ('id', 'review.other')]:
            with self.subTest(key=key):
                self.receipt = fixtures()[2]
                self.receipt['spec'][key] = value
                self.assert_shapes_valid()
                self.error('receipt-spec-mismatch')

    def test_spec_must_have_been_requested(self):
        self.request['questions'][0]['spec_revision'] = 3
        self.assert_shapes_valid()
        self.error('spec-not-requested')

    def test_duplicate_questions_are_ambiguous_not_silently_deduplicated(self):
        self.request['questions'] *= 2
        self.assert_shapes_valid()
        self.error('ambiguous-request-questions')

    def test_additional_distinct_requested_question_is_supported(self):
        self.request['questions'].append({'spec_id': 'review.other', 'spec_revision': 1})
        self.assertTrue(self.report()['consistent'])

    def test_state_schema_id_and_version_must_match_both_records(self):
        for target in (self.request, self.receipt):
            original = copy.deepcopy(target['state'])
            for key, value in [('schema_id', 'other.schema'), ('schema_version', 2), ('schema_version', '1')]:
                target['state'] = {**original, key: value}
                self.assert_shapes_valid()
                self.error('state-schema-mismatch')
            target['state'] = original

    def test_same_string_schema_version_supported_without_coercion(self):
        for state in (self.spec['input'], self.request['state'], self.receipt['state']):
            state['schema_version'] = 'v1'
        self.assertTrue(self.report()['consistent'])

    def test_float_revisions_and_format_versions_do_not_count_as_exact_integers(self):
        self.receipt['spec']['revision'] = 2.0
        self.error('non-exact-version-type')
        self.receipt = fixtures()[2]
        self.receipt['format_version'] = 1.0
        self.error('receipt-schema-invalid')

    def test_required_total_comes_from_spec_not_self_report(self):
        self.receipt['uncertainty']['evidence_coverage'].update(required_present=0, required_total=0)
        self.assert_shapes_valid()
        self.error('required-total-spec-mismatch')

    def test_duplicate_requirement_identity_rejected(self):
        self.spec['evidence']['requirements'].append(copy.deepcopy(self.spec['evidence']['requirements'][0]))
        self.assert_shapes_valid()
        self.error('duplicate-evidence-requirement')

    def test_optional_or_unknown_requirement_cannot_fill_required_missing_list(self):
        coverage = self.receipt['uncertainty']['evidence_coverage']
        coverage.update(required_present=1, value=0.5)
        for name in ('background', 'invented'):
            coverage['missing'] = [name]
            self.error('unknown-missing-requirement')

    def test_missing_count_and_coverage_arithmetic_are_checked(self):
        coverage = self.receipt['uncertainty']['evidence_coverage']
        coverage.update(required_present=1, missing=['policy'])
        self.error('coverage-arithmetic-mismatch')
        coverage.update(value=0.5, missing=[])
        self.error('coverage-missing-count-mismatch')

    def test_present_cannot_exceed_total(self):
        self.receipt['uncertainty']['evidence_coverage']['required_present'] = 3
        self.error('required-present-exceeds-total')

    def test_zero_requirements_uses_full_coverage_without_division_error(self):
        self.spec['evidence']['requirements'] = []
        self.receipt['uncertainty']['evidence_coverage'].update(required_present=0, required_total=0)
        self.assertTrue(self.report()['consistent'])
        self.receipt['uncertainty']['evidence_coverage']['value'] = 0
        self.error('coverage-arithmetic-mismatch')

    def test_high_confidence_never_removes_missing_evidence_review(self):
        self.receipt['uncertainty']['provider_confidence'] = 1.0
        self.receipt['uncertainty']['evidence_coverage'].update(required_present=1, value=0.5, missing=['policy'])
        self.receipt['policy']['disposition'] = 'accepted'  # A supplied claim, not evaluated authorization.
        result = self.report()
        self.assertTrue(result['consistent'])
        self.assertIn('missing-evidence-requires-review', result['review_reasons'])
        self.assertFalse(result['decision_accepted'])

    def test_used_and_missing_evidence_cannot_overlap(self):
        self.receipt['evidence']['missing'] = ['fixture:source']
        self.error('evidence-both-used-and-missing')

    def test_boolean_produced_value_is_not_coerced(self):
        for value in (0, 1, 'false', 'true', None, [], {}):
            with self.subTest(value=value):
                self.receipt['result']['value'] = value
                self.assert_shapes_valid()
                self.error('boolean-result-required')
        del self.receipt['result']['value']
        self.error('boolean-result-required')

    def test_choice_value_must_be_declared_and_case_exact(self):
        self.spec.update(decision_kind='choice', options=['safe', 'review'])
        self.receipt['result'] = {'value': 'review', 'distribution': {'safe': 0.2, 'review': 0.8}}
        self.assertTrue(self.report()['consistent'])
        for value in ('Review', 'invented', 1, False):
            self.receipt['result']['value'] = value
            self.error('undeclared-choice-result')

    def test_distribution_empty_bad_total_and_undeclared_labels(self):
        for distribution, error in [({}, 'empty-result-distribution'),
            ({'true': 0.8}, 'distribution-arithmetic-mismatch'),
            ({'yes': 1.0}, 'undeclared-distribution-option')]:
            self.receipt['result']['distribution'] = distribution
            self.error(error)
        self.receipt['result']['distribution'] = {'true': 1.0}  # Sparse is not forbidden by v1.
        self.assertTrue(self.report()['consistent'])

    def test_other_primitives_are_not_presented_as_typed_result_validation(self):
        self.spec.update(decision_kind='ranking')
        self.receipt['result'] = {'value': 'high'}
        result = self.report()
        self.assertTrue(result['consistent'])
        self.assertFalse(result['result_domain_checked'])
        self.assertIn('other-result-primitives-and-extensions', result['not_checked'])

    def test_non_produced_status_is_preserved_not_coerced_to_false(self):
        for status in ('unknown', 'insufficient-evidence', 'conflicting-evidence',
                       'out-of-distribution', 'abstained', 'provider-failure'):
            with self.subTest(status=status):
                self.receipt['status'] = status
                self.receipt.pop('result', None)
                result = self.report()
                self.assertTrue(result['consistent'])
                self.assertEqual(result['recorded_status'], status)
                self.assertIn('non-produced-status', result['review_reasons'])
                self.assertFalse(result['result_domain_checked'])

    def test_request_occurrence_and_payload_are_explicitly_unverified(self):
        first = self.report()
        self.request.update(request_id='another-identical-request')
        self.request['state']['payload'] = {'arbitrary': 'not hashed here'}
        self.assertEqual(first, self.report())
        self.assertIn('request-occurrence', first['not_checked'])
        self.assertIn('state-payload-fingerprint', first['not_checked'])

    def test_deterministic_output_no_input_mutation_or_content_replay(self):
        self.spec['description'] = 'PRIVATE_BODY_NOT_FOR_OUTPUT'
        self.request['state']['snapshot_ref'] = 'file:///not-to-be-opened'
        self.receipt['result']['extension'] = 'PRIVATE_BODY_NOT_FOR_OUTPUT'
        before = copy.deepcopy((self.spec, self.request, self.receipt))
        first = self.report()
        self.assertEqual(first, self.report())
        self.assertEqual(before, (self.spec, self.request, self.receipt))
        self.assertNotIn('PRIVATE_BODY', json.dumps(first))
        self.assertNotIn('file:///', json.dumps(first))

    def test_inspection_does_not_read_references(self):
        with patch.object(Path, 'open', side_effect=AssertionError('no reads during inspection')):
            self.assertTrue(self.report()['consistent'])

    def test_decode_rejects_duplicate_keys_nonfinite_and_bad_utf8(self):
        for raw in (b'{"id":1,"id":2}', b'NaN', b'Infinity', b'\xff', b'{'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                binding.decode(raw)
        for raw in ('{}', b'x' * (binding.MAX_BYTES + 1)):
            with self.assertRaises(ValueError):
                binding.decode(raw)

    def test_invalid_schema_non_json_values_and_oversize_are_fixed_failures(self):
        for value in (None, [], {}, {'extension': float('nan')}):
            result = binding.inspect_binding(value, self.request, self.receipt)
            self.assertFalse(result['consistent'])
        self.request['state']['payload'] = {'secret': 'x' * binding.MAX_BYTES}
        self.error('invalid-or-oversized-input')
        self.request['state']['payload'] = {'bad': set()}
        self.error('invalid-or-oversized-input')

    def test_huge_coverage_counts_do_not_trigger_overflow(self):
        self.receipt['uncertainty']['evidence_coverage'].update(required_total=1, required_present=10**1000)
        self.error('required-present-exceeds-total')

    def test_structure_limit_and_cyclic_objects_are_rejected(self):
        value = []
        value.append(value)
        self.request['state']['payload'] = {'cycle': value}
        self.error('invalid-or-oversized-input')
        self.request['state']['payload'] = {'items': [None] * 9000}
        self.error('invalid-or-oversized-input')


if __name__ == '__main__':
    unittest.main()
