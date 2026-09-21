#!/usr/bin/env python3
"""Inspect supplied DecisionRun v1 records; no provider, cache, reducer, or action executes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 131_072
SCHEMA = json.loads((ROOT / "catalog/schema/decision-run.v1.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)

class DecisionRunError(ValueError):
    pass

def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _sha(value):
    raw = value if isinstance(value, bytes) else _canonical(value)
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def identity_sha256(value):
    return _sha(value["identity"])

def reducer_input_digest(reducer):
    return _sha(reducer["inputs"])

def _ancestors(nodes):
    graph = {node["id"]: tuple(node["depends_on"]) for node in nodes}
    memo = {}
    visiting = set()
    errors = []

    def walk(node_id):
        if node_id in memo:
            return memo[node_id]
        if node_id in visiting:
            errors.append("cycle")
            return set()
        visiting.add(node_id)
        found = set()
        for dep in graph.get(node_id, ()):
            if dep not in graph:
                errors.append("unknown-dependency:" + dep)
                continue
            if dep == node_id:
                errors.append("self-dependency:" + node_id)
                continue
            found.add(dep)
            found.update(walk(dep))
        visiting.remove(node_id)
        memo[node_id] = found
        return found

    for node_id in graph:
        walk(node_id)
    return memo, sorted(set(errors))

def inspect_run(value):
    raw = _canonical(value)
    if len(raw) > MAX_BYTES:
        raise DecisionRunError("record-size-limit-exceeded")
    shape = sorted(error.message for error in VALIDATOR.iter_errors(value))
    if shape:
        return {"valid": False, "errors": shape, "identity_matches": False,
                "replay_without_provider": False, "cache_reuse_authorized": False,
                "execution_authorized": False, "consequence_authorized": False}

    errors = []
    ids = [node["id"] for node in value["nodes"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate-node-id")
    by_id = {node["id"]: node for node in value["nodes"]}
    ancestors, graph_errors = _ancestors(value["nodes"])
    errors.extend(graph_errors)

    identity_matches = value["identity_sha256"] == identity_sha256(value)
    if not identity_matches:
        errors.append("run-identity-mismatch")

    provider_nodes = 0
    intervals = []
    for node in value["nodes"]:
        node_id = node["id"]
        source = node["source"]
        status = node["status"]
        produced = status == "produced"

        if produced and (node["receipt_ref"] is None or node["receipt_digest"] is None):
            errors.append("produced-without-receipt:" + node_id)
        if not produced and (node["receipt_ref"] is not None or node["receipt_digest"] is not None):
            errors.append("nonproduced-with-receipt:" + node_id)

        if source == "provider":
            provider_nodes += 1
            if node["source_run_ref"] is not None or node["source_identity_sha256"] is not None:
                errors.append("provider-node-has-cache-provenance:" + node_id)
        elif source in ("cache", "replay"):
            if node["source_run_ref"] is None or node["source_identity_sha256"] is None:
                errors.append(source + "-node-missing-origin:" + node_id)
            elif node["source_identity_sha256"] != value["identity_sha256"]:
                errors.append(source + "-identity-mismatch:" + node_id)
        elif source == "none" and produced:
            errors.append("produced-node-has-no-source:" + node_id)

        reason = node["reason_code"]
        required_reason = {
            "insufficient-evidence": "insufficient-evidence",
            "conflicting-evidence": "conflicting-evidence",
            "out-of-distribution": "out-of-distribution",
            "provider-failure": "provider-failure",
            "timeout": "timeout",
            "budget-exceeded": "budget-exceeded",
            "cancelled": "cancelled",
            "blocked": "dependency-unavailable",
        }.get(status)
        if required_reason is not None and reason != required_reason:
            errors.append("status-reason-mismatch:" + node_id)
        if status == "produced" and reason != "none":
            errors.append("produced-node-has-failure-reason:" + node_id)

        left, right = node["started_at_ms"], node["ended_at_ms"]
        if (left is None) != (right is None):
            errors.append("partial-timing:" + node_id)
        if left is not None and right is not None:
            if right < left:
                errors.append("reversed-timing:" + node_id)
            else:
                intervals.append((left, right, node_id))
                for dep in ancestors.get(node_id, set()):
                    prior = by_id.get(dep)
                    if prior and prior["ended_at_ms"] is not None and prior["ended_at_ms"] > left:
                        errors.append("dependency-overlap:" + node_id)

    if provider_nodes and value["provider_calls"] == 0:
        errors.append("provider-sourced-results-without-provider-call")
    if value["mode"] == "replay":
        if value["provider_calls"] != 0:
            errors.append("replay-has-provider-calls")
        if provider_nodes:
            errors.append("replay-has-provider-sourced-node")

    events = []
    for left, right, _ in intervals:
        if left < right:
            events.append((left, 1))
            events.append((right, -1))
    active = peak = 0
    for _, delta in sorted(events, key=lambda item: (item[0], item[1])):
        active += delta
        peak = max(peak, active)
    if peak > value["limits"]["max_parallel"]:
        errors.append("max-parallel-exceeded")

    reducer_ids = set()
    for reducer in value["reducers"]:
        if reducer["id"] in reducer_ids:
            errors.append("duplicate-reducer-id")
        reducer_ids.add(reducer["id"])
        if reducer["input_digest"] != reducer_input_digest(reducer):
            errors.append("reducer-input-digest-mismatch:" + reducer["id"])
        seen = set()
        for item in reducer["inputs"]:
            node_id = item["node_id"]
            if node_id in seen:
                errors.append("duplicate-reducer-input:" + reducer["id"])
            seen.add(node_id)
            node = by_id.get(node_id)
            if node is None:
                errors.append("unknown-reducer-input:" + reducer["id"])
                continue
            for key in ("status", "receipt_ref", "receipt_digest"):
                if item[key] != node[key]:
                    errors.append("reducer-input-mismatch:" + reducer["id"] + ":" + node_id)
                    break

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "identity_matches": identity_matches,
        "peak_parallel": peak,
        "provider_nodes": provider_nodes,
        "replay_without_provider": value["mode"] == "replay" and value["provider_calls"] == 0 and provider_nodes == 0,
        "cache_reuse_authorized": False,
        "provider_call_authorized": False,
        "execution_authorized": False,
        "consequence_authorized": False,
        "reducer_execution_performed": False,
    }
