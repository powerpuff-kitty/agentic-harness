#!/usr/bin/env python3
from __future__ import annotations

import copy
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
    "work-evidence": WORK / "evidence.v1.schema.json",
    "work-artifact": WORK / "artifact.v1.schema.json",
    "work-redaction": WORK / "redaction.v1.schema.json",
    "work-lifecycle": WORK / "lifecycle.v1.schema.json",
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
evidence_records = load(FIXTURES / "evidence.v1.json")
artifacts = load(FIXTURES / "artifacts.v1.json")
redactions = load(FIXTURES / "redactions.v1.json")
replay_seed = load(FIXTURES / "replay-seed-work-unit.v1.json")
replay_expected = load(FIXTURES / "replay-expected-work-unit.v1.json")
replay_events = load(FIXTURES / "replay-events.v1.json")
lifecycle_policy = load(WORK / "lifecycle.v1.json")
lifecycle_work_units = load(FIXTURES / "lifecycle-work-units.v1.json")

reflection_files = [
    "reflection-failed-test.v1.json",
    "reflection-bad-assumption.v1.json",
    "reflection-insufficient-evidence.v1.json",
    "reflection-abstained.v1.json",
    "reflection-rereflection.v1.json",
]
reflections = [(name, load(FIXTURES / name)) for name in reflection_files]
reflection_policy = load(FIXTURES / "reflection-policy.v1.json")
reflection_decision = load(FIXTURES / "reflection-trigger-skip.v1.json")
reflection_events = load(FIXTURES / "reflection-correction-events.v1.json")
corrected_work_unit = load(FIXTURES / "reflection-corrected-work-unit.v1.json")

WORK_STATES = {
    "proposed", "queued", "running", "validating", "completed",
    "blocked", "waiting_for_user", "waiting_for_approval", "failed", "cancelled",
}
TRANSITIONS: dict[str, dict[str, set[str]]] = {}

if isinstance(lifecycle_policy, dict):
    validate("work-lifecycle", lifecycle_policy, "lifecycle-policy")
    if set(lifecycle_policy.get("states", [])) != WORK_STATES:
        fail("lifecycle-policy: states must enumerate the canonical Work state set exactly")

    progress = lifecycle_policy.get("progress", {})
    if isinstance(progress, dict):
        if progress.get("basis") != "latest-plan-task-state-counts":
            fail("lifecycle-policy: progress must derive from latest plan task states")
        if progress.get("persist_percentage") is not False:
            fail("lifecycle-policy: canonical state must not persist an invented progress percentage")

    entities = lifecycle_policy.get("entities", {})
    if isinstance(entities, dict):
        for entity_kind in ("work-unit", "run", "task", "attempt"):
            policy = entities.get(entity_kind)
            if not isinstance(policy, dict):
                fail(f"lifecycle-policy: missing policy for {entity_kind}")
                continue

            transition_rows = policy.get("transitions", [])
            by_from: dict[str, set[str]] = {}
            for row in transition_rows:
                if not isinstance(row, dict):
                    continue
                source = row.get("from")
                if source in by_from:
                    fail(f"lifecycle-policy:{entity_kind}: duplicate transition row for {source}")
                    continue
                targets = set(row.get("to", []))
                if source in targets:
                    fail(f"lifecycle-policy:{entity_kind}: self-transition is not allowed for {source}")
                by_from[source] = targets

            required_states = (
                {"queued", "running", "completed", "failed", "cancelled"}
                if entity_kind == "attempt"
                else WORK_STATES
            )
            if set(by_from) != required_states:
                missing = sorted(required_states - set(by_from))
                extra = sorted(set(by_from) - required_states)
                fail(
                    f"lifecycle-policy:{entity_kind}: transition rows mismatch "
                    f"(missing={missing}, extra={extra})"
                )

            terminal_states = set(policy.get("terminal_states", []))
            for terminal_state in terminal_states:
                if by_from.get(terminal_state):
                    fail(
                        f"lifecycle-policy:{entity_kind}: terminal state "
                        f"{terminal_state} must not have outgoing transitions"
                    )

            TRANSITIONS[entity_kind] = by_from


def transition_allowed(entity_kind: str, previous: str, next_state: str) -> bool:
    return next_state in TRANSITIONS.get(entity_kind, {}).get(previous, set())


def derived_progress(run: dict) -> dict:
    revisions = [
        revision
        for revision in run.get("plan_revisions", [])
        if isinstance(revision, dict)
    ]
    if not revisions:
        return {"total": 0, "by_state": {}}

    latest = max(revisions, key=lambda revision: revision.get("revision", 0))
    active_ids = set(latest.get("task_ids", []))
    by_state: dict[str, int] = {}
    total = 0
    for task in run.get("tasks", []):
        if not isinstance(task, dict) or task.get("id") not in active_ids:
            continue
        state = task.get("state")
        by_state[state] = by_state.get(state, 0) + 1
        total += 1
    return {"total": total, "by_state": by_state}


def validate_work_unit_lifecycle(value: dict, label: str) -> None:
    validate("work-unit", value, label)

    if "progress" in value or "progress_percentage" in value:
        fail(f"{label}: progress must be derived, not persisted")

    runs = [run for run in value.get("runs", []) if isinstance(run, dict)]
    run_ids = [run.get("id") for run in runs]
    if len(run_ids) != len(set(run_ids)):
        fail(f"{label}: run ids must be unique")

    current_run_id = value.get("current_run_id")
    current_run = next((run for run in runs if run.get("id") == current_run_id), None)
    if current_run_id is not None and current_run is None:
        fail(f"{label}: current_run_id must reference an existing run")

    for run in runs:
        run_id = run.get("id")
        if "progress" in run or "progress_percentage" in run:
            fail(f"{label}:{run_id}: progress must be derived from task state")

        tasks = [task for task in run.get("tasks", []) if isinstance(task, dict)]
        task_by_id = {
            task.get("id"): task
            for task in tasks
            if isinstance(task.get("id"), str)
        }
        if len(task_by_id) != len(tasks):
            fail(f"{label}:{run_id}: task ids must be unique")

        # Parent hierarchy and dependency edges are separate DAGs. Both must be acyclic.
        parent_edges: dict[str, list[str]] = {}
        dependency_edges: dict[str, list[str]] = {}
        for task_id, task in task_by_id.items():
            parent = task.get("parent_id")
            if parent is not None:
                if parent not in task_by_id:
                    fail(f"{label}:{run_id}:{task_id}: unknown parent {parent}")
                if parent == task_id:
                    fail(f"{label}:{run_id}:{task_id}: task cannot parent itself")
                parent_edges[task_id] = [parent]
            else:
                parent_edges[task_id] = []

            dependencies = list(task.get("depends_on", []))
            dependency_edges[task_id] = dependencies
            for dependency in dependencies:
                if dependency not in task_by_id:
                    fail(f"{label}:{run_id}:{task_id}: unknown dependency {dependency}")
                if dependency == task_id:
                    fail(f"{label}:{run_id}:{task_id}: task cannot depend on itself")

        def ensure_acyclic(edges: dict[str, list[str]], edge_kind: str) -> None:
            visiting: set[str] = set()
            visited: set[str] = set()

            def visit(node: str) -> None:
                if node in visited:
                    return
                if node in visiting:
                    fail(f"{label}:{run_id}: {edge_kind} graph contains a cycle at {node}")
                    return
                visiting.add(node)
                for dependency in edges.get(node, []):
                    if dependency in edges:
                        visit(dependency)
                visiting.remove(node)
                visited.add(node)

            for node in edges:
                visit(node)

        ensure_acyclic(parent_edges, "parent")
        ensure_acyclic(dependency_edges, "dependency")

        revisions = [
            revision
            for revision in run.get("plan_revisions", [])
            if isinstance(revision, dict)
        ]
        revision_numbers = [revision.get("revision") for revision in revisions]
        if revision_numbers != sorted(revision_numbers) or len(revision_numbers) != len(set(revision_numbers)):
            fail(f"{label}:{run_id}: plan revisions must append monotonically")
        for revision in revisions:
            for task_id in revision.get("task_ids", []):
                if task_id not in task_by_id:
                    fail(f"{label}:{run_id}: plan revision references unknown task {task_id}")

        latest_ids: set[str] = set()
        if revisions:
            latest_ids = set(max(revisions, key=lambda revision: revision.get("revision", 0)).get("task_ids", []))

        for task_id, task in task_by_id.items():
            if task.get("state") == "completed":
                for dependency in task.get("depends_on", []):
                    dependency_task = task_by_id.get(dependency)
                    if dependency_task is not None and dependency_task.get("state") != "completed":
                        fail(
                            f"{label}:{run_id}:{task_id}: completed task has "
                            f"non-completed dependency {dependency}"
                        )

        attempts_by_task: dict[str, list[dict]] = {}
        for attempt in run.get("attempts", []):
            if not isinstance(attempt, dict):
                continue
            task_id = attempt.get("task_id")
            attempt_id = attempt.get("id")
            if task_id not in task_by_id:
                fail(f"{label}:{run_id}:{attempt_id}: attempt references unknown task {task_id}")
                continue
            attempts_by_task.setdefault(task_id, []).append(attempt)

            state = attempt.get("state")
            started_at = attempt.get("started_at")
            completed_at = attempt.get("completed_at")
            if state == "queued" and (started_at is not None or completed_at is not None):
                fail(f"{label}:{run_id}:{attempt_id}: queued attempt cannot have timestamps")
            if state == "running" and (started_at is None or completed_at is not None):
                fail(f"{label}:{run_id}:{attempt_id}: running attempt requires start and no completion")
            if state in {"completed", "failed", "cancelled"} and (
                started_at is None or completed_at is None
            ):
                fail(f"{label}:{run_id}:{attempt_id}: terminal attempt requires start and completion")

        for task_id, attempts in attempts_by_task.items():
            attempts.sort(key=lambda attempt: attempt.get("ordinal", 0))
            ordinals = [attempt.get("ordinal") for attempt in attempts]
            expected_ordinals = list(range(1, len(attempts) + 1))
            if ordinals != expected_ordinals:
                fail(
                    f"{label}:{run_id}:{task_id}: retry ordinals must be contiguous "
                    f"from 1, found {ordinals}"
                )
            for prior in attempts[:-1]:
                if prior.get("state") not in {"failed", "cancelled"}:
                    fail(
                        f"{label}:{run_id}:{task_id}: a later retry cannot follow "
                        f"attempt {prior.get('id')} in state {prior.get('state')}"
                    )

        # The current projection can fail/block while historical tasks remain preserved.
        active_tasks = [task_by_id[task_id] for task_id in latest_ids if task_id in task_by_id]
        active_states = {task.get("state") for task in active_tasks}
        run_state = run.get("state")
        if run_state == "completed" and any(
            task.get("state") not in {"completed", "cancelled"} for task in active_tasks
        ):
            fail(f"{label}:{run_id}: completed run has unfinished active tasks")
        if run_state == "blocked" and not (
            active_states & {"blocked", "waiting_for_user", "waiting_for_approval"}
        ):
            fail(f"{label}:{run_id}: blocked run lacks an active blocking task")
        if run_state == "failed" and "failed" not in active_states:
            fail(f"{label}:{run_id}: failed run lacks an active failed task")

        progress = derived_progress(run)
        if progress["total"] != len(latest_ids):
            fail(f"{label}:{run_id}: derived progress does not cover latest plan tasks")

    if isinstance(current_run, dict):
        work_state = value.get("state")
        run_state = current_run.get("state")
        if work_state in {"completed", "blocked", "failed"} and run_state != work_state:
            fail(
                f"{label}: current run state {run_state} does not match "
                f"terminal/blocking work-unit state {work_state}"
            )


if isinstance(lifecycle_work_units, list):
    seen_lifecycle_ids: set[str] = set()
    for index, lifecycle_work_unit in enumerate(lifecycle_work_units):
        if not isinstance(lifecycle_work_unit, dict):
            fail(f"lifecycle-work-units[{index}]: expected an object")
            continue
        work_unit_id = lifecycle_work_unit.get("id")
        if work_unit_id in seen_lifecycle_ids:
            fail(f"lifecycle-work-units[{index}]: duplicate work-unit id {work_unit_id}")
        if isinstance(work_unit_id, str):
            seen_lifecycle_ids.add(work_unit_id)
        validate_work_unit_lifecycle(
            lifecycle_work_unit,
            f"lifecycle-work-units[{index}]",
        )

    required_cases = {
        "wu:lifecycle:successful",
        "wu:lifecycle:blocked",
        "wu:lifecycle:failed",
        "wu:lifecycle:retried",
    }
    if not required_cases.issubset(seen_lifecycle_ids):
        fail(
            "lifecycle-work-units: missing required lifecycle cases "
            f"{sorted(required_cases - seen_lifecycle_ids)}"
        )

for fixture_label, fixture_value in (
    ("replanned-work-unit", work_unit),
    ("reflection-corrected-work-unit", corrected_work_unit),
    ("replay-seed-work-unit", replay_seed),
    ("replay-expected-work-unit", replay_expected),
):
    if isinstance(fixture_value, dict):
        validate_work_unit_lifecycle(fixture_value, fixture_label)


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
validate_event_list(replay_events, "replay-events")

# Evidence, Artifact and Redaction records are canonical references rather than
# opaque strings. Keep their cross-record provenance deterministic.
evidence_by_id: dict[str, dict] = {}
artifact_by_id: dict[str, dict] = {}
redaction_by_id: dict[str, dict] = {}

if isinstance(replay_expected, dict):
    validate("work-unit", replay_expected, "replay-expected-work-unit")
if isinstance(replay_seed, dict):
    validate("work-unit", replay_seed, "replay-seed-work-unit")

expected_run_ids: set[str] = set()
expected_task_ids: set[str] = set()
expected_attempt_ids: set[str] = set()
if isinstance(replay_expected, dict):
    for run in replay_expected.get("runs", []):
        if not isinstance(run, dict):
            continue
        run_id = run.get("id")
        if isinstance(run_id, str):
            expected_run_ids.add(run_id)
        for task in run.get("tasks", []):
            if isinstance(task, dict) and isinstance(task.get("id"), str):
                expected_task_ids.add(task["id"])
        for attempt in run.get("attempts", []):
            if isinstance(attempt, dict) and isinstance(attempt.get("id"), str):
                expected_attempt_ids.add(attempt["id"])

if isinstance(evidence_records, list):
    for index, evidence in enumerate(evidence_records):
        validate("work-evidence", evidence, f"evidence[{index}]")
        if not isinstance(evidence, dict):
            continue

        evidence_id = evidence.get("id")
        if not isinstance(evidence_id, str):
            continue
        if evidence_id in evidence_by_id:
            fail(f"evidence[{index}]: duplicate evidence id {evidence_id}")
        evidence_by_id[evidence_id] = evidence

        if evidence.get("work_unit_id") != "wu:replay-demo":
            fail(f"{evidence_id}: evidence belongs to an unexpected work unit")

        provenance = evidence.get("provenance", {})
        if isinstance(provenance, dict):
            run_id = provenance.get("run_id")
            task_id = provenance.get("task_id")
            attempt_id = provenance.get("attempt_id")
            if isinstance(run_id, str) and run_id not in expected_run_ids:
                fail(f"{evidence_id}: provenance references unknown run {run_id}")
            if isinstance(task_id, str) and task_id not in expected_task_ids:
                fail(f"{evidence_id}: provenance references unknown task {task_id}")
            if isinstance(attempt_id, str) and attempt_id not in expected_attempt_ids:
                fail(f"{evidence_id}: provenance references unknown attempt {attempt_id}")

        evidence_kind = evidence.get("evidence_kind")
        status = evidence.get("status")
        derived_from = evidence.get("derived_from", [])
        payload = evidence.get("payload", {})

        if evidence_kind == "derived_result":
            if not derived_from:
                fail(f"{evidence_id}: derived evidence requires source evidence")
            if evidence_id in derived_from:
                fail(f"{evidence_id}: derived evidence cannot derive from itself")
        if evidence_kind == "unavailable":
            if status != "unavailable":
                fail(f"{evidence_id}: unavailable evidence requires unavailable status")
            if payload.get("mode") != "none":
                fail(f"{evidence_id}: unavailable evidence cannot carry a payload")
            if not evidence.get("unavailability_reason"):
                fail(f"{evidence_id}: unavailable evidence requires a reason")
        elif status == "unavailable":
            fail(f"{evidence_id}: non-unavailable evidence cannot use unavailable status")

if isinstance(artifacts, list):
    for index, artifact in enumerate(artifacts):
        validate("work-artifact", artifact, f"artifacts[{index}]")
        if not isinstance(artifact, dict):
            continue

        artifact_id = artifact.get("id")
        if not isinstance(artifact_id, str):
            continue
        if artifact_id in artifact_by_id:
            fail(f"artifacts[{index}]: duplicate artifact id {artifact_id}")
        artifact_by_id[artifact_id] = artifact

        if artifact.get("work_unit_id") != "wu:replay-demo":
            fail(f"{artifact_id}: artifact belongs to an unexpected work unit")

        producer = artifact.get("produced_by", {})
        if isinstance(producer, dict):
            run_id = producer.get("run_id")
            task_id = producer.get("task_id")
            attempt_id = producer.get("attempt_id")
            if isinstance(run_id, str) and run_id not in expected_run_ids:
                fail(f"{artifact_id}: producer references unknown run {run_id}")
            if isinstance(task_id, str) and task_id not in expected_task_ids:
                fail(f"{artifact_id}: producer references unknown task {task_id}")
            if isinstance(attempt_id, str) and attempt_id not in expected_attempt_ids:
                fail(f"{artifact_id}: producer references unknown attempt {attempt_id}")

        if artifact.get("artifact_kind") == "structured-snapshot":
            payload = artifact.get("payload", {})
            if payload.get("mode") != "inline_json" or not isinstance(payload.get("value"), dict):
                fail(f"{artifact_id}: replay snapshot must be inline structured JSON")

if isinstance(redactions, list):
    for index, redaction in enumerate(redactions):
        validate("work-redaction", redaction, f"redactions[{index}]")
        if not isinstance(redaction, dict):
            continue

        redaction_id = redaction.get("id")
        if not isinstance(redaction_id, str):
            continue
        if redaction_id in redaction_by_id:
            fail(f"redactions[{index}]: duplicate redaction id {redaction_id}")
        redaction_by_id[redaction_id] = redaction
        if redaction.get("work_unit_id") != "wu:replay-demo":
            fail(f"{redaction_id}: redaction belongs to an unexpected work unit")

for evidence_id, evidence in evidence_by_id.items():
    if evidence.get("evidence_kind") == "derived_result":
        for source_id in evidence.get("derived_from", []):
            if source_id not in evidence_by_id:
                fail(f"{evidence_id}: derived_from references unknown evidence {source_id}")

for record_id, record in {**evidence_by_id, **artifact_by_id}.items():
    payload = record.get("payload", {})
    if not isinstance(payload, dict) or payload.get("mode") != "redacted":
        continue
    redaction_ref = payload.get("redaction_ref")
    redaction = redaction_by_id.get(redaction_ref)
    if redaction is None:
        fail(f"{record_id}: redacted payload references unknown redaction {redaction_ref}")
    elif record_id not in redaction.get("target_refs", []):
        fail(f"{record_id}: referenced redaction does not target this record")

for redaction_id, redaction in redaction_by_id.items():
    for target_ref in redaction.get("target_refs", []):
        target = evidence_by_id.get(target_ref) or artifact_by_id.get(target_ref)
        if target is None:
            fail(f"{redaction_id}: redaction targets unknown record {target_ref}")
            continue
        payload = target.get("payload", {})
        if payload.get("mode") != "redacted" or payload.get("redaction_ref") != redaction_id:
            fail(f"{redaction_id}: target {target_ref} does not preserve the redaction reference")


def _run_by_id(projection: dict, run_id: str):
    for run in projection.get("runs", []):
        if isinstance(run, dict) and run.get("id") == run_id:
            return run
    return None


def _task_by_id(projection: dict, task_id: str):
    for run in projection.get("runs", []):
        if not isinstance(run, dict):
            continue
        for task in run.get("tasks", []):
            if isinstance(task, dict) and task.get("id") == task_id:
                return task
    return None


def _attempt_by_id(projection: dict, attempt_id: str):
    for run in projection.get("runs", []):
        if not isinstance(run, dict):
            continue
        for attempt in run.get("attempts", []):
            if isinstance(attempt, dict) and attempt.get("id") == attempt_id:
                return attempt
    return None


def _entity_for_delta(projection: dict, entity_kind: str, entity_id: str):
    if entity_kind == "work-unit":
        return projection if projection.get("id") == entity_id else None
    if entity_kind == "run":
        return _run_by_id(projection, entity_id)
    if entity_kind == "task":
        return _task_by_id(projection, entity_id)
    if entity_kind == "attempt":
        return _attempt_by_id(projection, entity_id)
    return None


def _snapshot_value(ref: str):
    artifact = artifact_by_id.get(ref)
    if artifact is None:
        fail(f"replay-events: snapshot references unknown artifact {ref}")
        return None
    payload = artifact.get("payload", {})
    if payload.get("mode") != "inline_json" or not isinstance(payload.get("value"), dict):
        fail(f"replay-events: snapshot artifact {ref} is not inline structured JSON")
        return None
    return copy.deepcopy(payload["value"])


if isinstance(replay_seed, dict) and isinstance(replay_expected, dict) and isinstance(replay_events, list):
    projection = copy.deepcopy(replay_seed)
    terminal_states = {"completed", "failed", "cancelled"}

    for index, event in enumerate(replay_events):
        if not isinstance(event, dict):
            continue

        for evidence_ref in event.get("evidence_refs", []):
            if evidence_ref not in evidence_by_id:
                fail(f"replay-events[{index}]: unknown evidence ref {evidence_ref}")
        for artifact_ref in event.get("artifact_refs", []):
            if artifact_ref not in artifact_by_id:
                fail(f"replay-events[{index}]: unknown artifact ref {artifact_ref}")
        for redaction_ref in event.get("redaction_refs", []):
            if redaction_ref not in redaction_by_id:
                fail(f"replay-events[{index}]: unknown redaction ref {redaction_ref}")

        delta = event.get("projection_delta")
        if delta is None:
            continue
        if not isinstance(delta, dict):
            fail(f"replay-events[{index}]: projection_delta must be an object")
            continue

        operation = delta.get("operation")
        entity = delta.get("entity", {})
        entity_kind = entity.get("kind") if isinstance(entity, dict) else None
        entity_id = entity.get("id") if isinstance(entity, dict) else None

        if operation == "state_transition":
            if not transition_allowed(entity_kind, delta.get("previous_state"), delta.get("next_state")):
                fail(
                    f"replay-events[{index}]: lifecycle forbids "
                    f"{entity_kind} {delta.get('previous_state')} -> {delta.get('next_state')}"
                )
                continue
            target = _entity_for_delta(projection, entity_kind, entity_id)
            if target is None:
                fail(f"replay-events[{index}]: transition target {entity_kind}:{entity_id} is missing")
                continue
            if target.get("state") != delta.get("previous_state"):
                fail(
                    f"replay-events[{index}]: expected {entity_kind}:{entity_id} "
                    f"state {delta.get('previous_state')}, found {target.get('state')}"
                )
                continue
            target["state"] = delta.get("next_state")
            if entity_kind == "attempt" and delta.get("next_state") in terminal_states:
                target["completed_at"] = event.get("occurred_at")

        elif operation == "entity_created":
            snapshot_ref = delta.get("snapshot_ref")
            snapshot = _snapshot_value(snapshot_ref)
            if snapshot is None:
                continue
            if snapshot.get("id") != entity_id:
                fail(f"replay-events[{index}]: snapshot id does not match created entity")
                continue
            run = _run_by_id(projection, event.get("run_id"))
            if run is None:
                fail(f"replay-events[{index}]: creation event references missing run")
                continue
            if entity_kind == "task":
                if _task_by_id(projection, entity_id) is not None:
                    fail(f"replay-events[{index}]: task {entity_id} already exists")
                    continue
                run.setdefault("tasks", []).append(snapshot)
            elif entity_kind == "attempt":
                if _attempt_by_id(projection, entity_id) is not None:
                    fail(f"replay-events[{index}]: attempt {entity_id} already exists")
                    continue
                if snapshot.get("task_id") not in {
                    task.get("id") for task in run.get("tasks", []) if isinstance(task, dict)
                }:
                    fail(f"replay-events[{index}]: attempt snapshot references unknown task")
                    continue
                run.setdefault("attempts", []).append(snapshot)
            else:
                fail(f"replay-events[{index}]: unsupported entity_created kind {entity_kind}")

        elif operation == "plan_revision":
            snapshot = _snapshot_value(delta.get("snapshot_ref"))
            run = _run_by_id(projection, event.get("run_id"))
            if snapshot is None or run is None:
                continue
            if snapshot.get("revision") != delta.get("plan_revision"):
                fail(f"replay-events[{index}]: plan revision number does not match snapshot")
                continue
            previous_revisions = [
                item.get("revision")
                for item in run.get("plan_revisions", [])
                if isinstance(item, dict)
            ]
            if previous_revisions and snapshot.get("revision") <= max(previous_revisions):
                fail(f"replay-events[{index}]: plan revision must append monotonically")
                continue
            run.setdefault("plan_revisions", []).append(snapshot)

        elif operation in {"append_evidence_ref", "append_artifact_ref"}:
            target = _entity_for_delta(projection, entity_kind, entity_id)
            if target is None or entity_kind != "task":
                fail(f"replay-events[{index}]: ref append requires an existing task")
                continue
            value_ref = delta.get("value_ref")
            key = "evidence_refs" if operation == "append_evidence_ref" else "artifact_refs"
            refs = target.setdefault(key, [])
            if value_ref not in refs:
                refs.append(value_ref)

        else:
            fail(f"replay-events[{index}]: unsupported projection operation {operation}")

    if projection != replay_expected:
        fail("replay-events: replayed projection does not match expected WorkUnit")


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
    prior_reflection_ref = reflection.get("prior_reflection_ref")
    if prior_reflection_ref is not None and prior_reflection_ref not in reflection_by_id:
        fail(f"{filename}: prior_reflection_ref must reference an earlier fixture reflection")

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

# Negative lifecycle checks make recovery/terminal semantics executable.
if TRANSITIONS:
    if transition_allowed("attempt", "failed", "running"):
        fail("lifecycle-policy: failed Attempt must be terminal; retry requires a new Attempt")
    if transition_allowed("task", "completed", "running"):
        fail("lifecycle-policy: completed Task must not restart in place")
    if not transition_allowed("task", "failed", "queued"):
        fail("lifecycle-policy: failed Task should support explicit recovery through queued state")

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
