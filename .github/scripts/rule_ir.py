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


def _compile_inventory(value: Any) -> dict:
    """Build a bounded-input review view before applying a caller output budget."""
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
    return result


def compile_inventory(value: Any, *, budget_bytes: int = DEFAULT_BUDGET) -> dict:
    """Combine declared exact duplicates; expose conflicts without resolving them.

    Raises fixed-code RuleError on malformed/ambiguous input, never a partial plan.
    The output is a generated review view, not authenticated or executable policy.
    """
    if type(budget_bytes) is not int or not 1 <= budget_bytes <= MAX_BYTES:
        raise RuleError('invalid-output-budget')
    result = _compile_inventory(value)
    output_bytes = len(encoded(result))
    if output_bytes > budget_bytes:
        # Never prune mandatory rules, occurrences, exceptions or conflicting rules.
        return {'format_version': 1, 'kind': 'compiled-rule-ir', 'authority': 'navigation-only',
                'status': 'budget-exceeded', 'rules': [], 'conflicts': [],
                'required_output_bytes': output_bytes, 'budget_bytes': budget_bytes,
                'conflicts_detected': len(result['conflicts']), 'complete_payload_emitted': False,
                'next_step': 'Review the selected task scope or raise the budget; do not drop applicable rules.'}
    return result


# These bounds apply to bytes the caller has already acquired. The API never
# interprets a reference as a path, URL or permission to acquire more material.
MAX_SOURCE_COUNT = 128
MAX_SOURCE_BYTES = 1_048_576
MAX_TOTAL_SOURCE_BYTES = 4_194_304


def _source_context(reference: str, digest: str, lines: list[bytes],
                    final_newline: bool, occurrences: list[dict]) -> dict:
    """Retain the complement of verified rule ranges, not inferred rule meaning."""
    cursor = 1
    gaps = []
    for start, end in sorted((r['source']['start_line'], r['source']['end_line'])
                             for r in occurrences):
        if cursor < start:
            gaps.append((cursor, start - 1))
        cursor = max(cursor, end + 1)
    if cursor <= len(lines):
        gaps.append((cursor, len(lines)))

    spans = []
    retained_lines = 0
    for start, end in gaps:
        raw = b'\n'.join(lines[start - 1:end])
        if end < len(lines) or final_newline:
            raw += b'\n'
        spans.append({'start_line': start, 'end_line': end, 'text': raw.decode('utf-8')})
        retained_lines += end - start + 1
    return {'reference': reference, 'sha256': digest,
            'rule_covered_lines': len(lines) - retained_lines,
            'retained_context_lines': retained_lines, 'spans': spans}


def _bind_sources(value: dict, sources: Any, *,
                  context_records: list[dict] | None = None) -> dict:
    if type(sources) is not dict:
        raise RuleError('invalid-source-map')
    if len(sources) > MAX_SOURCE_COUNT:
        raise RuleError('source-count-limit')
    if any(type(key) is not str for key in sources):
        raise RuleError('invalid-source-reference')
    selected = dict(sources)
    by_reference: dict[str, list[dict]] = {}
    for rule in value['rules']:
        by_reference.setdefault(rule['source']['reference'], []).append(rule)
    if set(selected) != set(by_reference):
        raise RuleError('source-set-mismatch')

    # Validate the entire map before hashing or decoding any selected contents.
    total_bytes = 0
    for raw in selected.values():
        if type(raw) is not bytes:
            raise RuleError('source-bytes-required')
        if len(raw) > MAX_SOURCE_BYTES:
            raise RuleError('source-size-limit')
        total_bytes += len(raw)
        if total_bytes > MAX_TOTAL_SOURCE_BYTES:
            raise RuleError('source-total-size-limit')
    for occurrences in by_reference.values():
        if len({item['source']['sha256'] for item in occurrences}) != 1:
            raise RuleError('conflicting-source-versions')

    identities = []
    for reference, occurrences in sorted(by_reference.items()):
        raw = selected[reference]
        actual_digest = _digest(raw)
        if actual_digest != occurrences[0]['source']['sha256']:
            raise RuleError('source-digest-mismatch')
        try:
            text = raw.decode('utf-8')
        except UnicodeError:
            raise RuleError('source-not-utf8-text') from None
        if any(ord(char) < 32 and char not in '\t\r\n' or 127 <= ord(char) <= 159 for char in text):
            raise RuleError('source-not-utf8-text')

        # Only LF delimits lines, exactly as in RuleInventory v1. Keep CRLF,
        # Unicode separators and the final-newline distinction byte-exact.
        lines = raw.split(b'\n') if raw else []
        final_newline = raw.endswith(b'\n')
        if final_newline:
            lines.pop()
        for rule in occurrences:
            start = rule['source']['start_line']
            end = rule['source']['end_line']
            if end > len(lines):
                raise RuleError('source-range-unavailable')
            excerpt = b'\n'.join(lines[start - 1:end])
            if end < len(lines) or final_newline:
                excerpt += b'\n'
            if excerpt != rule['statement'].encode('utf-8'):
                raise RuleError('source-statement-mismatch')
        if context_records is not None:
            context_records.append(_source_context(reference, actual_digest, lines,
                                                   final_newline, occurrences))
        identities.append({'reference': reference, 'sha256': actual_digest,
                           'bytes': len(raw), 'lines': len(lines)})

    return {'matched': True, 'scope': 'supplied-byte-map-only',
            'inventory_sha256': _digest(encoded(value)),
            'sources': identities, 'occurrences_checked': len(value['rules']),
            'source_bytes_checked': total_bytes,
            'acquisition_authenticated': False, 'current_at_use_verified': False,
            'inventory_complete': None, 'authority_authenticated': False}


def compile_with_sources(value: Any, *, target: str, sources: dict[str, bytes],
                         budget_bytes: int = DEFAULT_BUDGET,
                         preserve_source_context: bool = False) -> dict:
    """Bind a review plan to an exact, caller-supplied full-source byte map.

    This optional repository API does not acquire files, authenticate their origin,
    establish freshness, find omitted rules or upgrade the declared authority.
    A matching source map is not approval, a Jev cache hit or project verification.
    The nested Rule IR v1 is unchanged; binding evidence belongs to this report.
    Opting into preserve_source_context returns all surrounding supplied text too;
    review the full source disclosure for the destination before enabling it.
    Coverage of supplied lines is not semantic completeness or source discovery.
    All inputs must remain quiescent during the call. Fixed-code RuleError rejects
    mismatches without returning source text, references or a partially bound plan.
    """
    if type(budget_bytes) is not int or not 1 <= budget_bytes <= MAX_BYTES:
        raise RuleError('invalid-output-budget')
    if type(preserve_source_context) is not bool:
        raise RuleError('invalid-source-context-mode')
    plan = _compile_inventory(value)
    if type(target) is not str or target != value['target']:
        raise RuleError('source-target-mismatch')
    context_records = [] if preserve_source_context else None
    binding = _bind_sources(value, sources, context_records=context_records)
    result = {'format_version': 1, 'kind': 'rule-source-review',
              'authority': 'navigation-only', 'target': target, 'status': plan['status'],
              'source_binding': binding, 'plan': plan, 'complete_payload_emitted': True}
    if preserve_source_context:
        result['source_context'] = {
            'scope': 'supplied-sources-only', 'all_supplied_lines_represented': True,
            'sources': context_records}
    output_bytes = len(encoded(result))
    if output_bytes > budget_bytes:
        # This small diagnostic can itself exceed a very small requested budget;
        # the budget governs the complete review payload, never evidence clipping.
        deferred = {'format_version': 1, 'kind': 'rule-source-review',
                'authority': 'navigation-only', 'status': 'budget-exceeded',
                'source_binding': None, 'plan': None, 'complete_payload_emitted': False,
                'required_output_bytes': output_bytes, 'budget_bytes': budget_bytes,
                'conflicts_detected': len(plan['conflicts']),
                'next_step': 'Review the selected task scope or raise the budget; do not drop applicable rules.'}
        if preserve_source_context:
            deferred['source_context'] = None
        return deferred
    return result
