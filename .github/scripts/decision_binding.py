"""Inspect supplied Decision Kernel bindings; never call providers or accept decisions.

Repository contract tooling, not a runtime policy gate, cache or skill dependency.
Only the three trusted repository schemas are read. Embedded references are inert.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 65_536
SCHEMAS = {}
for _kind in ('spec', 'request', 'receipt'):
    _schema = json.loads((ROOT / 'catalog/schema' / f'decision-{_kind}.v1.schema.json').read_text())
    Draft202012Validator.check_schema(_schema)
    SCHEMAS[_kind] = Draft202012Validator(_schema)


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate-json-key')
        value[key] = item
    return value


def _constant(_):
    raise ValueError('non-finite-json')


def decode(raw: bytes) -> Any:
    """Decode explicit bytes without fetching source references or printing content."""
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise ValueError('binding-input-limit')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique, parse_constant=_constant)
    except (UnicodeError, ValueError, RecursionError):
        raise ValueError('invalid-binding-json') from None


def _bounded_json(values):
    stack = [(values, 0)]
    nodes = 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if nodes > 8192 or depth > 32:
            raise ValueError('binding-structure-limit')
        if type(value) is dict:
            if any(type(key) is not str for key in value):
                raise ValueError('non-json-key')
            stack.extend((item, depth + 1) for item in value.values())
        elif type(value) is list:
            stack.extend((item, depth + 1) for item in value)
        elif type(value) not in (str, int, float, bool, type(None)):
            raise ValueError('non-json-value')
    if len(json.dumps(values, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')) > MAX_BYTES:
        raise ValueError('binding-input-limit')


def _same(left, right):
    return type(left) is type(right) and left == right


def inspect_binding(spec: Any, request: Any, receipt: Any) -> dict[str, Any]:
    """Check core cross-document identity and Boolean/choice domains, not truth."""
    errors: set[str] = set()
    review: set[str] = set()
    domain_checked = False
    status = None
    try:
        _bounded_json([spec, request, receipt])
        for role, value in (('spec', spec), ('request', request), ('receipt', receipt)):
            if not SCHEMAS[role].is_valid(value) or type(value.get('format_version')) is not int:
                errors.add(role + '-schema-invalid')
    except (TypeError, ValueError, UnicodeError, RecursionError, OverflowError):
        errors.add('invalid-or-oversized-input')
    if not errors:
        status = receipt['status']
        revisions = [spec['revision'], receipt['spec']['revision'],
                     *(q['spec_revision'] for q in request['questions'])]
        versions = [spec['input']['schema_version'], request['state']['schema_version'],
                    receipt['state']['schema_version']]
        if any(type(v) is not int for v in revisions) or any(type(v) not in (str, int) for v in versions):
            errors.add('non-exact-version-type')
        pair = (spec['id'], spec['revision'])
        questions = [(q['spec_id'], q['spec_revision']) for q in request['questions']]
        if len(set(questions)) != len(questions):
            errors.add('ambiguous-request-questions')
        if pair not in questions:
            errors.add('spec-not-requested')
        if receipt['spec']['id'] != spec['id'] or not _same(receipt['spec']['revision'], spec['revision']):
            errors.add('receipt-spec-mismatch')
        for key in ('schema_id', 'schema_version'):
            if not all(_same(spec['input'][key], state[key]) for state in (request['state'], receipt['state'])):
                errors.add('state-schema-mismatch')
        if receipt['state']['fingerprint'] != request['state']['fingerprint']:
            errors.add('state-fingerprint-mismatch')

        requirements = spec['evidence']['requirements']
        names = [item['id'] for item in requirements]
        if len(names) != len(set(names)):
            errors.add('duplicate-evidence-requirement')
        required_ids = {item['id'] for item in requirements if item['required']}
        coverage = receipt['uncertainty']['evidence_coverage']
        present, total = coverage['required_present'], coverage['required_total']
        if type(present) is not int or type(total) is not int:
            errors.add('non-exact-coverage-count')
        if total != len(required_ids):
            errors.add('required-total-spec-mismatch')
        if present > total:
            errors.add('required-present-exceeds-total')
        if not set(coverage['missing']).issubset(required_ids):
            errors.add('unknown-missing-requirement')
        if len(coverage['missing']) != total - present:
            errors.add('coverage-missing-count-mismatch')
        # Compute only bounded, coherent counts; enormous supplied integers are not evidence.
        if type(present) is int and type(total) is int and 0 <= present <= total == len(required_ids):
            expected = present / total if total else 1.0
            if not math.isclose(coverage['value'], expected, rel_tol=0, abs_tol=1e-9):
                errors.add('coverage-arithmetic-mismatch')
        if set(receipt['evidence']['used']) & set(receipt['evidence']['missing']):
            errors.add('evidence-both-used-and-missing')
        if coverage['missing'] or present != total or receipt['evidence']['missing']:
            review.add('missing-evidence-requires-review')
        if status != 'produced':
            review.add('non-produced-status')
        else:
            result = receipt['result']
            kind = spec['decision_kind']
            allowed = None
            if kind == 'boolean':
                domain_checked = True
                if type(result.get('value')) is not bool:
                    errors.add('boolean-result-required')
                allowed = {'false', 'true'}
            elif kind == 'choice':
                domain_checked = True
                allowed = set(spec['options'])
                if type(result.get('value')) is not str or result['value'] not in allowed:
                    errors.add('undeclared-choice-result')
            distribution = result.get('distribution')
            if distribution is not None:
                if not distribution:
                    errors.add('empty-result-distribution')
                elif not math.isclose(math.fsum(distribution.values()), 1, rel_tol=0, abs_tol=1e-6):
                    errors.add('distribution-arithmetic-mismatch')
                if allowed is not None and not set(distribution).issubset(allowed):
                    errors.add('undeclared-distribution-option')
    return {
        'kind': 'decision-binding-inspection', 'consistent': not errors,
        'errors': sorted(errors), 'review_reasons': sorted(review),
        'recorded_status': status, 'result_domain_checked': domain_checked,
        'scope': 'supplied-core-identity-and-finite-results',
        'not_checked': ['request-occurrence', 'state-payload-fingerprint', 'source-content-and-age',
                        'evidence-requirement-mapping', 'provider-execution-and-calibration',
                        'policy-disposition', 'other-result-primitives-and-extensions'],
        'claims_authenticated': False, 'current_evidence_verified': False,
        'cache_reuse_authorized': False, 'decision_accepted': False,
        'consequence_authorized': False, 'provider_calls': 0, 'model_tokens': None,
    }
