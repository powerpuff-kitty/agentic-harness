#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

WORK = Path(__file__).resolve().parents[1]
SCHEMA_PATH = WORK / "otel-export.v1.schema.json"

SENSITIVE_ATTRIBUTE_KEYS = {
    "gen_ai.input.messages",
    "gen_ai.output.messages",
    "gen_ai.prompt",
    "gen_ai.completion",
    "agent.work.prompt",
    "agent.work.response",
    "http.request.body",
    "http.response.body",
    "db.statement",
    "messaging.message.body",
}
SENSITIVE_KEY_SEGMENTS = {
    "secret",
    "password",
    "authorization",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_errors(export: Any) -> list[str]:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(export), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"schema:{location}: {error.message}")
    return errors


def canonical_entities(work_unit: dict[str, Any] | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "work-unit": set(),
        "run": set(),
        "task": set(),
        "attempt": set(),
        "task_to_run": {},
        "attempt_to_run": {},
        "attempt_to_task": {},
    }
    if not isinstance(work_unit, dict):
        return result

    work_unit_id = work_unit.get("id")
    if isinstance(work_unit_id, str):
        result["work-unit"].add(work_unit_id)

    for run in work_unit.get("runs", []):
        if not isinstance(run, dict) or not isinstance(run.get("id"), str):
            continue
        run_id = run["id"]
        result["run"].add(run_id)
        for task in run.get("tasks", []):
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                continue
            task_id = task["id"]
            result["task"].add(task_id)
            result["task_to_run"][task_id] = run_id
        for attempt in run.get("attempts", []):
            if not isinstance(attempt, dict) or not isinstance(attempt.get("id"), str):
                continue
            attempt_id = attempt["id"]
            result["attempt"].add(attempt_id)
            result["attempt_to_run"][attempt_id] = run_id
            if isinstance(attempt.get("task_id"), str):
                result["attempt_to_task"][attempt_id] = attempt["task_id"]
    return result


def sensitive_attribute_error(key: str) -> bool:
    lowered = key.lower()
    if lowered in SENSITIVE_ATTRIBUTE_KEYS:
        return True
    segments = {segment.replace("-", "_") for segment in lowered.split(".")}
    return bool(segments & SENSITIVE_KEY_SEGMENTS)


def semantic_errors(
    export: Any,
    work_unit: dict[str, Any] | None = None,
    canonical_events: list[dict[str, Any]] | None = None,
    canonical_redactions: list[dict[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(export, dict):
        return ["semantic:<root>: export must be an object"]

    spans = export.get("spans", [])
    if not isinstance(spans, list):
        return ["semantic:spans: spans must be an array"]

    work_unit_id = export.get("work_unit_id")
    span_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    entity_spans: list[dict[str, Any]] = []

    for index, span in enumerate(spans):
        if not isinstance(span, dict):
            continue
        trace_id = span.get("trace_id")
        span_id = span.get("span_id")
        key = (trace_id, span_id)
        if key in span_by_key:
            errors.append(f"semantic:spans[{index}]: duplicate span identity {trace_id}/{span_id}")
        else:
            span_by_key[key] = span

        try:
            started_at = parse_time(span["started_at"])
            ended_at = parse_time(span["ended_at"])
            if ended_at < started_at:
                errors.append(f"semantic:spans[{index}]: ended_at precedes started_at")
        except Exception:
            # JSON Schema reports malformed/missing timestamps.
            pass

        entity = span.get("entity", {})
        attributes = span.get("attributes", {})
        if not isinstance(entity, dict) or not isinstance(attributes, dict):
            continue
        entity_spans.append(span)
        entity_kind = entity.get("kind")
        entity_id = entity.get("id")

        required_attributes = {
            "agent.work.protocol.version": 1,
            "agent.work.work_unit.id": work_unit_id,
            "agent.work.entity.kind": entity_kind,
            "agent.work.entity.id": entity_id,
        }
        specific_key = {
            "run": "agent.work.run.id",
            "task": "agent.work.task.id",
            "attempt": "agent.work.attempt.id",
            "action": "agent.work.action.id",
        }.get(entity_kind)
        if specific_key:
            required_attributes[specific_key] = entity_id

        for attr_key, expected in required_attributes.items():
            if attributes.get(attr_key) != expected:
                errors.append(
                    f"semantic:spans[{index}]: {attr_key} must equal {expected!r}"
                )

        for attr_key in attributes:
            if sensitive_attribute_error(attr_key):
                errors.append(
                    f"semantic:spans[{index}]: metadata-only export forbids sensitive/content attribute {attr_key}"
                )

        parent_span_id = span.get("parent_span_id")
        if parent_span_id is not None and (trace_id, parent_span_id) not in span_by_key:
            # Parent may appear later in the array. Defer until every span is indexed.
            pass

    # Parent references and cycles need the complete span index.
    for index, span in enumerate(spans):
        if not isinstance(span, dict):
            continue
        trace_id = span.get("trace_id")
        parent_span_id = span.get("parent_span_id")
        if parent_span_id is not None and (trace_id, parent_span_id) not in span_by_key:
            errors.append(
                f"semantic:spans[{index}]: parent span {trace_id}/{parent_span_id} is absent"
            )

        seen: set[tuple[str, str]] = set()
        cursor = (span.get("trace_id"), span.get("span_id"))
        while cursor in span_by_key:
            if cursor in seen:
                errors.append(
                    f"semantic:spans[{index}]: parent relationship contains a cycle at {cursor[1]}"
                )
                break
            seen.add(cursor)
            current = span_by_key[cursor]
            parent = current.get("parent_span_id")
            if parent is None:
                break
            cursor = (current.get("trace_id"), parent)

    entities = canonical_entities(work_unit)
    if isinstance(work_unit, dict):
        if work_unit.get("id") != work_unit_id:
            errors.append(
                "semantic:work_unit_id: export work_unit_id does not match canonical WorkUnit"
            )

        for index, span in enumerate(spans):
            if not isinstance(span, dict):
                continue
            entity = span.get("entity", {})
            attributes = span.get("attributes", {})
            if not isinstance(entity, dict) or not isinstance(attributes, dict):
                continue
            kind = entity.get("kind")
            entity_id = entity.get("id")
            if kind in {"work-unit", "run", "task", "attempt"}:
                if entity_id not in entities[kind]:
                    errors.append(
                        f"semantic:spans[{index}]: {kind} {entity_id} is absent from canonical WorkUnit"
                    )
            if kind == "task" and entity_id in entities["task_to_run"]:
                expected_run = entities["task_to_run"][entity_id]
                if attributes.get("agent.work.run.id") != expected_run:
                    errors.append(
                        f"semantic:spans[{index}]: task {entity_id} must correlate to run {expected_run}"
                    )
            if kind == "attempt" and entity_id in entities["attempt_to_run"]:
                expected_run = entities["attempt_to_run"][entity_id]
                expected_task = entities["attempt_to_task"].get(entity_id)
                if attributes.get("agent.work.run.id") != expected_run:
                    errors.append(
                        f"semantic:spans[{index}]: attempt {entity_id} must correlate to run {expected_run}"
                    )
                if attributes.get("agent.work.task.id") != expected_task:
                    errors.append(
                        f"semantic:spans[{index}]: attempt {entity_id} must correlate to task {expected_task}"
                    )

        if export.get("status") == "collected":
            roots = [
                span
                for span in spans
                if isinstance(span, dict)
                and span.get("entity") == {"kind": "work-unit", "id": work_unit_id}
                and span.get("parent_span_id") is None
            ]
            if len(roots) != 1:
                errors.append(
                    "semantic:spans: collected export requires exactly one root WorkUnit span"
                )

    event_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(canonical_events, list):
        for event in canonical_events:
            if isinstance(event, dict) and isinstance(event.get("id"), str):
                event_by_id[event["id"]] = event

    observed_event_ids: list[str] = []
    for span_index, span in enumerate(spans):
        if not isinstance(span, dict):
            continue
        for event_index, event in enumerate(span.get("events", [])):
            if not isinstance(event, dict):
                continue
            canonical_event_id = event.get("canonical_event_id")
            if canonical_event_id is None:
                continue
            if canonical_event_id in observed_event_ids:
                errors.append(
                    f"semantic:spans[{span_index}].events[{event_index}]: duplicate canonical event {canonical_event_id}"
                )
            observed_event_ids.append(canonical_event_id)

            if not event_by_id:
                continue
            canonical = event_by_id.get(canonical_event_id)
            if canonical is None:
                errors.append(
                    f"semantic:spans[{span_index}].events[{event_index}]: unknown canonical event {canonical_event_id}"
                )
                continue

            if event.get("occurred_at") != canonical.get("occurred_at"):
                errors.append(
                    f"semantic:spans[{span_index}].events[{event_index}]: timestamp differs from canonical event {canonical_event_id}"
                )

            attributes = event.get("attributes", {})
            if not isinstance(attributes, dict):
                continue
            if attributes.get("agent.work.event.id") != canonical_event_id:
                errors.append(
                    f"semantic:spans[{span_index}].events[{event_index}]: event id attribute mismatch"
                )
            if attributes.get("agent.work.event.type") != canonical.get("type"):
                errors.append(
                    f"semantic:spans[{span_index}].events[{event_index}]: event type attribute mismatch"
                )
            for attr_key in attributes:
                if sensitive_attribute_error(attr_key):
                    errors.append(
                        f"semantic:spans[{span_index}].events[{event_index}]: metadata-only export forbids sensitive/content attribute {attr_key}"
                    )

            delta = canonical.get("projection_delta")
            if isinstance(delta, dict) and delta.get("operation") == "state_transition":
                previous_state = delta.get("previous_state")
                next_state = delta.get("next_state")
                if attributes.get("agent.work.state.previous") != previous_state:
                    errors.append(
                        f"semantic:spans[{span_index}].events[{event_index}]: previous state mismatch for {canonical_event_id}"
                    )
                if attributes.get("agent.work.state.next") != next_state:
                    errors.append(
                        f"semantic:spans[{span_index}].events[{event_index}]: next state mismatch for {canonical_event_id}"
                    )

    if event_by_id and export.get("status") == "collected":
        missing = sorted(set(event_by_id) - set(observed_event_ids))
        extra = sorted(set(observed_event_ids) - set(event_by_id))
        if missing:
            errors.append(
                f"semantic:events: collected export is missing canonical events {missing}"
            )
        if extra:
            errors.append(
                f"semantic:events: collected export has unknown canonical events {extra}"
            )

    redaction_ids: set[str] = set()
    if isinstance(canonical_redactions, list):
        redaction_ids = {
            item["id"]
            for item in canonical_redactions
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
    if redaction_ids:
        content_policy = export.get("content_policy", {})
        if isinstance(content_policy, dict):
            for redaction_ref in content_policy.get("redaction_refs", []):
                if redaction_ref not in redaction_ids:
                    errors.append(
                        f"semantic:content_policy: unknown canonical redaction {redaction_ref}"
                    )

    return errors


def validate_export(
    export: Any,
    work_unit: dict[str, Any] | None,
    events: list[dict[str, Any]] | None,
    redactions: list[dict[str, Any]] | None,
) -> list[str]:
    return schema_errors(export) + semantic_errors(export, work_unit, events, redactions)


def run_self_test(
    export: dict[str, Any],
    work_unit: dict[str, Any],
    events: list[dict[str, Any]],
    redactions: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []

    def expect(mutated: dict[str, Any], fragment: str, label: str) -> None:
        observed = validate_export(mutated, work_unit, events, redactions)
        if not any(fragment in item for item in observed):
            failures.append(
                f"self-test:{label}: expected error containing {fragment!r}, got {observed}"
            )

    duplicate = copy.deepcopy(export)
    duplicate["spans"].append(copy.deepcopy(duplicate["spans"][0]))
    expect(duplicate, "duplicate span identity", "duplicate-span")

    wrong_entity = copy.deepcopy(export)
    wrong_entity["spans"][0]["attributes"]["agent.work.entity.id"] = "wu:wrong"
    expect(wrong_entity, "agent.work.entity.id must equal", "entity-correlation")

    sensitive = copy.deepcopy(export)
    sensitive["spans"][0]["attributes"]["gen_ai.input.messages"] = "forbidden-content"
    expect(sensitive, "metadata-only export forbids", "sensitive-content")

    wrong_state = copy.deepcopy(export)
    event = wrong_state["spans"][0]["events"][0]
    event["attributes"]["agent.work.state.next"] = "failed"
    expect(wrong_state, "next state mismatch", "state-correlation")

    missing_event = copy.deepcopy(export)
    missing_event["spans"][0]["events"] = missing_event["spans"][0]["events"][1:]
    expect(missing_event, "collected export is missing canonical events", "event-coverage")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Agent Work OpenTelemetry export against optional canonical fixtures."
    )
    parser.add_argument("export", type=Path)
    parser.add_argument("--canonical-work-unit", type=Path)
    parser.add_argument("--canonical-events", type=Path)
    parser.add_argument("--canonical-redactions", type=Path)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic negative mutations after validating a collected fixture.",
    )
    args = parser.parse_args()

    try:
        export = load_json(args.export)
        work_unit = load_json(args.canonical_work_unit) if args.canonical_work_unit else None
        events = load_json(args.canonical_events) if args.canonical_events else None
        redactions = load_json(args.canonical_redactions) if args.canonical_redactions else None
    except Exception as exc:
        print(f"OpenTelemetry export validation failed: {exc}", file=sys.stderr)
        return 2

    errors = validate_export(export, work_unit, events, redactions)
    if errors:
        print("OpenTelemetry export validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.self_test:
        if not (
            isinstance(export, dict)
            and export.get("status") == "collected"
            and isinstance(work_unit, dict)
            and isinstance(events, list)
            and isinstance(redactions, list)
        ):
            print(
                "--self-test requires a collected export and all canonical inputs",
                file=sys.stderr,
            )
            return 2
        failures = run_self_test(export, work_unit, events, redactions)
        if failures:
            print("OpenTelemetry export self-test failed:", file=sys.stderr)
            for failure in failures:
                print(f"- {failure}", file=sys.stderr)
            return 1

    span_count = len(export.get("spans", [])) if isinstance(export, dict) else 0
    mapped_events = (
        sum(
            len(span.get("events", []))
            for span in export.get("spans", [])
            if isinstance(span, dict)
        )
        if isinstance(export, dict)
        else 0
    )
    print(
        "Agent Work OpenTelemetry export valid: "
        f"status={export.get('status')}, spans={span_count}, mapped_events={mapped_events}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
