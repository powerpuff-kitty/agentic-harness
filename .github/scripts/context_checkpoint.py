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
            if check['status'] in ('not-run', 'blocked') and (check['evidence_source_ids']
                    or check['output_complete'] is not None):
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


def plan_refresh(previous: Any, current: Any, *, current_source_ids: list[str]) -> dict[str, Any]:
    """Compare declared dependencies; never fetch source, restore notes or accept checks.

    Select current versions explicitly when the newer checkpoint retains historical
    versions. References and roles match exactly; IDs alone never identify content.
    The result describes supplied records, not authenticated/current filesystem state.
    """
    for role, record in (('previous', previous), ('current', current)):
        if not inspect(record)['consistent']:
            raise ValueError('inconsistent-' + role + '-checkpoint')
    if datetime.fromisoformat(current['created_at'].replace('Z', '+00:00')) < datetime.fromisoformat(
        previous['created_at'].replace('Z', '+00:00')
    ):
        raise ValueError('current-checkpoint-predates-previous')
    if (not isinstance(current_source_ids, list) or not 1 <= len(current_source_ids) <= 256
            or any(not isinstance(name, str) for name in current_source_ids)
            or len(set(current_source_ids)) != len(current_source_ids)):
        raise ValueError('invalid-current-source-selection')
    old = {item['id']: item for item in previous['sources']}
    new = {item['id']: item for item in current['sources']}
    if any(name not in new for name in current_source_ids):
        raise ValueError('unknown-current-source-id')

    def key(source):
        return source['reference'], source['role']

    selected = {}
    for name in sorted(current_source_ids):
        item = new[name]
        if key(item) in selected:
            raise ValueError('ambiguous-current-source-version')
        selected[key(item)] = item
    old_keys = {key(item) for item in old.values()}
    added = sorted(item['id'] for k, item in selected.items() if k not in old_keys)
    source_rows, states = [], {}
    for name, item in sorted(old.items()):
        chosen = selected.get(key(item))
        if chosen is None:
            state = 'not-selected'
        elif item['availability'] != 'recorded':
            state = 'previously-unavailable'
        elif chosen['availability'] != 'recorded':
            state = 'currently-unavailable'
        elif item['sha256'] != chosen['sha256']:
            state = 'changed-recorded-bytes'
        else:
            state = 'matching-recorded-bytes'
        states[name] = state
        source_rows.append({'previous_id': name, 'current_id': chosen['id'] if chosen else None,
                            'state': state})

    scope_changes = [name for name in ('id', 'goal', 'scope', 'base_revision')
                     if previous['task'][name] != current['task'][name]]
    global_reasons = ['task-' + name + '-changed' for name in scope_changes]
    if previous['task']['base_revision'] is None or current['task']['base_revision'] is None:
        global_reasons.append('unknown-base-revision')
    context_roles = {'instruction', 'criterion'}
    if any(item['role'] in context_roles and states[name] != 'matching-recorded-bytes'
           for name, item in old.items()):
        global_reasons.append('recorded-context-changed-or-unavailable')
    if any(selected[k]['role'] in context_roles for k in selected if k not in old_keys):
        global_reasons.append('new-selected-context')
    unselected_context = sorted(item['id'] for item in new.values()
                                if item['role'] in context_roles and key(item) not in selected)
    if unselected_context:
        global_reasons.append('current-context-not-selected')

    def check_identity(check, inventory):
        def inputs(field):
            return sorted((inventory[name]['reference'], inventory[name]['role'],
                           inventory[name]['availability'], inventory[name]['sha256'])
                          for name in check[field])
        return ([check[name] for name in ('name', 'attempt', 'command', 'status', 'output_complete')],
                inputs('input_source_ids'), inputs('evidence_source_ids'))

    # Keep attempts from the older record visible even if the newer record drops them.
    current_checks = {item['id']: item for item in current['checks']}
    missing_checks, changed_checks = [], []
    for check in previous['checks']:
        newer = current_checks.get(check['id'])
        if newer is None:
            missing_checks.append(check['id'])
        elif check_identity(check, old) != check_identity(newer, new):
            changed_checks.append(check['id'])
    if missing_checks or changed_checks:
        global_reasons.append('historical-check-records-diverged')
    global_reasons.sort()

    def dependency_row(item, names):
        affected = sorted({name for name in names if states[name] != 'matching-recorded-bytes'})
        state = ('review-required' if global_reasons or affected else
                 'matching-recorded-inputs' if names else 'no-recorded-inputs')
        return {'id': item['id'], 'dependency_state': state, 'affected_source_ids': affected}

    notes = [dependency_row(note, note['source_ids'])
             for note in sorted(previous['notes'], key=lambda item: item['id'])]
    checks = []
    for check in sorted(previous['checks'], key=lambda item: (item['name'], item['attempt'])):
        row = dependency_row(check, check['input_source_ids'] + check['evidence_source_ids'])
        row.update(name=check['name'], attempt=check['attempt'], historical_status=check['status'],
                   historical_output_complete=check['output_complete'])
        checks.append(row)
    open_items = []
    for item in sorted(previous['open_items'], key=lambda item: item['id']):
        row = dependency_row(item, item['source_ids'])
        row['blocking'] = item['blocking']
        open_items.append(row)
    needs_review = bool(global_reasons or added or
                        any(state != 'matching-recorded-bytes' for state in states.values()))
    return {
        'kind': 'context-checkpoint-refresh-plan', 'scope': 'supplied-record-dependencies',
        'dependency_state': 'review-required' if needs_review else 'matching-recorded-inputs',
        'global_review_reasons': global_reasons, 'sources': source_rows,
        'new_selected_source_ids': added, 'unselected_context_source_ids': unselected_context,
        'unselected_current_source_count': len(new) - len(current_source_ids),
        'selection_review_required': bool(added),
        'history': {'missing_check_ids': sorted(missing_checks),
                    'changed_check_ids': sorted(changed_checks)},
        'notes': notes, 'checks': checks, 'open_items': open_items,
        'limits': {'same_target_authenticated': False, 'source_freshness_verified': False,
                   'claims_authenticated': False, 'semantic_completeness_verified': False,
                   'unselected_dependencies_checked': False, 'retained_model_context_verified': False,
                   'checks_executed': False, 'check_success_verified': False,
                   'approval_transferred': False, 'automatic_reuse_authorized': False,
                   'blocking_items_resolved': False, 'provider_calls': 0, 'model_tokens': None},
    }
