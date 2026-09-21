#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
MEMORY = ROOT / "registry" / "project-memory"
FIXTURES = MEMORY / "fixtures"

SCHEMAS = {
    "project-memory": MEMORY / "memory.v1.schema.json",
    "memory-query": MEMORY / "memory-query.v1.schema.json",
    "memory-result": MEMORY / "memory-result.v1.schema.json",
    "memory-provider": MEMORY / "memory-provider.v1.schema.json",
    "memory-operation": MEMORY / "memory-operation.v1.schema.json",
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return None


validators: dict[str, Draft202012Validator] = {}
for kind, path in SCHEMAS.items():
    schema = load(path)
    if not isinstance(schema, dict):
        continue
    try:
        Draft202012Validator.check_schema(schema)
        validators[kind] = Draft202012Validator(schema, format_checker=FormatChecker())
    except Exception as exc:
        fail(f"invalid schema {path.relative_to(ROOT)}: {exc}")


def validate(kind: str, value, label: str) -> None:
    validator = validators.get(kind)
    if validator is None:
        return
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        fail(f"{label}:{location}: {error.message}")


memories_value = load(FIXTURES / "memories.v1.json")
operations_value = load(FIXTURES / "operations.v1.json")
local_provider = load(FIXTURES / "provider-local.v1.json")
remote_provider = load(FIXTURES / "provider-remote.v1.json")
hybrid_provider = load(FIXTURES / "provider-hybrid.v1.json")
query = load(FIXTURES / "query-remote.v1.json")
result = load(FIXTURES / "result-remote.v1.json")

memories = memories_value if isinstance(memories_value, list) else []
operations = operations_value if isinstance(operations_value, list) else []
memory_by_id: dict[str, dict] = {}

for index, memory in enumerate(memories):
    validate("project-memory", memory, f"memories[{index}]")
    if not isinstance(memory, dict):
        continue
    memory_id = memory.get("id")
    if not isinstance(memory_id, str):
        continue
    if memory_id in memory_by_id:
        fail(f"memories[{index}]: duplicate memory id {memory_id}")
    memory_by_id[memory_id] = memory

    lineage = memory.get("lineage", {})
    if not isinstance(lineage, dict):
        continue
    related = []
    for key in ("supersedes", "invalidates", "consolidated_from", "conflicts_with"):
        value = lineage.get(key, [])
        if isinstance(value, list):
            related.extend(value)
    for key in ("superseded_by", "consolidated_into"):
        value = lineage.get(key)
        if isinstance(value, str):
            related.append(value)
    if memory_id in related:
        fail(f"{memory_id}: lineage cannot reference itself")

    sensitivity = memory.get("sensitivity", {})
    if isinstance(sensitivity, dict) and sensitivity.get("level") == "local_only":
        if sensitivity.get("remote_persistence_allowed") is not False:
            fail(f"{memory_id}: local_only memory cannot allow remote persistence")
        if sensitivity.get("remote_retrieval_allowed") is not False:
            fail(f"{memory_id}: local_only memory cannot allow remote retrieval")

    state = memory.get("state")
    validity = memory.get("validity", {})
    if state == "stale" and isinstance(validity, dict) and validity.get("status") != "stale":
        fail(f"{memory_id}: stale memory must report stale validity")
    if state == "superseded" and not isinstance(lineage.get("superseded_by"), str):
        fail(f"{memory_id}: superseded memory requires superseded_by")
    if state == "invalidated" and not isinstance(lineage.get("invalidated_by"), str):
        fail(f"{memory_id}: invalidated memory requires invalidated_by")
    if state == "consolidated" and not isinstance(lineage.get("consolidated_into"), str):
        fail(f"{memory_id}: consolidated memory requires consolidated_into")

for memory_id, memory in memory_by_id.items():
    lineage = memory.get("lineage", {})
    if not isinstance(lineage, dict):
        continue

    superseded_by = lineage.get("superseded_by")
    if isinstance(superseded_by, str):
        target = memory_by_id.get(superseded_by)
        if target is None:
            fail(f"{memory_id}: unknown superseded_by {superseded_by}")
        elif memory_id not in target.get("lineage", {}).get("supersedes", []):
            fail(f"{memory_id}: supersession lineage must be bidirectional")

    for old_id in lineage.get("supersedes", []):
        old = memory_by_id.get(old_id)
        if old is None:
            fail(f"{memory_id}: unknown supersedes target {old_id}")
        elif old.get("lineage", {}).get("superseded_by") != memory_id:
            fail(f"{memory_id}: supersedes target does not point back")

    consolidated_into = lineage.get("consolidated_into")
    if isinstance(consolidated_into, str):
        target = memory_by_id.get(consolidated_into)
        if target is None:
            fail(f"{memory_id}: unknown consolidated_into {consolidated_into}")
        elif memory_id not in target.get("lineage", {}).get("consolidated_from", []):
            fail(f"{memory_id}: consolidation lineage must be bidirectional")

    for conflict_id in lineage.get("conflicts_with", []):
        conflict = memory_by_id.get(conflict_id)
        if conflict is None:
            fail(f"{memory_id}: unknown conflict {conflict_id}")
        elif memory_id not in conflict.get("lineage", {}).get("conflicts_with", []):
            fail(f"{memory_id}: conflicts_with must be bidirectional")

    consolidated_from = lineage.get("consolidated_from", [])
    if consolidated_from:
        expected: set[str] = set()
        for source_id in consolidated_from:
            source = memory_by_id.get(source_id)
            if source is None:
                fail(f"{memory_id}: unknown consolidation source {source_id}")
                continue
            expected.update(source.get("source", {}).get("source_refs", []))
        actual = set(memory.get("source", {}).get("source_refs", []))
        if not expected.issubset(actual):
            fail(f"{memory_id}: consolidation lost source refs {sorted(expected - actual)}")

operation_by_id: dict[str, dict] = {}
for index, operation in enumerate(operations):
    validate("memory-operation", operation, f"operations[{index}]")
    if not isinstance(operation, dict):
        continue
    operation_id = operation.get("id")
    if isinstance(operation_id, str):
        if operation_id in operation_by_id:
            fail(f"operations[{index}]: duplicate operation id {operation_id}")
        operation_by_id[operation_id] = operation

    targets = operation.get("target_memory_refs", [])
    for target_id in targets:
        if target_id not in memory_by_id:
            fail(f"{operation_id}: unknown target {target_id}")
    result_ref = operation.get("result_memory_ref")
    if isinstance(result_ref, str) and result_ref not in memory_by_id:
        fail(f"{operation_id}: unknown result {result_ref}")

    op = operation.get("operation")
    if op == "promote":
        if len(targets) != 1 or memory_by_id.get(targets[0], {}).get("state") != "candidate":
            fail(f"{operation_id}: promotion requires one candidate")
        promoted = memory_by_id.get(result_ref)
        if not isinstance(promoted, dict) or promoted.get("state") != "accepted":
            fail(f"{operation_id}: promotion result must be accepted")
        elif targets[0] not in promoted.get("source", {}).get("source_refs", []):
            fail(f"{operation_id}: promotion must retain candidate provenance")
    elif op == "supersede":
        replacement = memory_by_id.get(result_ref)
        if not isinstance(replacement, dict) or replacement.get("state") != "accepted":
            fail(f"{operation_id}: replacement must be accepted")
        for target_id in targets:
            target = memory_by_id.get(target_id, {})
            if target.get("state") != "superseded":
                fail(f"{operation_id}: target must be superseded")
            if target.get("lineage", {}).get("superseded_by") != result_ref:
                fail(f"{operation_id}: target must point to replacement")
    elif op == "invalidate":
        if result_ref is not None:
            fail(f"{operation_id}: invalidate cannot emit a replacement")
        for target_id in targets:
            target = memory_by_id.get(target_id, {})
            if target.get("state") != "invalidated":
                fail(f"{operation_id}: target must be invalidated")
            if target.get("lineage", {}).get("invalidated_by") != operation_id:
                fail(f"{operation_id}: target must retain operation lineage")
    elif op == "consolidate":
        consolidated = memory_by_id.get(result_ref)
        if not isinstance(consolidated, dict) or consolidated.get("state") != "accepted":
            fail(f"{operation_id}: consolidation result must be accepted")
        elif set(consolidated.get("lineage", {}).get("consolidated_from", [])) != set(targets):
            fail(f"{operation_id}: result must reference all inputs")
        for target_id in targets:
            target = memory_by_id.get(target_id, {})
            if target.get("state") != "consolidated":
                fail(f"{operation_id}: input must be consolidated")
            if target.get("lineage", {}).get("consolidated_into") != result_ref:
                fail(f"{operation_id}: input must point at result")

for memory_id, memory in memory_by_id.items():
    invalidated_by = memory.get("lineage", {}).get("invalidated_by")
    if isinstance(invalidated_by, str) and invalidated_by not in operation_by_id:
        fail(f"{memory_id}: invalidated_by references unknown operation {invalidated_by}")

for label, provider in (("local-provider", local_provider), ("remote-provider", remote_provider), ("hybrid-provider", hybrid_provider)):
    if isinstance(provider, dict):
        validate("memory-provider", provider, label)

if isinstance(hybrid_provider, dict):
    hybrid_policy = hybrid_provider.get("sensitivity_policy", {})
    if hybrid_provider.get("mode") == "hybrid" and hybrid_policy.get("enforce_before_remote_handoff") is not True:
        fail("hybrid-provider: sensitivity must be enforced before remote handoff")

if isinstance(remote_provider, dict):
    policy = remote_provider.get("sensitivity_policy", {})
    accepted = policy.get("accepted_levels", []) if isinstance(policy, dict) else []
    if remote_provider.get("mode") == "remote" and "local_only" in accepted:
        fail("remote-provider: remote provider cannot accept local_only memory")
    if remote_provider.get("mode") == "remote" and policy.get("enforce_before_remote_handoff") is not True:
        fail("remote-provider: sensitivity must be enforced before handoff")

if isinstance(query, dict):
    validate("memory-query", query, "query-remote")
    if query.get("execution_environment") == "remote" and "local_only" in query.get("allowed_sensitivity", []):
        fail("query-remote: remote query cannot authorize local_only memory")

if isinstance(result, dict):
    validate("memory-result", result, "result-remote")
    if isinstance(query, dict) and result.get("query_id") != query.get("id"):
        fail("result-remote: query_id mismatch")
    if isinstance(remote_provider, dict) and result.get("provider_id") != remote_provider.get("id"):
        fail("result-remote: provider_id mismatch")

    matched_ids = [m.get("memory_id") for m in result.get("matches", []) if isinstance(m, dict)]
    if len(matched_ids) != len(set(matched_ids)):
        fail("result-remote: duplicate matches")

    states = set(query.get("states", [])) if isinstance(query, dict) else set()
    sensitivities = set(query.get("allowed_sensitivity", [])) if isinstance(query, dict) else set()
    for memory_id in matched_ids:
        memory = memory_by_id.get(memory_id)
        if memory is None:
            fail(f"result-remote: unknown match {memory_id}")
            continue
        if states and memory.get("state") not in states:
            fail(f"result-remote: disallowed state for {memory_id}")
        sensitivity = memory.get("sensitivity", {})
        if sensitivity.get("level") not in sensitivities:
            fail(f"result-remote: disallowed sensitivity for {memory_id}")
        if sensitivity.get("remote_retrieval_allowed") is not True:
            fail(f"result-remote: remote retrieval not authorized for {memory_id}")
        if memory.get("state") == "stale" and not query.get("include_stale"):
            fail(f"result-remote: stale memory matched while include_stale=false: {memory_id}")

    excluded = {
        item.get("memory_id"): item.get("reason")
        for item in result.get("excluded", [])
        if isinstance(item, dict)
    }
    for memory_id, memory in memory_by_id.items():
        if memory.get("sensitivity", {}).get("level") != "local_only":
            continue
        if memory_id in matched_ids:
            fail(f"result-remote: leaked local_only memory {memory_id}")
        if excluded.get(memory_id) != "sensitivity":
            fail(f"result-remote: local_only memory must be excluded for sensitivity: {memory_id}")

if errors:
    print("Project Memory validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "Project Memory valid: "
    f"{len(validators)} schemas, {len(memories)} memories, "
    f"{len(operations)} lifecycle operations"
)
