#!/usr/bin/env python3
"""Validate supplied context-memory records; never read referenced sources or authorize reuse."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 65_536
LEVELS = {"repository": 0, "package": 1, "module": 2, "file": 3, "symbol": 4}

def _schema(name):
    value = json.loads((ROOT / "catalog/schema" / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(value)
    return Draft202012Validator(value, format_checker=FormatChecker())

SUMMARY = _schema("context-summary.v1.schema.json")
CACHE = _schema("context-cache-entry.v1.schema.json")
EVENT = _schema("context-event.v1.schema.json")

class ContextMemoryError(ValueError):
    pass

def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _sha(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()

def _validate_size(value):
    if len(_canonical(value)) > MAX_BYTES:
        raise ContextMemoryError("record-size-limit-exceeded")

def inspect_summary(value):
    _validate_size(value)
    errors = sorted(error.message for error in SUMMARY.iter_errors(value))
    if errors:
        return {"valid": False, "errors": errors, "authority": None, "summary_identity_matches": False}
    ids = [item["id"] for item in value["sources"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate-source-id")
    rank = LEVELS[value["scope"]["level"]]
    ancestry = value["scope"]["ancestry"]
    ranks = [LEVELS[item["level"]] for item in ancestry]
    if any(item >= rank for item in ranks) or ranks != sorted(set(ranks)):
        errors.append("invalid-scope-ancestry")
    if rank == 0 and ancestry:
        errors.append("repository-summary-has-ancestry")
    if rank > 0 and (not ancestry or ranks[0] != 0):
        errors.append("nonrepository-summary-missing-repository-ancestor")
    if value["coverage"]["status"] == "complete" and (value["coverage"]["missing"] or value["coverage"]["not_checked"]):
        errors.append("complete-summary-has-gaps")
    if value["coverage"]["status"] != "complete" and not (value["coverage"]["missing"] or value["coverage"]["not_checked"]):
        errors.append("incomplete-summary-without-explicit-gap")
    if value["coverage"]["status"] == "complete" and any(item["required"] is False for item in value["sources"]):
        # Optional inputs are allowed, but completeness cannot be inferred from them alone.
        pass
    match = value["summary_sha256"] == _sha(value["summary"].encode("utf-8"))
    if not match:
        errors.append("summary-identity-mismatch")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "authority": value["authority"],
        "summary_identity_matches": match,
        "canonical_truth": False,
        "source_authenticity_verified": False,
        "model_behaviour_verified": False,
    }

def cache_identity(value):
    identity = {
        "artifact_type": value["artifact_type"],
        "repository": value["repository"],
        "producer": value["producer"],
        "inputs": sorted(value["inputs"], key=lambda item: item["id"]),
    }
    return _sha(_canonical(identity))

def inspect_cache(value, current=None):
    _validate_size(value)
    errors = sorted(error.message for error in CACHE.iter_errors(value))
    if errors:
        return {"valid": False, "errors": errors, "identity_matches": False, "status": "invalid", "reuse_authorized": False}
    ids = [item["id"] for item in value["inputs"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate-input-id")
    identity_matches = value["identity_sha256"] == cache_identity(value)
    if not identity_matches:
        errors.append("cache-identity-mismatch")
    status = "recorded-only"
    changed, missing, extra = [], [], []
    if current is not None:
        if not isinstance(current, dict) or set(current) != {"repository", "inputs"}:
            raise ContextMemoryError("invalid-current-input-view")
        if current["repository"] != value["repository"]:
            changed.append("repository")
        old = {item["id"]: item for item in value["inputs"]}
        new = {item["id"]: item for item in current["inputs"]}
        if len(new) != len(current["inputs"]):
            raise ContextMemoryError("duplicate-current-input-id")
        missing = sorted(set(old) - set(new))
        extra = sorted(set(new) - set(old))
        for key in sorted(set(old) & set(new)):
            if old[key] != new[key]:
                changed.append(key)
        status = "matching-recorded-inputs" if not (changed or missing or extra) else "stale-or-different-inputs"
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "identity_matches": identity_matches,
        "status": status,
        "changed": changed,
        "missing": missing,
        "extra": extra,
        "reuse_authorized": False,
        "provider_call_authorized": False,
        "result_authenticity_verified": False,
    }

def inspect_events(values):
    if not isinstance(values, list) or not values:
        raise ContextMemoryError("nonempty-event-list-required")
    if len(values) > 4096:
        raise ContextMemoryError("event-count-limit-exceeded")
    errors = []
    ids, sequences = [], []
    previous_time = None
    previous_sequence = None
    for index, value in enumerate(values):
        _validate_size(value)
        shape = sorted(error.message for error in EVENT.iter_errors(value))
        if shape:
            errors.extend(f"event-{index}:{message}" for message in shape)
            continue
        ids.append(value["id"])
        sequences.append(value["sequence"])
        if value["id"] in value["supersedes"]:
            errors.append(f"event-{index}:self-supersedes")
        stamp = datetime.fromisoformat(value["occurred_at"].replace("Z", "+00:00"))
        if previous_time is not None and stamp < previous_time:
            errors.append(f"event-{index}:time-regression")
        if previous_sequence is not None and value["sequence"] <= previous_sequence:
            errors.append(f"event-{index}:sequence-not-increasing")
        previous_time, previous_sequence = stamp, value["sequence"]
    if len(ids) != len(set(ids)):
        errors.append("duplicate-event-id")
    if len(sequences) != len(set(sequences)):
        errors.append("duplicate-event-sequence")
    known = set(ids)
    for index, value in enumerate(values):
        if not isinstance(value, dict) or value.get("kind") != "context-event":
            continue
        for prior in value.get("supersedes", []):
            if prior not in known:
                errors.append(f"event-{index}:unknown-superseded-event")
            elif ids.index(prior) >= index:
                errors.append(f"event-{index}:supersedes-nonprior-event")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "events": len(values),
        "append_order_consistent": not errors,
        "canonical_truth_replaced": False,
        "authorization_granted": False,
        "source_authenticity_verified": False,
    }
