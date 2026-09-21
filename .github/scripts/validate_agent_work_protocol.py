#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "registry" / "agent-work"
FIXTURES = WORK / "fixtures"

SCHEMAS = {
    "work-unit": WORK / "work-unit.v1.schema.json",
    "work-event": WORK / "work-event.v1.schema.json",
    "work-evaluation": WORK / "evaluation.v1.schema.json",
    "work-action": WORK / "work-action.v1.schema.json",
    "agent-connection": WORK / "agent-connection.v1.schema.json",
    "work-reflection": WORK / "reflection.v1.schema.json",
    "reflection-policy": WORK / "reflection-policy.v1.schema.json",
    "reflection-trigger-decision": WORK / "reflection-trigger-decision.v1.schema.json",
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


def validate_event_list(value, label: str) -> None:
    if not isinstance(value, list):
        fail(f"{label}: expected an array of work events")
        return

    last_sequence = -1
    event_ids: set[str] = set()
    work_unit_id = None

    for index, event in enumerate(value):
        validate("work-event", event, f"{label}[{index}]")
        if not isinstance(event, dict):
            continue

        event_id = event.get("id")
        if event_id in event_ids:
            fail(f"{label}[{index}]: duplicate event id {event_id}")
        event_ids.add(event_id)

        sequence = event.get("sequence")
        if isinstance(sequence, int) and sequence <= last_sequence:
            fail(f"{label}[{index}]: sequence must be strictly increasing")
        if isinstance(sequence, int):
            last_sequence = sequence

        if work_unit_id is None:
            work_unit_id = event.get("work_unit_id")
        elif event.get("work_unit_id") != work_unit_id:
            fail(f"{label}[{index}]: fixture mixes work units")


work_unit = load(FIXTURES / "replanned-work-unit.v1.json")
evaluation = load(FIXTURES / "evaluation.v1.json")
action = load(FIXTURES / "action.v1.json")
connection = load(FIXTURES / "agent-connection.v1.json")
events = load(FIXTURES / "events.v1.json")

reflection_files = [
    "reflection-failed-test.v1.json",
    "reflection-bad-assumption.v1.json",
    "reflection-insufficient-evidence.v1.json",
    "reflection-abstained.v1.json",
]
reflections = [(name, load(FIXTURES / name)) for name in reflection_files]
reflection_policy = load(FIXTURES / "reflection-policy.v1.json")
reflection_decision = load(FIXTURES / "reflection-trigger-skip.v1.json")
reflection_events = load(FIXTURES / "reflection-correction-events.v1.json")
corrected_work_unit = load(FIXTURES / "reflection-corrected-work-unit.v1.json")

if isinstance(work_unit, dict):
    validate("work-unit", work_unit, "replanned-work-unit")
    run_ids = [run.get("id") for run in work_unit.get("runs", []) if isinstance(run, dict)]
    if len(run_ids) != len(set(run_ids)):
        fail("work-unit: run ids must be unique")
    if work_unit.get("current_run_id") is not None and work_unit.get("current_run_id") not in run_ids:
        fail("work-unit: current_run_id must reference an existing run")

    for run in work_unit.get("runs", []):
        if not isinstance(run, dict):
            continue

        tasks = run.get("tasks", [])
        task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
        known = set(task_ids)
        if len(task_ids) != len(known):
            fail(f"{run.get('id')}: task ids must be unique")

        dependencies: dict[str, list[str]] = {}
        for task in tasks:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                continue
            task_id = task["id"]
            parent = task.get("parent_id")
            if parent is not None and parent not in known:
                fail(f"{run.get('id')}: {task_id} references missing parent {parent}")

            deps = task.get("depends_on", [])
            dependencies[task_id] = list(deps) if isinstance(deps, list) else []
            for dependency in dependencies[task_id]:
                if dependency not in known:
                    fail(f"{run.get('id')}: {task_id} references missing dependency {dependency}")
                if dependency == task_id:
                    fail(f"{run.get('id')}: {task_id} cannot depend on itself")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visited:
                return
            if task_id in visiting:
                fail(f"{run.get('id')}: task dependency graph contains a cycle at {task_id}")
                return
            visiting.add(task_id)
            for dependency in dependencies.get(task_id, []):
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in known:
            visit(task_id)

        revisions = run.get("plan_revisions", [])
        numbers = [item.get("revision") for item in revisions if isinstance(item, dict)]
        if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
            fail(f"{run.get('id')}: plan revisions must be unique and monotonically increasing")
        for revision in revisions:
            if not isinstance(revision, dict):
                continue
            for task_id in revision.get("task_ids", []):
                if task_id not in known:
                    fail(f"{run.get('id')}: plan revision references unknown task {task_id}")

        attempts_seen: set[tuple[str, int]] = set()
        for attempt in run.get("attempts", []):
            if not isinstance(attempt, dict):
                continue
            key = (attempt.get("task_id"), attempt.get("ordinal"))
            if attempt.get("task_id") not in known:
                fail(f"{run.get('id')}: attempt references unknown task {attempt.get('task_id')}")
            if key in attempts_seen:
                fail(f"{run.get('id')}: duplicate task attempt {key}")
            attempts_seen.add(key)

if isinstance(evaluation, dict):
    validate("work-evaluation", evaluation, "evaluation")
    for dimension in evaluation.get("dimensions", []):
        if not isinstance(dimension, dict):
            continue
        status = dimension.get("status")
        score = dimension.get("score")
        if status in {"unknown", "not_checked", "blocked", "not_applicable"} and score is not None:
            fail(f"evaluation:{dimension.get('id')}: non-measured status cannot carry a score")
        if status in {"measured", "judged"} and score is not None and not dimension.get("method"):
            fail(f"evaluation:{dimension.get('id')}: scored dimensions require a method")

    for signal in evaluation.get("confidence", []):
        if not isinstance(signal, dict):
            continue
        status = signal.get("status")
        value = signal.get("value")
        if status in {"unknown", "not_checked", "blocked", "not_applicable"} and value is not None:
            fail(f"evaluation:{signal.get('kind')}: non-measured confidence cannot carry a value")
        if value is not None and not signal.get("method"):
            fail(f"evaluation:{signal.get('kind')}: confidence values require a method")

if isinstance(action, dict):
    validate("work-action", action, "action")
    permissions = action.get("permissions", {})
    if action.get("intent") in {"inspect", "audit", "evaluate", "reflect", "reassess", "validate", "compare_requirements", "review"}:
        if isinstance(permissions, dict) and any(permissions.get(key) for key in ("write", "commit", "create_pr")):
            fail("action: read/review/reflection intent requests write-capable permissions")

if isinstance(connection, dict):
    validate("agent-connection", connection, "agent-connection")
    capabilities = connection.get("capabilities", {})
    if isinstance(capabilities, dict):
        if capabilities.get("commit") and not capabilities.get("write_repo"):
            fail("agent-connection: commit capability requires write_repo")
        if capabilities.get("create_pr") and not capabilities.get("commit"):
            fail("agent-connection: create_pr capability requires commit")

validate_event_list(events, "events")
validate_event_list(reflection_events, "reflection-correction-events")

reflection_by_id: dict[str, dict] = {}
for filename, reflection in reflections:
    if not isinstance(reflection, dict):
        continue

    validate("work-reflection", reflection, filename)
    reflection_id = reflection.get("id")
    if isinstance(reflection_id, str):
        if reflection_id in reflection_by_id:
            fail(f"{filename}: duplicate reflection id {reflection_id}")
        reflection_by_id[reflection_id] = reflection

    status = reflection.get("status")
    evidence_refs = reflection.get("evidence_refs", [])
    observation = reflection.get("observation", {})
    corrections = reflection.get("corrections", [])
    memory_candidates = reflection.get("memory_candidate_refs", [])

    if reflection.get("prior_reflection_ref") == reflection_id:
        fail(f"{filename}: reflection cannot reference itself as prior_reflection_ref")

    if status == "completed":
        if not evidence_refs:
            fail(f"{filename}: completed reflection requires evidence")
        if not isinstance(observation, dict) or not observation.get("failure_or_risk"):
            fail(f"{filename}: completed reflection requires an observed failure or risk")
        if not corrections:
            fail(f"{filename}: completed reflection requires at least one proposed correction")
    elif status in {"abstained", "insufficient_evidence"}:
        if corrections:
            fail(f"{filename}: {status} reflection cannot emit corrective actions")
        if reflection.get("resulting_action_ref") is not None:
            fail(f"{filename}: {status} reflection cannot link a resulting action")
        if reflection.get("next_attempt_ref") is not None:
            fail(f"{filename}: {status} reflection cannot link a corrective attempt")
        if memory_candidates:
            fail(f"{filename}: {status} reflection cannot emit memory candidates")

    provider = reflection.get("provider", {})
    if isinstance(provider, dict) and provider.get("kind") == "agent" and not provider.get("connection_id"):
        fail(f"{filename}: agent-assisted reflection requires connection_id provenance")

    if memory_candidates and status != "completed":
        fail(f"{filename}: only completed reflection can emit memory candidates")

if isinstance(corrected_work_unit, dict):
    validate("work-unit", corrected_work_unit, "reflection-corrected-work-unit")
    corrective_attempts = [
        attempt
        for run in corrected_work_unit.get("runs", [])
        if isinstance(run, dict)
        for attempt in run.get("attempts", [])
        if isinstance(attempt, dict) and attempt.get("triggered_by_reflection_ref")
    ]
    if not corrective_attempts:
        fail("reflection-corrected-work-unit: expected a corrective attempt linked to reflection")
    for attempt in corrective_attempts:
        reflection_ref = attempt.get("triggered_by_reflection_ref")
        if reflection_ref not in reflection_by_id:
            fail(
                "reflection-corrected-work-unit: corrective attempt references "
                f"unknown reflection {reflection_ref}"
            )
        if attempt.get("ordinal", 0) <= 1:
            fail("reflection-corrected-work-unit: corrective attempt must follow an earlier attempt")

if isinstance(reflection_policy, dict):
    validate("reflection-policy", reflection_policy, "reflection-policy")
    rules = reflection_policy.get("rules", [])
    rule_ids = [rule.get("id") for rule in rules if isinstance(rule, dict)]
    priorities = [rule.get("priority") for rule in rules if isinstance(rule, dict)]
    if len(rule_ids) != len(set(rule_ids)):
        fail("reflection-policy: rule ids must be unique")
    if len(priorities) != len(set(priorities)):
        fail("reflection-policy: priorities must be unique for deterministic selection")
    if priorities != sorted(priorities, reverse=True):
        fail("reflection-policy: rules must be ordered by descending priority")

if isinstance(reflection_decision, dict):
    validate("reflection-trigger-decision", reflection_decision, "reflection-trigger-skip")
    if reflection_decision.get("decision") == "skip" and not reflection_decision.get("evidence_refs"):
        fail("reflection-trigger-skip: skip decisions require evidence")

failed_reflection = reflection_by_id.get("reflection:test-failure:1")
if isinstance(failed_reflection, dict) and isinstance(reflection_events, list):
    event_subjects = {
        (event.get("type"), event.get("subject", {}).get("kind"), event.get("subject", {}).get("id"))
        for event in reflection_events
        if isinstance(event, dict) and isinstance(event.get("subject"), dict)
    }

    reflection_id = failed_reflection.get("id")
    action_id = failed_reflection.get("resulting_action_ref")
    attempt_id = failed_reflection.get("next_attempt_ref")

    if ("reflection.created", "reflection", reflection_id) not in event_subjects:
        fail("reflection-correction-events: missing reflection.created event")
    if ("action.created", "action", action_id) not in event_subjects:
        fail("reflection-correction-events: missing corrective action event")
    if ("attempt.started", "attempt", attempt_id) not in event_subjects:
        fail("reflection-correction-events: missing corrective attempt start")
    if ("attempt.completed", "attempt", attempt_id) not in event_subjects:
        fail("reflection-correction-events: missing corrective attempt completion")
    if not any(event.get("type") == "test.passed" for event in reflection_events if isinstance(event, dict)):
        fail("reflection-correction-events: successful correction requires verification evidence")

if errors:
    print("Agent Work Protocol validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "Agent Work Protocol valid: "
    f"{len(validators)} schemas, "
    f"{len(events) if isinstance(events, list) else 0} base events, "
    f"{len(reflections)} reflection fixtures"
)
