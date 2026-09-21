#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "catalog" / "schema"
FIXTURES = ROOT / "registry" / "context-gateway" / "fixtures"

SCHEMAS = {
    "request": SCHEMA_DIR / "context-gateway-request.v1.schema.json",
    "trace": SCHEMA_DIR / "context-selection-trace.v1.schema.json",
    "benchmark": SCHEMA_DIR / "context-gateway-benchmark.v1.schema.json",
    "compiled": SCHEMA_DIR / "compiled-context-plan.v1.schema.json",
}

TRACE_FILES = [
    "trace-no-memory.v1.json",
    "trace-no-memory-replay.v1.json",
    "trace-stale-memory.v1.json",
    "trace-conflicting-memory.v1.json",
    "trace-local-only.v1.json",
    "trace-budget-overflow.v1.json",
    "trace-memory-included.v1.json",
]

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
for name, path in SCHEMAS.items():
    schema = load(path)
    if not isinstance(schema, dict):
        continue
    try:
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
    except Exception as exc:
        fail(f"invalid schema {path.relative_to(ROOT)}: {exc}")


def validate(name: str, value, label: str) -> None:
    validator = validators.get(name)
    if validator is None:
        return
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        fail(f"{label}:{location}: {error.message}")


request = load(FIXTURES / "request-remote.v1.json")
traces = {name: load(FIXTURES / name) for name in TRACE_FILES}
compiled_plan = load(FIXTURES / "compiled-plan-memory.v1.json")
benchmark = load(FIXTURES / "benchmark.v1.json")

if isinstance(request, dict):
    validate("request", request, "request")
    execution = request.get("execution", {})
    policy = request.get("policy", {})
    stages = request.get("stages", {})

    if execution.get("environment") == "remote" and "local_only" in policy.get("allowed_sensitivity", []):
        fail("request: remote target cannot authorize local_only context")
    if stages.get("typed_decision") and not policy.get("semantic_gating_allowed"):
        fail("request: typed decision stage enabled while semantic gating is forbidden")
    if stages.get("generative_compression") and not policy.get("generative_compression_allowed"):
        fail("request: compression stage enabled while compression policy is forbidden")

    allocation_kinds = [
        item.get("kind")
        for item in request.get("budget", {}).get("allocations", [])
        if isinstance(item, dict)
    ]
    if len(allocation_kinds) != len(set(allocation_kinds)):
        fail("request: allocation kinds must be unique")


STAGE_ORDER = {
    "mandatory-policy": 0,
    "scope-filter": 1,
    "sensitivity-policy": 2,
    "lexical": 3,
    "semantic-search": 4,
    "typed-decision": 5,
    "compression": 6,
    "budget": 7,
}


def trace_semantic_errors(trace: dict, label: str) -> list[str]:
    local: list[str] = []

    def err(message: str) -> None:
        local.append(f"{label}: {message}")

    candidate_ids = [
        candidate.get("id")
        for candidate in trace.get("candidates", [])
        if isinstance(candidate, dict)
    ]
    if len(candidate_ids) != len(set(candidate_ids)):
        err("candidate ids must be unique")

    if isinstance(request, dict) and trace.get("request_ref") != request.get("id"):
        err("request_ref mismatch")

    included = [
        candidate
        for candidate in trace.get("candidates", [])
        if isinstance(candidate, dict) and candidate.get("final_disposition") == "included"
    ]
    selected_tokens = sum(candidate.get("estimated_tokens", 0) for candidate in included)
    budget = trace.get("budget", {})
    if budget.get("estimated_selected") != selected_tokens:
        err("budget estimated_selected must equal included candidate estimates")

    token_usage = trace.get("token_usage", {})
    if token_usage.get("estimated", {}).get("input") != selected_tokens:
        err("estimated input usage must equal selected context estimate")

    if isinstance(request, dict) and budget.get("input_limit") != request.get("budget", {}).get("input_limit"):
        err("trace input limit must match request input limit")

    limit = budget.get("input_limit")
    expected_over = isinstance(limit, int) and selected_tokens > limit
    if budget.get("over_budget") is not expected_over:
        err("over_budget must reflect selected estimated input against the limit")

    allocations = [
        item
        for item in budget.get("allocations", [])
        if isinstance(item, dict)
    ]
    kinds = [item.get("kind") for item in allocations]
    if len(kinds) != len(set(kinds)):
        err("allocation kinds must be unique")
    if sum(item.get("estimated_selected", 0) for item in allocations) != selected_tokens:
        err("allocation estimates must sum to selected estimated input")

    observed = token_usage.get("observed", {})
    observed_values = [observed.get(key) for key in ("input", "tool_output", "output")]
    observed_ref = token_usage.get("observed_source_ref")
    if any(value is not None for value in observed_values) and observed_ref is None:
        err("observed usage requires observed_source_ref")
    if all(value is None for value in observed_values) and observed_ref is not None:
        err("observed_source_ref must be null when usage is unobserved")

    remote = isinstance(request, dict) and request.get("execution", {}).get("environment") == "remote"
    typed_allowed = isinstance(request, dict) and request.get("stages", {}).get("typed_decision")
    semantic_allowed = isinstance(request, dict) and request.get("policy", {}).get("semantic_gating_allowed")

    for candidate in trace.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        candidate_id = candidate.get("id")

        if candidate.get("mandatory") and candidate.get("final_disposition") != "included":
            err(f"{candidate_id}: mandatory candidate was not included")

        source = candidate.get("source", {})
        retrieval = source.get("retrieval", {}) if isinstance(source, dict) else {}
        if source.get("kind") == "project-memory":
            for key in ("query_ref", "provider_ref", "result_digest"):
                if retrieval.get(key) is None:
                    err(f"{candidate_id}: memory retrieval missing {key}")

        if candidate.get("freshness") == "stale" and source.get("kind") == "project-memory":
            if candidate.get("final_disposition") == "included":
                err(f"{candidate_id}: stale memory was included")

        if remote and candidate.get("sensitivity") == "local_only":
            if candidate.get("final_disposition") != "rejected":
                err(f"{candidate_id}: local_only candidate reached remote selection")
            stages_seen = [stage.get("stage") for stage in candidate.get("stages", []) if isinstance(stage, dict)]
            if "sensitivity-policy" not in stages_seen:
                err(f"{candidate_id}: local_only rejection lacks sensitivity-policy stage")
            if "typed-decision" in stages_seen and stages_seen.index("typed-decision") < stages_seen.index("sensitivity-policy"):
                err(f"{candidate_id}: remote semantic decision ran before local_only sensitivity rejection")

        order = [
            STAGE_ORDER.get(stage.get("stage"), -1)
            for stage in candidate.get("stages", [])
            if isinstance(stage, dict)
        ]
        if order != sorted(order):
            err(f"{candidate_id}: stages are not ordered from cheap/policy gates to expensive stages")

        for stage in candidate.get("stages", []):
            if not isinstance(stage, dict) or stage.get("stage") != "typed-decision":
                continue
            if not typed_allowed or not semantic_allowed:
                err(f"{candidate_id}: typed decision used when request/policy disallows it")
            decision = stage.get("decision")
            if not isinstance(decision, dict):
                err(f"{candidate_id}: typed-decision stage lacks decision provenance")
                continue
            if decision.get("advisory") is not True:
                err(f"{candidate_id}: semantic decision must remain advisory")
            provider = decision.get("provider", {})
            if provider.get("type") not in {"deterministic", "human"}:
                if not provider.get("model") or not provider.get("version"):
                    err(f"{candidate_id}: semantic provider must record model and version")
            distribution = decision.get("distribution")
            if decision.get("status") == "produced" and isinstance(distribution, dict) and distribution:
                total = sum(distribution.values())
                if abs(total - 1.0) > 1e-6:
                    err(f"{candidate_id}: decision distribution must sum to 1")

    return local


for name, trace in traces.items():
    if not isinstance(trace, dict):
        continue
    validate("trace", trace, name)
    errors.extend(trace_semantic_errors(trace, name))


no_memory = traces.get("trace-no-memory.v1.json")
replay = traces.get("trace-no-memory-replay.v1.json")
if isinstance(no_memory, dict) and isinstance(replay, dict):
    if any(
        candidate.get("source", {}).get("kind") == "project-memory"
        for candidate in no_memory.get("candidates", [])
        if isinstance(candidate, dict)
    ):
        fail("no-memory fixture unexpectedly contains memory candidates")
    if no_memory.get("input_fingerprint") != replay.get("input_fingerprint"):
        fail("deterministic replay input fingerprints differ")
    if not no_memory.get("selector", {}).get("deterministic") or not replay.get("selector", {}).get("deterministic"):
        fail("deterministic replay fixtures must use deterministic selectors")
    if no_memory.get("selection_fingerprint") != replay.get("selection_fingerprint"):
        fail("same deterministic inputs produced different selection fingerprints")
    projection = lambda value: [
        (item.get("id"), item.get("final_disposition"), tuple(item.get("reasons", [])))
        for item in value.get("candidates", [])
        if isinstance(item, dict)
    ]
    if projection(no_memory) != projection(replay):
        fail("same deterministic inputs produced different candidate dispositions")


stale = traces.get("trace-stale-memory.v1.json")
if isinstance(stale, dict):
    stale_memories = [
        item for item in stale.get("candidates", [])
        if isinstance(item, dict)
        and item.get("source", {}).get("kind") == "project-memory"
        and item.get("freshness") == "stale"
    ]
    if not stale_memories or any(item.get("final_disposition") == "included" for item in stale_memories):
        fail("stale-memory fixture must contain non-included stale memory")


conflict = traces.get("trace-conflicting-memory.v1.json")
if isinstance(conflict, dict):
    conflicted = [
        item for item in conflict.get("candidates", [])
        if isinstance(item, dict) and "conflicting-memory" in item.get("reasons", [])
    ]
    if len(conflicted) < 2:
        fail("conflicting-memory fixture requires at least two conflicting candidates")
    if any(item.get("final_disposition") == "included" for item in conflicted):
        fail("unresolved conflicting memory cannot be silently included")
    if not any(
        stage.get("stage") == "typed-decision"
        for item in conflicted
        for stage in item.get("stages", [])
        if isinstance(stage, dict)
    ):
        fail("conflicting-memory fixture must exercise typed decision provenance")


local_only = traces.get("trace-local-only.v1.json")
if isinstance(local_only, dict):
    local_candidates = [
        item for item in local_only.get("candidates", [])
        if isinstance(item, dict) and item.get("sensitivity") == "local_only"
    ]
    if not local_candidates or any(item.get("final_disposition") != "rejected" for item in local_candidates):
        fail("local-only fixture must reject local_only candidates for remote handoff")


overflow = traces.get("trace-budget-overflow.v1.json")
if isinstance(overflow, dict):
    if overflow.get("budget", {}).get("over_budget") is not True:
        fail("budget-overflow fixture must report over_budget")
    mandatory = [
        item for item in overflow.get("candidates", [])
        if isinstance(item, dict) and item.get("mandatory")
    ]
    if not mandatory or any(item.get("final_disposition") != "included" for item in mandatory):
        fail("budget overflow must not remove mandatory context")


if isinstance(compiled_plan, dict):
    validate("compiled", compiled_plan, "compiled-memory-plan")
    memory_items = [
        item for item in compiled_plan.get("items", [])
        if isinstance(item, dict) and item.get("source", {}).get("kind") == "memory"
    ]
    if not memory_items:
        fail("compiled-memory-plan: expected a memory item")
    for item in memory_items:
        source = item.get("source", {})
        for key in ("memory_id", "provider_id", "query_id", "result_digest"):
            if not source.get(key):
                fail(f"compiled-memory-plan:{item.get('id')}: missing {key}")
        if not item.get("selection_trace_ref"):
            fail(f"compiled-memory-plan:{item.get('id')}: missing selection_trace_ref")


if isinstance(benchmark, dict):
    validate("benchmark", benchmark, "benchmark")
    baseline = benchmark.get("baseline", {})
    gateway = benchmark.get("gateway", {})
    comparison = benchmark.get("comparison", {})

    for label, variant in (("baseline", baseline), ("gateway", gateway)):
        if variant.get("outcome", {}).get("status") != "verified":
            fail(f"benchmark:{label}: outcome must be independently verified")
        if variant.get("mandatory_context_complete") is not True:
            fail(f"benchmark:{label}: mandatory context must be complete")
        if not variant.get("usage", {}).get("observed_source_ref"):
            fail(f"benchmark:{label}: observed usage requires an authoritative source reference")

    estimated_delta = (
        gateway.get("usage", {}).get("estimated", {}).get("input", 0)
        - baseline.get("usage", {}).get("estimated", {}).get("input", 0)
    )
    observed_delta = (
        gateway.get("usage", {}).get("observed", {}).get("input", 0)
        - baseline.get("usage", {}).get("observed", {}).get("input", 0)
    )
    if comparison.get("estimated_input_delta") != estimated_delta:
        fail("benchmark: estimated input delta is inconsistent")
    if comparison.get("observed_input_delta") != observed_delta:
        fail("benchmark: observed input delta is inconsistent")
    if comparison.get("outcome_equivalent") is not True:
        fail("benchmark: fixture must verify equivalent outcomes")
    if comparison.get("quality_regression") is not False:
        fail("benchmark: fixture must not claim equivalence while reporting a quality regression")


# Negative conformance checks make policy boundaries executable.
if isinstance(overflow, dict):
    invalid = copy.deepcopy(overflow)
    for candidate in invalid.get("candidates", []):
        if candidate.get("mandatory"):
            candidate["final_disposition"] = "deferred"
            break
    if validators.get("trace") and validators["trace"].is_valid(invalid):
        fail("negative fixture: schema allowed mandatory context to be deferred")

if isinstance(local_only, dict):
    invalid = copy.deepcopy(local_only)
    for candidate in invalid.get("candidates", []):
        if candidate.get("sensitivity") == "local_only":
            candidate["final_disposition"] = "included"
            break
    if not trace_semantic_errors(invalid, "negative-local-only"):
        fail("negative fixture: semantic validation allowed local_only remote inclusion")

if isinstance(conflict, dict):
    invalid = copy.deepcopy(conflict)
    changed = False
    for candidate in invalid.get("candidates", []):
        for stage in candidate.get("stages", []):
            decision = stage.get("decision")
            if isinstance(decision, dict):
                decision["advisory"] = False
                changed = True
                break
        if changed:
            break
    if validators.get("trace") and validators["trace"].is_valid(invalid):
        fail("negative fixture: schema allowed semantic decision to become non-advisory")


if errors:
    print("Context Gateway validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "Context Gateway valid: "
    f"{len(validators)} schemas, {len(traces)} selection traces, "
    "deterministic replay + memory/privacy/budget/benchmark invariants passed"
)
