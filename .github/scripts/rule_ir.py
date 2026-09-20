"""Compile a supplied rule inventory into a provenance-preserving review view.

Canonical repository tooling only. No rule discovery, selector evaluation, file
resolution, policy override, model call, automatic prompt injection or source edit.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 262_144
DEFAULT_BUDGET = 65_536
MAX_NODES = 32_768
AUTHORITY = ('policy', 'project-truth', 'adr', 'pack', 'skill', 'prompt')
SCHEMA = json.loads((ROOT / 'catalog/schema/rule-inventory.v1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


class RuleError(ValueError):
    """Fixed diagnostics exclude rejected rule text and references."""


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RuleError('duplicate-json-key')
        result[key] = value
    return result


def _constant(_):
    raise RuleError('nonfinite-json')


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('utf-8')


def _bounded(value: Any) -> bytes:
    stack = [(value, 0)]
    visited = text_bytes = 0
    while stack:
        item, depth = stack.pop()
        visited += 1
        if visited > MAX_NODES or depth > 32:
            raise RuleError('inventory-structure-limit')
        if type(item) in (dict, list):
            if len(item) > MAX_NODES:
                raise RuleError('inventory-structure-limit')
            if type(item) is dict:
                if any(type(key) is not str for key in item):
                    raise RuleError('non-json-value')
                values = list(item.keys()) + list(item.values())
            else:
                values = item
            stack.extend((child, depth + 1) for child in values)
        elif type(item) is str:
            text_bytes += len(item.encode('utf-8'))
            if text_bytes > MAX_BYTES:
                raise RuleError('inventory-size-limit')
        elif type(item) not in (int, float, bool, type(None)):
            raise RuleError('non-json-value')
    raw = encoded(value)
    if len(raw) > MAX_BYTES:
        raise RuleError('inventory-size-limit')
    return raw


def decode(raw: bytes) -> Any:
    """Parse explicitly supplied bytes; references in the record remain inert."""
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise RuleError('inventory-size-limit')
    try:
        result = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique,
                            parse_constant=_constant)
        _bounded(result)
        return result
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
        raise RuleError('invalid-inventory-json') from None


def _normalized(rule: dict) -> dict:
    # Set order is immaterial only where the accepted inventory contract says so.
    # Text, key, authority, base and conditions are otherwise never rewritten.
    return {key: (sorted(rule[key]) if key in ('conditions', 'exceptions') else
                  {'base': rule[key]['base'], 'include': sorted(rule[key]['include']),
                   'exclude': sorted(rule[key]['exclude'])} if key == 'scope' else rule[key])
            for key in ('key', 'statement', 'authority', 'strength', 'directive',
                        'scope', 'conditions', 'exceptions')}


def _digest(raw: bytes) -> str:
    return 'sha256:' + hashlib.sha256(raw).hexdigest()


def compile_inventory(value: Any, *, budget_bytes: int = DEFAULT_BUDGET) -> dict:
    """Combine declared exact duplicates; expose conflicts without resolving them.

    Raises fixed-code RuleError on malformed/ambiguous input, never a partial plan.
    The output is a generated review view, not authenticated or executable policy.
    """
    if type(budget_bytes) is not int or not 1 <= budget_bytes <= MAX_BYTES:
        raise RuleError('invalid-output-budget')
    try:
        raw = _bounded(value)
        if not VALIDATOR.is_valid(value) or type(value.get('format_version')) is not int:
            raise RuleError('inventory-schema-invalid')
    except (TypeError, UnicodeError, RecursionError, OverflowError):
        raise RuleError('invalid-inventory-value') from None
    except ValueError as error:
        if isinstance(error, RuleError):
            raise
        raise RuleError('invalid-inventory-value') from None

    ids = set()
    locations: dict[bytes, str] = {}
    groups: dict[bytes, dict] = {}
    for rule in value['rules']:
        if rule['id'] in ids:
            raise RuleError('duplicate-rule-id')
        ids.add(rule['id'])
        source = rule['source']
        if (type(source['start_line']) is not int or type(source['end_line']) is not int
                or source['start_line'] > source['end_line']):
            raise RuleError('invalid-source-range')
        line_count = rule['statement'].count('\n') + int(not rule['statement'].endswith('\n'))
        if line_count != source['end_line'] - source['start_line'] + 1:
            raise RuleError('source-range-text-line-count-mismatch')
        location = encoded(source)
        if location in locations and locations[location] != rule['statement']:
            raise RuleError('same-source-range-has-different-text')
        locations[location] = rule['statement']
        content = _normalized(rule)
        signature = encoded({'target': value['target'], **content})
        if signature not in groups:
            groups[signature] = {'id': _digest(signature), **content,
                                 'authority_rank': AUTHORITY.index(rule['authority']),
                                 'occurrences': []}
        groups[signature]['occurrences'].append({'id': rule['id'], 'source': dict(source)})

    compiled = sorted(groups.values(), key=lambda r: (r['authority_rank'], r['key'], r['id']))
    contexts: dict[bytes, list[dict]] = {}
    for rule in compiled:
        rule['occurrences'].sort(key=lambda occurrence: occurrence['id'])
        context = encoded({'target': value['target'], **{key: rule[key] for key in
                            ('key', 'scope', 'conditions', 'exceptions')}})
        contexts.setdefault(context, []).append(rule)
    conflicts = []
    for context, rules in sorted(contexts.items()):
        directions = {r['directive'] for r in rules}
        if 'forbid' in directions and directions & {'require', 'allow'}:
            conflicts.append({'context_id': _digest(context),
                              'rule_ids': sorted(r['id'] for r in rules),
                              'reason': 'opposed-declared-directives',
                              'resolution': 'review-required'})

    result = {
        'format_version': 1, 'kind': 'compiled-rule-ir', 'authority': 'navigation-only',
        'target': value['target'],
        'status': 'review-required' if conflicts else 'compiled',
        'rules': compiled, 'conflicts': conflicts,
        'measurement': {'unit': 'utf8-bytes', 'normalized_input_bytes': len(raw),
                        'input_rules': len(value['rules']), 'compiled_rules': len(compiled),
                        'duplicate_presentations_avoided': len(value['rules']) - len(compiled),
                        'statement_bytes_before': sum(len(r['statement'].encode('utf-8')) for r in value['rules']),
                        'statement_bytes_after': sum(len(r['statement'].encode('utf-8')) for r in compiled)},
        'limits': {'source_bytes_verified': False, 'inventory_complete': None,
                   'semantic_equivalence_verified': False, 'scope_overlap_checked': False,
                   'authority_authenticated': False, 'automatic_injection': False,
                   'canonical_sources_modified': False, 'conflicts_resolved': False,
                   'checks_verified': False, 'provider_calls': 0, 'model_tokens': None},
        'not_checked': ['source-extraction-and-completeness', 'undeclared-context-and-exceptions',
                        'nonidentical-selector-overlap', 'natural-language-contradictions',
                        'host-precedence-and-loading'],
    }
    output_bytes = len(encoded(result))
    if output_bytes > budget_bytes:
        # Never prune mandatory rules, occurrences, exceptions or conflicting rules.
        return {'format_version': 1, 'kind': 'compiled-rule-ir', 'authority': 'navigation-only',
                'status': 'budget-exceeded', 'rules': [], 'conflicts': [],
                'required_output_bytes': output_bytes, 'budget_bytes': budget_bytes,
                'conflicts_detected': len(conflicts), 'complete_payload_emitted': False,
                'next_step': 'Review the selected task scope or raise the budget; do not drop applicable rules.'}
    return result
