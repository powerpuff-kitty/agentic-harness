"""Validate supplied continuation records, not their truth or current source state.

Repository contract tooling only. No reference resolution, model execution, cache
restoration or action authorization. Runtime consumers must separately check facts.
"""
from __future__ import annotations

from datetime import datetime
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 65_536
SCHEMA = json.loads((ROOT / 'catalog/schema/context-checkpoint.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate-json-key')
        result[key] = value
    return result


def _constant(value):
    raise ValueError('non-finite-json')


def decode(raw: bytes) -> Any:
    """Decode caller-supplied bytes; embedded references are never opened."""
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('checkpoint-size-limit')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique,
                          parse_constant=_constant)
    except (UnicodeError, ValueError, RecursionError):
        raise ValueError('invalid-checkpoint-json') from None


def inspect(value: Any) -> dict[str, Any]:
    """Check field consistency without trusting declared observations/approvals."""
    errors: set[str] = set()
    try:
        raw = json.dumps(value, ensure_ascii=True, separators=(',', ':'),
                         allow_nan=False).encode('utf-8')
        if len(raw) > MAX_BYTES:
            errors.add('checkpoint-size-limit')
        if not VALIDATOR.is_valid(value):
            errors.add('schema-invalid')
        if isinstance(value, dict) and type(value.get('format_version')) is not int:
            errors.add('schema-invalid')
    except (TypeError, ValueError, UnicodeError, RecursionError):
        errors.add('invalid-checkpoint-value')
    if not errors:
        stamp = value['created_at']
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})', stamp):
            errors.add('invalid-recorded-time')
        else:
            try:
                datetime.fromisoformat(stamp.replace('Z', '+00:00'))
            except ValueError:
                errors.add('invalid-recorded-time')
        for section in ('sources', 'notes', 'checks', 'open_items'):
            identities = [item['id'] for item in value[section]]
            if len(identities) != len(set(identities)):
                errors.add('duplicate-id:' + section)
        sources = {item['id']: item for item in value['sources']}

        def references(names, *, recorded=False, role=None):
            for name in names:
                source = sources.get(name)
                if source is None:
                    errors.add('unknown-source-reference')
                elif recorded and source['availability'] != 'recorded':
                    errors.add('unavailable-supporting-source')
                elif role is not None and source['role'] != role:
                    errors.add('incorrect-source-role')

        for note in value['notes']:
            references(note['source_ids'], recorded=True)
            if note['kind'] == 'decision-reference' and not any(
                sources.get(name, {}).get('role') == 'decision' for name in note['source_ids']
            ):
                errors.add('decision-source-required')
        attempts: dict[str, list[dict]] = {}
        for check in value['checks']:
            attempts.setdefault(check['name'], []).append(check)
            if type(check['attempt']) is not int:
                errors.add('invalid-attempt-number')
            executed = check['status'] in ('passed', 'failed')
            references(check['input_source_ids'], recorded=executed)
            references(check['evidence_source_ids'], recorded=executed, role='diagnostic')
            if executed and (check['command'] is None or not check['input_source_ids']
                             or not check['evidence_source_ids']):
                errors.add('executed-check-provenance-required')
            if check['status'] in ('not-run', 'blocked') and check['evidence_source_ids']:
                errors.add('unexecuted-check-has-execution-evidence')
        for group in attempts.values():
            sequence = sorted(check['attempt'] for check in group)
            if sequence != list(range(1, len(group) + 1)):
                errors.add('incomplete-or-duplicate-attempt-history')
            if len({check['command'] for check in group if check['command'] is not None}) > 1:
                errors.add('check-command-changed-within-history')
        for item in value['open_items']:
            references(item['source_ids'])
        if any(item['blocking'] for item in value['open_items']):
            if value['task']['status'] != 'blocked':
                errors.add('blocking-item-status-mismatch')
    return {
        'kind': 'context-checkpoint-inspection',
        'consistent': not errors, 'errors': sorted(errors),
        'scope': 'supplied-record-consistency',
        'source_freshness_verified': False, 'claims_authenticated': False,
        'checks_executed': False, 'approval_transferred': False,
        'model_execution': 'not-performed', 'token_savings_verified': False,
    }
