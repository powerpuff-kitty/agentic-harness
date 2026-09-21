#!/usr/bin/env python3
"""Review caller-resolved Rule IR applicability without interpreting source selectors."""
from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from jsonschema import Draft202012Validator

import rule_ir

ROOT = Path(__file__).resolve().parents[2]
MAX_MAP_BYTES = 262_144
MAX_TARGET_REFS = 4096
DEFAULT_BUDGET = 65_536
MAP_SCHEMA = json.loads((ROOT / "catalog/schema/rule-applicability-map.v1.schema.json").read_text())
Draft202012Validator.check_schema(MAP_SCHEMA)
MAP_VALIDATOR = Draft202012Validator(MAP_SCHEMA)
OPPOSED = {("forbid", "require"), ("require", "forbid"),
           ("forbid", "allow"), ("allow", "forbid")}


class ApplicabilityError(ValueError):
    """Fixed diagnostics never echo rule statements or resolved target names."""


def _encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def _digest(value):
    raw = value if isinstance(value, bytes) else _encoded(value)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _normalized_text(value):
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def _similarity(left, right):
    a, b = _normalized_text(left), _normalized_text(right)
    if not a or not b:
        return 0.0
    return round(difflib.SequenceMatcher(None, a, b, autojunk=False).ratio(), 6)


def _validate_inventory(value):
    # Use the existing public compiler as the accepted inventory validator. A
    # budget-deferred result is sufficient here; its payload is not consumed.
    rule_ir.compile_inventory(value, budget_bytes=rule_ir.MAX_BYTES)


def _validate_map(inventory, resolution):
    if type(resolution) is not dict:
        raise ApplicabilityError("invalid-applicability-map")
    try:
        raw = _encoded(resolution)
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise ApplicabilityError("invalid-applicability-map") from None
    if len(raw) > MAX_MAP_BYTES or not MAP_VALIDATOR.is_valid(resolution):
        raise ApplicabilityError("invalid-applicability-map")
    if resolution["target"] != inventory["target"]:
        raise ApplicabilityError("applicability-target-mismatch")
    expected = {rule["id"] for rule in inventory["rules"]}
    rows = resolution["rules"]
    ids = [row["rule_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ApplicabilityError("duplicate-applicability-rule-id")
    if set(ids) != expected:
        raise ApplicabilityError("applicability-rule-set-mismatch")
    refs = sum(len(row["targets"]) for row in rows)
    if refs > MAX_TARGET_REFS:
        raise ApplicabilityError("applicability-target-limit")
    return raw


def review_applicability(inventory, resolution, *, target=None,
                         similarity_threshold=0.88,
                         budget_bytes=DEFAULT_BUDGET):
    """Review exact caller-resolved target overlap and lexical near-duplicates.

    No source selector, path, rule reference, file, network resource or provider is
    resolved here. The caller owns target-membership semantics and completeness.
    Near-duplicate scores are review candidates only and never automatic equivalence.
    """
    if type(similarity_threshold) not in (int, float) or isinstance(similarity_threshold, bool):
        raise ApplicabilityError("invalid-similarity-threshold")
    if not 0.5 <= float(similarity_threshold) <= 1:
        raise ApplicabilityError("invalid-similarity-threshold")
    if type(budget_bytes) is not int or not 1 <= budget_bytes <= MAX_MAP_BYTES:
        raise ApplicabilityError("invalid-output-budget")
    if target is not None and (type(target) is not str or not target):
        raise ApplicabilityError("invalid-selected-target")

    _validate_inventory(inventory)
    resolution_raw = _validate_map(inventory, resolution)
    by_rule = {row["rule_id"]: set(row["targets"]) for row in resolution["rules"]}
    rules = {rule["id"]: rule for rule in inventory["rules"]}
    ids = sorted(rules)

    applicable = sorted(rule_id for rule_id in ids
                        if target is not None and target in by_rule[rule_id])
    overlaps = []
    lexical = []
    for index, left_id in enumerate(ids):
        left = rules[left_id]
        for right_id in ids[index + 1:]:
            right = rules[right_id]
            shared = sorted(by_rule[left_id] & by_rule[right_id])
            if not shared:
                continue
            score = _similarity(left["statement"], right["statement"])
            same_conditions = (sorted(left["conditions"]) == sorted(right["conditions"])
                               and sorted(left["exceptions"]) == sorted(right["exceptions"]))
            same_key = left["key"] == right["key"]
            opposed = (left["directive"], right["directive"]) in OPPOSED
            same_directive = left["directive"] == right["directive"]
            if same_key and opposed and same_conditions:
                review = "declared-overlap-conflict"
            elif same_key and same_directive and same_conditions and score >= similarity_threshold:
                review = "possible-equivalence"
            else:
                review = "scope-overlap-review"
            overlaps.append({
                "rule_ids": [left_id, right_id],
                "shared_targets": shared,
                "same_key": same_key,
                "same_conditions_and_exceptions": same_conditions,
                "directive_relation": "opposed" if opposed else
                                      ("same" if same_directive else "different"),
                "lexical_similarity": score,
                "review": review,
            })
            if score >= similarity_threshold and not (same_key and same_directive and same_conditions):
                lexical.append({
                    "rule_ids": [left_id, right_id],
                    "shared_targets": shared,
                    "lexical_similarity": score,
                    "relation": "similar-text-different-context",
                    "resolution": "review-required",
                })

    conflict_count = sum(item["review"] == "declared-overlap-conflict" for item in overlaps)
    equivalence_count = sum(item["review"] == "possible-equivalence" for item in overlaps)
    result = {
        "format_version": 1,
        "kind": "rule-applicability-review",
        "authority": "navigation-only",
        "target": inventory["target"],
        "selected_target": target,
        "applicability_map_sha256": _digest(resolution_raw),
        "applicable_rule_ids": applicable,
        "overlaps": overlaps,
        "lexical_review_candidates": lexical,
        "summary": {
            "resolved_rules": len(ids),
            "resolved_target_references": sum(len(by_rule[item]) for item in ids),
            "overlapping_pairs": len(overlaps),
            "declared_overlap_conflicts": conflict_count,
            "possible_equivalences": equivalence_count,
        },
        "limits": {
            "selector_semantics_inferred": False,
            "source_inventory_complete": None,
            "target_membership_authenticated": False,
            "semantic_equivalence_verified": False,
            "natural_language_conflicts_resolved": False,
            "automatic_merge": False,
            "canonical_sources_modified": False,
            "authority_authenticated": False,
            "provider_calls": 0,
            "model_tokens": None,
        },
        "not_checked": [
            "source-discovery-and-inventory-completeness",
            "selector-expansion-correctness",
            "condition-co-satisfiability",
            "semantic-equivalence",
            "natural-language-contradictions",
            "host-loading-and-precedence",
        ],
    }
    output_bytes = len(_encoded(result))
    if output_bytes > budget_bytes:
        return {
            "format_version": 1,
            "kind": "rule-applicability-review",
            "authority": "navigation-only",
            "status": "budget-exceeded",
            "complete_payload_emitted": False,
            "required_output_bytes": output_bytes,
            "budget_bytes": budget_bytes,
            "overlaps_detected": len(overlaps),
            "declared_overlap_conflicts": conflict_count,
            "possible_equivalences": equivalence_count,
            "next_step": "Narrow the reviewed target set or raise the budget; do not discard overlapping rules.",
        }
    result["status"] = "review-required" if overlaps else "resolved-map-reviewed"
    result["complete_payload_emitted"] = True
    return result
