"""Ordinal binding regressions over synthetic records; no provider/model execution."""
import copy
import json
from pathlib import Path
import random
import unittest
from unittest.mock import patch

import decision_binding as binding
from test_decision_binding import fixtures


def ordinal_fixture():
    spec, request, receipt = fixtures()
    spec.update(decision_kind='ordinal', levels=['low', 'medium', 'high'])
    receipt['result'] = {'value': 'medium'}
    return spec, request, receipt


class OrdinalBinding(unittest.TestCase):
    def setUp(self):
        self.spec, self.request, self.receipt = ordinal_fixture()

    def report(self):
        return binding.inspect_binding(self.spec, self.request, self.receipt)

    def reject(self, result, code):
        self.receipt['result'] = result
        # Prove generic individual schemas do not establish cross-document domains.
        for role, value in zip(('spec', 'request', 'receipt'),
                               (self.spec, self.request, self.receipt)):
            binding.SCHEMAS[role].validate(value)
        report = self.report()
        self.assertFalse(report['consistent'], report)
        self.assertIn(code, report['errors'])
        return report

    def test_every_declared_level_is_checked_without_normalization(self):
        for level in self.spec['levels']:
            self.receipt['result'] = {'value': level}
            result = self.report()
            self.assertTrue(result['consistent'], result)
            self.assertTrue(result['result_domain_checked'])

    def test_numeric_endpoints_and_fractional_positions_are_valid(self):
        for position in (0, 1, 2, 0.0, 0.25, 1.5, 2.0, -0.0):
            with self.subTest(position=position):
                self.receipt['result'] = {'value': position}
                result = self.report()
                self.assertTrue(result['consistent'], result)
                self.assertTrue(result['result_domain_checked'])

    def test_boolean_is_not_a_numeric_position(self):
        for value in (True, False):
            with self.subTest(value=value):
                self.reject({'value': value}, 'invalid-ordinal-value')

    def test_null_containers_and_missing_value_are_not_a_result(self):
        for value in (None, [], {}, {'index': 1}):
            with self.subTest(value=value):
                self.reject({'value': value}, 'invalid-ordinal-value')
        self.reject({}, 'ordinal-result-required')
        self.reject({'alternatives': [0, 1]}, 'ordinal-result-required')

    def test_level_names_are_exact_and_numeric_strings_are_not_coerced(self):
        for value in ('Medium', ' medium', 'medium ', 'unknown', '1', ''):
            with self.subTest(value=value):
                self.reject({'value': value}, 'undeclared-ordinal-level')

    def test_out_of_range_and_extreme_positions_are_rejected(self):
        for value in (-1, -0.001, 2.001, 3, 1e300, -(10**1000), 10**1000):
            with self.subTest(value_type=type(value).__name__):
                self.reject({'value': value}, 'ordinal-position-out-of-range')

    def test_nonfinite_values_fail_before_domain_inspection(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            self.receipt['result'] = {'value': value}
            result = self.report()
            self.assertFalse(result['consistent'])
            self.assertIn('invalid-or-oversized-input', result['errors'])

    def test_distribution_only_is_supported_without_inventing_a_value(self):
        self.receipt['result'] = {'distribution': {'0': 0.2, '1': 0.5, '2': 0.3}}
        before = copy.deepcopy(self.receipt)
        result = self.report()
        self.assertTrue(result['consistent'], result)
        self.assertTrue(result['result_domain_checked'])
        self.assertEqual(before, self.receipt)
        self.assertNotIn('value', self.receipt['result'])

    def test_sparse_distribution_and_both_forms_are_supported(self):
        for value in (1.7, 'medium'):
            self.receipt['result'] = {'value': value, 'distribution': {'2': 1.0}}
            result = self.report()
            self.assertTrue(result['consistent'], result)
            # No universal mean/mode relationship is imposed by receipt v1.
            self.assertIn('ordinal-value-distribution-relationship', result['not_checked'])

    def test_distribution_cannot_hide_a_malformed_supplied_value(self):
        for value, code in [(None, 'invalid-ordinal-value'), (True, 'invalid-ordinal-value'),
                            (99, 'ordinal-position-out-of-range'), ('invented', 'undeclared-ordinal-level')]:
            self.reject({'value': value, 'distribution': {'1': 1.0}}, code)

    def test_named_levels_are_not_distribution_indexes(self):
        for label in self.spec['levels']:
            self.reject({'distribution': {label: 1.0}}, 'undeclared-distribution-option')

    def test_ambiguous_signed_padded_fractional_and_unicode_indexes_rejected(self):
        for label in ('01', '+1', '-0', ' 1', '1 ', '1.0', '1e0', '\u0661', '3', '-1', '9' * 1000):
            with self.subTest(label=label[:10]):
                self.reject({'distribution': {label: 1.0}}, 'undeclared-distribution-option')
        self.reject({'distribution': {'1': 0.5, '01': 0.5}}, 'undeclared-distribution-option')

    def test_distribution_normalization_is_retained(self):
        self.reject({'distribution': {}}, 'empty-result-distribution')
        self.reject({'distribution': {'0': 0.2}}, 'distribution-arithmetic-mismatch')
        for value in (True, -0.1, 1.1, '1'):
            self.receipt['result'] = {'distribution': {'0': value}}
            self.assertFalse(self.report()['consistent'])

    def test_numeric_looking_and_unicode_level_names_remain_literal(self):
        self.spec['levels'] = ['2', '0', 'eleve\u0301']
        for name in self.spec['levels']:
            self.receipt['result'] = {'value': name, 'distribution': {'0': 1.0}}
            self.assertTrue(self.report()['consistent'])
        self.reject({'value': 'elev\u00e9'}, 'undeclared-ordinal-level')

    def test_level_count_sets_numeric_domain_not_an_assumed_zero_one_scale(self):
        self.spec['levels'] = ['a', 'b', 'c', 'd', 'e']
        self.receipt['result'] = {'value': 3.5, 'distribution': {'4': 1.0}}
        self.assertTrue(self.report()['consistent'])
        self.reject({'value': 5}, 'ordinal-position-out-of-range')

    def test_nonproduced_states_remain_non_success_without_invented_score(self):
        for status in ('unknown', 'insufficient-evidence', 'conflicting-evidence',
                       'out-of-distribution', 'abstained', 'provider-failure'):
            self.receipt['status'] = status
            self.receipt.pop('result', None)
            result = self.report()
            self.assertTrue(result['consistent'])
            self.assertFalse(result['result_domain_checked'])
            self.assertEqual(result['recorded_status'], status)
            self.assertIn('non-produced-status', result['review_reasons'])
            self.assertFalse(result['decision_accepted'])

    def test_high_confidence_does_not_resolve_missing_evidence_or_authorize(self):
        self.receipt['uncertainty']['provider_confidence'] = 1.0
        self.receipt['uncertainty']['evidence_coverage'].update(required_present=1, value=0.5, missing=['policy'])
        self.receipt['policy']['disposition'] = 'accepted'
        result = self.report()
        self.assertTrue(result['consistent'])
        self.assertIn('missing-evidence-requires-review', result['review_reasons'])
        for key in ('claims_authenticated', 'current_evidence_verified', 'cache_reuse_authorized',
                    'decision_accepted', 'consequence_authorized'):
            self.assertIs(result[key], False)
        self.assertEqual(result['provider_calls'], 0)
        self.assertIsNone(result['model_tokens'])

    def test_no_reads_mutation_or_output_replay(self):
        self.spec['levels'] = ['PRIVATE_LEVEL_A', 'PRIVATE_LEVEL_B']
        self.receipt['result'] = {'value': 'PRIVATE_LEVEL_A'}
        before = copy.deepcopy((self.spec, self.request, self.receipt))
        with patch.object(Path, 'open', side_effect=AssertionError('no source reads')):
            first = self.report()
            self.assertEqual(first, self.report())
        self.assertTrue(first['consistent'])
        self.assertEqual(before, (self.spec, self.request, self.receipt))
        self.assertNotIn('PRIVATE_LEVEL', json.dumps(first))
        self.assertNotIn('fixture://', json.dumps(first))

    def test_duplicate_or_missing_level_definitions_remain_schema_errors(self):
        for levels in ([], ['only'], ['same', 'same']):
            self.spec['levels'] = levels
            self.assertIn('spec-schema-invalid', self.report()['errors'])
        del self.spec['levels']
        self.assertIn('spec-schema-invalid', self.report()['errors'])

    def test_result_type_validation_does_not_relax_state_identity(self):
        self.receipt['state']['fingerprint'] = 'another-recorded-state'
        result = self.report()
        self.assertFalse(result['consistent'])
        self.assertIn('state-fingerprint-mismatch', result['errors'])
        self.assertFalse(result['cache_reuse_authorized'])

    def test_random_positions_match_declared_range(self):
        rng = random.Random(141)
        for _ in range(100):
            size = rng.randint(2, 12)
            self.spec['levels'] = [f'level-{i}' for i in range(size)]
            position = rng.randint(-20, 80) / 4
            self.receipt['result'] = {'value': position}
            with self.subTest(size=size, position=position):
                self.assertEqual(self.report()['consistent'], 0 <= position <= size - 1)


if __name__ == '__main__':
    unittest.main()
