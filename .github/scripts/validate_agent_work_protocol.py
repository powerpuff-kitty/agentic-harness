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
    "work-unit-v2": WORK / "work-unit.v2.schema.json",
    "work-progress": WORK / "work-progress.v1.schema.json",
    "work-lifecycle": WORK / "lifecycle.v1.schema.json",
    "work-event": WORK / "work-event.v1.schema.json",
    "work-evidence": WORK / "evidence.v1.schema.json",
    "work-artifact": WORK / "artifact.v1.schema.json",
    "work-redaction": WORK / "redaction.v1.schema.json",
    "work-evaluation": WORK / "evaluation.v1.schema.json",
    "work-evaluation-v2": WORK / "evaluation.v2.schema.json",
    "work-metric": WORK / "metric.v1.schema.json",
    "work-finding": WORK / "finding.v1.schema.json",
    "work-action": WORK / "work-action.v1.schema.json",
    "work-action-v2": WORK / "work-action.v2.schema.json",
    "agent-connection": WORK / "agent-connection.v1.schema.json",
    "agent-connection-v2": WORK / "agent-connection.v2.schema.json",
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
work_unit_v2 = load(FIXTURES / "work-unit-v2.v2.json")
work_progress = load(FIXTURES / "work-progress.v1.json")
lifecycle = load(WORK / "lifecycle.v1.json")
lifecycle_work_units = load(FIXTURES / "lifecycle-work-units.v1.json")
evaluation = load(FIXTURES / "evaluation.v1.json")
evaluations_v2 = load(FIXTURES / "evaluations.v2.json")
metrics_v1 = load(FIXTURES / "metrics.v1.json")
findings_v1 = load(FIXTURES / "findings.v1.json")
action = load(FIXTURES / "action.v1.json")
action_lineage = load(FIXTURES / "action-lineage.v2.json")
connection = load(FIXTURES / "agent-connection.v1.json")
connections_v2 = load(FIXTURES / "agent-connections.v2.json")
events = load(FIXTURES / "events.v1.json")
evidence_records = load(FIXTURES / "evidence.v1.json")
artifacts = load(FIXTURES / "artifacts.v1.json")
redactions = load(FIXTURES / "redactions.v1.json")
replay_seed = load(FIXTURES / "replay-seed-work-unit.v1.json")
replay_expected = load(FIXTURES / "replay-expected-work-unit.v1.json")
replay_events = load(FIXTURES / "replay-events.v1.json")

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

EXPECTED_WORK_STATES = {
    "proposed", "queued", "running", "validating", "completed",
    "blocked", "waiting_for_user", "waiting_for_approval", "failed", "cancelled",
}
lifecycle_transitions: dict[str, dict[str, set[str]]] = {}

if isinstance(lifecycle, dict):
    validate("work-lifecycle", lifecycle, "lifecycle")
    states = lifecycle.get("states", [])
    terminal_states_declared = set(lifecycle.get("terminal_states", []))
    if set(states) != EXPECTED_WORK_STATES:
        fail("lifecycle: states must exactly match the WorkUnit v1 state domain")
    if terminal_states_declared != {"completed", "failed", "cancelled"}:
        fail("lifecycle: terminal states must be completed, failed and cancelled")

    raw_transitions = lifecycle.get("entity_transitions", {})
    if isinstance(raw_transitions, dict):
        for entity_kind in ("work-unit", "run", "task", "attempt"):
            mapping = raw_transitions.get(entity_kind, {})
            if not isinstance(mapping, dict):
                fail(f"lifecycle: missing transition map for {entity_kind}")
                continue
            if set(mapping) != EXPECTED_WORK_STATES:
                fail(f"lifecycle: {entity_kind} transition map must cover every state")
                continue

            normalized: dict[str, set[str]] = {}
            for previous_state, next_states in mapping.items():
                if not isinstance(next_states, list):
                    fail(f"lifecycle: {entity_kind}:{previous_state} transitions must be an array")
                    continue
                normalized[previous_state] = set(next_states)
                if previous_state in terminal_states_declared and next_states:
                    fail(f"lifecycle: terminal {entity_kind} state {previous_state} cannot transition")
                if previous_state in next_states:
                    fail(f"lifecycle: {entity_kind}:{previous_state} cannot self-transition")
                unknown = set(next_states) - EXPECTED_WORK_STATES
                if unknown:
                    fail(f"lifecycle: {entity_kind}:{previous_state} has unknown targets {sorted(unknown)}")
            lifecycle_transitions[entity_kind] = normalized


def transition_allowed(entity_kind: str, previous_state: str, next_state: str) -> bool:
    return next_state in lifecycle_transitions.get(entity_kind, {}).get(previous_state, set())


if lifecycle_transitions:
    if transition_allowed("task", "completed", "running"):
        fail("lifecycle: completed task must be terminal")
    if transition_allowed("attempt", "failed", "running"):
        fail("lifecycle: failed attempt must not be resurrected; create a new attempt")
    if not transition_allowed("task", "running", "completed"):
        fail("lifecycle: running task must be able to complete")


if isinstance(lifecycle_work_units, list):
    expected_scenarios = {
        "wu:lifecycle:success": "completed",
        "wu:lifecycle:blocked": "blocked",
        "wu:lifecycle:failed": "failed",
        "wu:lifecycle:retry": "running",
    }
    observed_scenarios: dict[str, str] = {}
    for index, scenario in enumerate(lifecycle_work_units):
        validate("work-unit", scenario, f"lifecycle-work-units[{index}]")
        if isinstance(scenario, dict) and isinstance(scenario.get("id"), str):
            observed_scenarios[scenario["id"]] = scenario.get("state")
    if observed_scenarios != expected_scenarios:
        fail("lifecycle-work-units: fixtures must cover success, blocked, failed and retry states")


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

def attempt_invariant_errors(value, label: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(value, dict):
        return problems
    terminal = {"completed", "failed", "cancelled"}

    for run in value.get("runs", []):
        if not isinstance(run, dict):
            continue
        by_task: dict[str, list[dict]] = {}
        for attempt in run.get("attempts", []):
            if not isinstance(attempt, dict) or not isinstance(attempt.get("task_id"), str):
                continue
            by_task.setdefault(attempt["task_id"], []).append(attempt)

            state = attempt.get("state")
            completed_at = attempt.get("completed_at")
            if state in terminal and completed_at is None:
                problems.append(f"{label}:{attempt.get('id')}: terminal attempt requires completed_at")
            if state not in terminal and completed_at is not None:
                problems.append(f"{label}:{attempt.get('id')}: nonterminal attempt cannot have completed_at")

        for task_id, attempts in by_task.items():
            ordered = sorted(attempts, key=lambda item: item.get("ordinal", 0))
            ordinals = [item.get("ordinal") for item in ordered]
            if ordinals != list(range(1, len(ordered) + 1)):
                problems.append(f"{label}:{task_id}: attempt ordinals must be contiguous from 1")
                continue
            for previous in ordered[:-1]:
                if previous.get("state") not in {"failed", "cancelled"}:
                    problems.append(
                        f"{label}:{task_id}: retry requires prior failed/cancelled attempt, "
                        f"found {previous.get('state')}"
                    )

    return problems


for label, candidate in [
    ("replanned-work-unit", work_unit),
    ("reflection-corrected-work-unit", corrected_work_unit),
]:
    for problem in attempt_invariant_errors(candidate, label):
        fail(problem)

if isinstance(lifecycle_work_units, list):
    for index, scenario in enumerate(lifecycle_work_units):
        for problem in attempt_invariant_errors(scenario, f"lifecycle-work-units[{index}]"):
            fail(problem)

    retry_fixture = next(
        (
            item for item in lifecycle_work_units
            if isinstance(item, dict) and item.get("id") == "wu:lifecycle:retry"
        ),
        None,
    )
    if isinstance(retry_fixture, dict):
        bad_ordinal = copy.deepcopy(retry_fixture)
        bad_ordinal["runs"][0]["attempts"][1]["ordinal"] = 3
        if not any("attempt ordinals must be contiguous" in item
                   for item in attempt_invariant_errors(bad_ordinal, "retry-mutation")):
            fail("lifecycle mutation: noncontiguous retry ordinal was not rejected")

        resurrected = copy.deepcopy(retry_fixture)
        resurrected["runs"][0]["attempts"][0]["state"] = "completed"
        if not any("retry requires prior failed/cancelled attempt" in item
                   for item in attempt_invariant_errors(resurrected, "retry-mutation")):
            fail("lifecycle mutation: retry after completed attempt was not rejected")


def work_unit_v2_errors(value) -> list[str]:
    problems: list[str] = []
    validator = validators.get("work-unit-v2")
    if validator is not None:
        for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            problems.append(f"{location}: {error.message}")

    if not isinstance(value, dict):
        return problems

    runs = value.get("runs", [])
    run_ids = [run.get("id") for run in runs if isinstance(run, dict)]
    if len(run_ids) != len(set(run_ids)):
        problems.append("run ids must be unique")
    if value.get("current_run_id") is not None and value.get("current_run_id") not in set(run_ids):
        problems.append("current_run_id must reference an existing run")

    for run in runs:
        if not isinstance(run, dict):
            continue
        run_id = run.get("id")
        tasks = run.get("tasks", [])
        task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
        known = set(task_ids)
        if len(task_ids) != len(known):
            problems.append(f"{run_id}: task ids must be unique")

        dependencies: dict[str, list[str]] = {}
        parents: dict[str, list[str]] = {}
        for task in tasks:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                continue
            task_id = task["id"]
            parent = task.get("parent_id")
            if parent is not None and parent not in known:
                problems.append(f"{run_id}: {task_id} references missing parent {parent}")
            if parent == task_id:
                problems.append(f"{run_id}: {task_id} cannot parent itself")
            parents[task_id] = [parent] if isinstance(parent, str) and parent in known else []

            deps = task.get("depends_on", [])
            dependencies[task_id] = list(deps) if isinstance(deps, list) else []
            for dependency in dependencies[task_id]:
                if dependency not in known:
                    problems.append(f"{run_id}: {task_id} references missing dependency {dependency}")
                if dependency == task_id:
                    problems.append(f"{run_id}: {task_id} cannot depend on itself")

        def detect_cycle(graph: dict[str, list[str]], label: str) -> None:
            visiting: set[str] = set()
            visited: set[str] = set()

            def visit(node_id: str) -> None:
                if node_id in visited:
                    return
                if node_id in visiting:
                    problems.append(f"{run_id}: {label} graph contains a cycle at {node_id}")
                    return
                visiting.add(node_id)
                for target in graph.get(node_id, []):
                    if target in graph:
                        visit(target)
                visiting.remove(node_id)
                visited.add(node_id)

            for node_id in graph:
                visit(node_id)

        detect_cycle(dependencies, "task dependency")
        detect_cycle(parents, "task parent")

        revisions = run.get("plan_revisions", [])
        numbers = [item.get("revision") for item in revisions if isinstance(item, dict)]
        if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
            problems.append(f"{run_id}: plan revisions must be unique and monotonically increasing")
        for revision in revisions:
            if not isinstance(revision, dict):
                continue
            for task_id in revision.get("task_ids", []):
                if task_id not in known:
                    problems.append(f"{run_id}: plan revision references unknown task {task_id}")

    return problems


def derive_work_progress(value):
    if not isinstance(value, dict):
        raise ValueError("work unit must be an object")

    current_run_id = value.get("current_run_id")
    runs = [run for run in value.get("runs", []) if isinstance(run, dict)]
    run = next((item for item in runs if item.get("id") == current_run_id), None)
    if run is None:
        raise ValueError("current_run_id must reference an existing run")

    revisions = [item for item in run.get("plan_revisions", []) if isinstance(item, dict)]
    if not revisions:
        raise ValueError("current run must have at least one plan revision")
    latest = max(revisions, key=lambda item: item.get("revision", 0))

    tasks = {
        task.get("id"): task
        for task in run.get("tasks", [])
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }
    active_ids = latest.get("task_ids", [])
    if len(active_ids) != len(set(active_ids)):
        raise ValueError("latest plan task ids must be unique")
    missing = [task_id for task_id in active_ids if task_id not in tasks]
    if missing:
        raise ValueError(f"latest plan references unknown tasks: {missing}")

    states = [
        "proposed", "queued", "running", "validating", "completed",
        "blocked", "waiting_for_user", "waiting_for_approval", "failed", "cancelled",
    ]
    counts = {state: 0 for state in states}
    for task_id in active_ids:
        state = tasks[task_id].get("state")
        if state not in counts:
            raise ValueError(f"active task {task_id} has unknown state {state}")
        counts[state] += 1

    return {
        "format_version": 1,
        "kind": "work-progress",
        "work_unit_id": value.get("id"),
        "run_id": current_run_id,
        "plan_revision": latest.get("revision"),
        "basis": "latest-plan-task-state-counts",
        "active_task_count": len(active_ids),
        "state_counts": counts,
    }


if isinstance(work_unit_v2, dict):
    for problem in work_unit_v2_errors(work_unit_v2):
        fail(f"work-unit-v2:{problem}")

    missing_input = copy.deepcopy(work_unit_v2)
    missing_input["runs"][0].pop("input_revision", None)
    if not any("'input_revision' is a required property" in item
               for item in work_unit_v2_errors(missing_input)):
        fail("work-unit-v2 mutation: missing immutable input identity was not rejected")

    missing_session = copy.deepcopy(work_unit_v2)
    missing_session["runs"][0].pop("session_ref", None)
    if not any("'session_ref' is a required property" in item
               for item in work_unit_v2_errors(missing_session)):
        fail("work-unit-v2 mutation: missing session reference field was not rejected")

    parent_cycle = copy.deepcopy(work_unit_v2)
    parent_cycle["runs"][0]["tasks"][0]["parent_id"] = "task:verify"
    parent_cycle["runs"][0]["tasks"][2]["parent_id"] = "task:inspect"
    if not any("task parent graph contains a cycle" in item
               for item in work_unit_v2_errors(parent_cycle)):
        fail("work-unit-v2 mutation: task parent cycle was not rejected")

if isinstance(work_progress, dict):
    validate("work-progress", work_progress, "work-progress")
    if isinstance(work_unit_v2, dict):
        try:
            derived_progress = derive_work_progress(work_unit_v2)
        except ValueError as exc:
            fail(f"work-progress: derivation failed: {exc}")
        else:
            if derived_progress != work_progress:
                fail("work-progress: fixture does not equal deterministic latest-plan derivation")
            if derived_progress["active_task_count"] != sum(derived_progress["state_counts"].values()):
                fail("work-progress: active task count must equal state-count sum")

    percentage = copy.deepcopy(work_progress)
    percentage["percentage"] = 50
    progress_validator = validators.get("work-progress")
    if progress_validator is not None and progress_validator.is_valid(percentage):
        fail("work-progress mutation: invented percentage was accepted")


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

def action_v2_semantic_errors(value) -> list[str]:
    problems: list[str] = []
    if not isinstance(value, list):
        return ["expected an array of WorkAction v2 records"]

    validator = validators.get("work-action-v2")
    by_id: dict[str, dict] = {}
    read_only_intents = {
        "inspect", "audit", "evaluate", "reflect", "reassess",
        "validate", "compare_requirements", "review",
    }

    for index, candidate in enumerate(value):
        if validator is not None:
            for error in sorted(validator.iter_errors(candidate), key=lambda item: list(item.path)):
                location = ".".join(str(part) for part in error.path) or "<root>"
                problems.append(f"[{index}].{location}: {error.message}")
        if not isinstance(candidate, dict):
            continue
        action_id = candidate.get("id")
        if not isinstance(action_id, str):
            continue
        if action_id in by_id:
            problems.append(f"duplicate action id {action_id}")
        by_id[action_id] = candidate

        permissions = candidate.get("permissions", {})
        if candidate.get("intent") in read_only_intents and isinstance(permissions, dict):
            if any(permissions.get(key) for key in ("write", "commit", "create_pr")):
                problems.append(f"{action_id}: read/review intent requests write-capable permissions")

        approval = candidate.get("approval", {})
        if isinstance(approval, dict):
            if candidate.get("status") == "completed" and approval.get("required") is True:
                if approval.get("status") != "granted":
                    problems.append(f"{action_id}: completed approval-gated action requires granted approval")

    for action_id, candidate in by_id.items():
        lineage = candidate.get("lineage", {})
        if not isinstance(lineage, dict):
            continue
        parent = lineage.get("parent_action_id")
        declared_root = lineage.get("root_action_id")
        if parent is None:
            if declared_root is not None:
                problems.append(f"{action_id}: root action must have null root_action_id")
            continue
        if parent == action_id:
            problems.append(f"{action_id}: action cannot parent itself")
            continue
        if parent not in by_id:
            problems.append(f"{action_id}: unknown parent action {parent}")
            continue
        if not isinstance(declared_root, str) or declared_root not in by_id:
            problems.append(f"{action_id}: unknown root action {declared_root}")
            continue

        seen = {action_id}
        cursor = parent
        computed_root = None
        while True:
            if cursor in seen:
                problems.append(f"{action_id}: action lineage contains a cycle at {cursor}")
                break
            seen.add(cursor)
            ancestor = by_id.get(cursor)
            if not isinstance(ancestor, dict):
                break
            ancestor_lineage = ancestor.get("lineage", {})
            if not isinstance(ancestor_lineage, dict):
                break
            ancestor_parent = ancestor_lineage.get("parent_action_id")
            if ancestor_parent is None:
                computed_root = cursor
                break
            if ancestor_parent not in by_id:
                problems.append(f"{action_id}: ancestor references unknown parent {ancestor_parent}")
                break
            cursor = ancestor_parent

        if computed_root is not None and declared_root != computed_root:
            problems.append(
                f"{action_id}: declared root {declared_root} does not match computed root {computed_root}"
            )

    return problems


if isinstance(action_lineage, list):
    for problem in action_v2_semantic_errors(action_lineage):
        fail(f"action-lineage:{problem}")

    self_parent = copy.deepcopy(action_lineage)
    self_parent[-1]["lineage"]["parent_action_id"] = self_parent[-1]["id"]
    if not any("cannot parent itself" in item for item in action_v2_semantic_errors(self_parent)):
        fail("action-lineage mutation: self-parenting action was not rejected")

    wrong_root = copy.deepcopy(action_lineage)
    wrong_root[-1]["lineage"]["root_action_id"] = wrong_root[-2]["id"]
    if not any("does not match computed root" in item for item in action_v2_semantic_errors(wrong_root)):
        fail("action-lineage mutation: incorrect root lineage was not rejected")

    read_write = copy.deepcopy(action_lineage)
    read_write[0]["permissions"]["write"] = True
    if not any("write-capable permissions" in item or "False was expected" in item
               for item in action_v2_semantic_errors(read_write)):
        fail("action-lineage mutation: read-only audit gained write permission")

    missing_result = copy.deepcopy(action_lineage)
    missing_result[-1]["result"] = None
    if not any("not of type 'object'" in item for item in action_v2_semantic_errors(missing_result)):
        fail("action-lineage mutation: completed action without result was not rejected")


if isinstance(connection, dict):
    validate("agent-connection", connection, "agent-connection")
    capabilities = connection.get("capabilities", {})
    if isinstance(capabilities, dict):
        if capabilities.get("commit") and not capabilities.get("write_repo"):
            fail("agent-connection: commit capability requires write_repo")
        if capabilities.get("create_pr") and not capabilities.get("commit"):
            fail("agent-connection: create_pr capability requires commit")

def connection_v2_semantic_errors(value) -> list[str]:
    problems: list[str] = []
    if not isinstance(value, list):
        return ["expected an array of AgentConnection v2 records"]

    validator = validators.get("agent-connection-v2")
    by_id: dict[str, dict] = {}
    usable = {"supported", "requires_approval"}

    for index, candidate in enumerate(value):
        if validator is not None:
            for error in sorted(validator.iter_errors(candidate), key=lambda item: list(item.path)):
                location = ".".join(str(part) for part in error.path) or "<root>"
                problems.append(f"[{index}].{location}: {error.message}")
        if not isinstance(candidate, dict):
            continue

        connection_id = candidate.get("id")
        if not isinstance(connection_id, str):
            continue
        if connection_id in by_id:
            problems.append(f"duplicate connection id {connection_id}")
        by_id[connection_id] = candidate

        capabilities = candidate.get("capabilities", {})
        if isinstance(capabilities, dict):
            if capabilities.get("commit") in usable and capabilities.get("write_repo") not in usable:
                problems.append(f"{connection_id}: commit capability requires usable write_repo")
            if capabilities.get("create_pr") in usable and capabilities.get("commit") not in usable:
                problems.append(f"{connection_id}: create_pr capability requires usable commit")

            session = candidate.get("session", {})
            continuation = session.get("continuation") if isinstance(session, dict) else None
            continuation_capability = capabilities.get("continue_session")
            if continuation == "supported" and continuation_capability not in usable:
                problems.append(f"{connection_id}: supported session continuation lacks usable capability")
            if continuation == "unsupported" and continuation_capability in usable:
                problems.append(f"{connection_id}: continuation capability conflicts with unsupported session")

        repository_access = candidate.get("repository_access", {})
        if isinstance(repository_access, dict) and isinstance(capabilities, dict):
            scope = repository_access.get("scope")
            repositories = repository_access.get("repositories", [])
            if scope == "none" and (
                capabilities.get("read_repo") in usable or capabilities.get("write_repo") in usable
            ):
                problems.append(f"{connection_id}: repository capabilities conflict with access scope none")
            if capabilities.get("write_repo") in usable and scope == "selected":
                if not any(
                    isinstance(item, dict) and item.get("access") == "write"
                    for item in repositories
                ):
                    problems.append(f"{connection_id}: usable write_repo lacks selected write access")

        tools = candidate.get("connected_tools", [])
        if isinstance(tools, list):
            tool_ids = [item.get("id") for item in tools if isinstance(item, dict)]
            if len(tool_ids) != len(set(tool_ids)):
                problems.append(f"{connection_id}: connected tool ids must be unique")

        readiness = candidate.get("readiness", {})
        usage = candidate.get("usage", {})
        readiness_state = readiness.get("state") if isinstance(readiness, dict) else None
        usage_status = usage.get("status") if isinstance(usage, dict) else None
        if readiness_state == "rate_limited" and usage_status != "rate_limited":
            problems.append(f"{connection_id}: rate-limited readiness requires rate-limited usage evidence")

    return problems


def action_connection_eligibility(action: dict, connection: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    readiness = connection.get("readiness", {})
    if not isinstance(readiness, dict) or readiness.get("state") != "ready":
        reasons.append(f"connection-not-ready:{readiness.get('state') if isinstance(readiness, dict) else 'unknown'}")

    capabilities = connection.get("capabilities", {})
    approval = action.get("approval", {})
    approval_granted = isinstance(approval, dict) and approval.get("status") == "granted"
    permission_to_capability = {
        "read": "read_repo",
        "write": "write_repo",
        "execute": "execute",
        "commit": "commit",
        "create_pr": "create_pr",
    }
    permissions = action.get("permissions", {})
    if isinstance(permissions, dict) and isinstance(capabilities, dict):
        for permission, capability in permission_to_capability.items():
            if not permissions.get(permission):
                continue
            state = capabilities.get(capability)
            if state == "supported":
                continue
            if state == "requires_approval" and approval_granted:
                continue
            reasons.append(f"capability:{capability}:{state or 'unknown'}")

    repository_access = connection.get("repository_access", {})
    if isinstance(permissions, dict) and isinstance(repository_access, dict):
        scope = repository_access.get("scope")
        repositories = repository_access.get("repositories", [])
        if (permissions.get("read") or permissions.get("write")) and scope == "none":
            reasons.append("repository-access:none")
        if permissions.get("write") and scope == "selected":
            if not any(
                isinstance(item, dict) and item.get("access") == "write"
                for item in repositories
            ):
                reasons.append("repository-access:no-selected-write")

    return (not reasons, reasons)


if isinstance(connections_v2, list):
    for problem in connection_v2_semantic_errors(connections_v2):
        fail(f"agent-connections-v2:{problem}")

    connections_by_id = {
        item.get("id"): item
        for item in connections_v2
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if isinstance(action_lineage, list):
        for candidate in action_lineage:
            if not isinstance(candidate, dict):
                continue
            connection_id = candidate.get("agent_connection_id")
            selected = connections_by_id.get(connection_id)
            if selected is None:
                fail(f"agent-connections-v2: action {candidate.get('id')} references unknown connection {connection_id}")
                continue
            eligible, reasons = action_connection_eligibility(candidate, selected)
            if not eligible:
                fail(
                    f"agent-connections-v2: action {candidate.get('id')} is not eligible for "
                    f"{connection_id}: {', '.join(reasons)}"
                )

    bad_commit = copy.deepcopy(connections_v2)
    bad_commit[0]["capabilities"]["commit"] = "supported"
    if not any("commit capability requires usable write_repo" in item
               for item in connection_v2_semantic_errors(bad_commit)):
        fail("agent-connections-v2 mutation: commit without write capability was not rejected")

    leaked_secret = copy.deepcopy(connections_v2)
    leaked_secret[-1]["auth"]["api_key_value"] = "must-not-be-stored"
    if not any("Additional properties are not allowed" in item
               for item in connection_v2_semantic_errors(leaked_secret)):
        fail("agent-connections-v2 mutation: raw credential-like field was not rejected")

    if isinstance(action_lineage, list) and action_lineage:
        unavailable = copy.deepcopy(action_lineage[0])
        unavailable["agent_connection_id"] = "agent:api-advisor"
        eligible, reasons = action_connection_eligibility(
            unavailable, connections_by_id["agent:api-advisor"]
        )
        if eligible or not reasons:
            fail("agent-connections-v2 mutation: unavailable API advisor was incorrectly eligible")


def evaluation_bundle_errors(evaluations, metrics, findings) -> list[str]:
    problems: list[str] = []
    if not isinstance(evaluations, list) or not isinstance(metrics, list) or not isinstance(findings, list):
        return ["evaluation bundle fixtures must all be arrays"]

    evaluation_validator = validators.get("work-evaluation-v2")
    metric_validator = validators.get("work-metric")
    finding_validator = validators.get("work-finding")

    evaluation_by_id: dict[str, dict] = {}
    metric_by_id: dict[str, dict] = {}
    finding_by_id: dict[str, dict] = {}

    for label, values, validator, target in (
        ("evaluation", evaluations, evaluation_validator, evaluation_by_id),
        ("metric", metrics, metric_validator, metric_by_id),
        ("finding", findings, finding_validator, finding_by_id),
    ):
        for index, value in enumerate(values):
            if validator is not None:
                for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
                    location = ".".join(str(part) for part in error.path) or "<root>"
                    problems.append(f"{label}[{index}].{location}: {error.message}")
            if not isinstance(value, dict) or not isinstance(value.get("id"), str):
                continue
            identifier = value["id"]
            if identifier in target:
                problems.append(f"duplicate {label} id {identifier}")
            target[identifier] = value

    non_measured = {"unknown", "not_checked", "blocked", "not_applicable"}
    for metric_id, metric in metric_by_id.items():
        measurement = metric.get("measurement", {})
        if not isinstance(measurement, dict):
            continue
        populated = any(
            measurement.get(key) is not None
            for key in ("value", "normalized_score", "grade")
        )
        if metric.get("status") in non_measured and populated:
            problems.append(f"{metric_id}: non-measured status carries a measurement")
        if populated:
            method = metric.get("method", {})
            if not isinstance(method, dict) or not method.get("description"):
                problems.append(f"{metric_id}: measurement requires an explicit method")
            if not metric.get("input_refs"):
                problems.append(f"{metric_id}: measurement requires input refs")
            if not metric.get("evidence_refs"):
                problems.append(f"{metric_id}: measurement requires evidence refs")

    confidence_dimensions = {
        "evidence_completeness", "evaluator_confidence", "completion_confidence"
    }
    for evaluation_id, evaluation_record in evaluation_by_id.items():
        run_id = evaluation_record.get("run_id")
        implementer = evaluation_record.get("implementer", {})
        evaluator = evaluation_record.get("evaluator", {})
        if isinstance(implementer, dict):
            if implementer.get("run_id") != run_id:
                problems.append(f"{evaluation_id}: implementer run does not match evaluation run")
        if isinstance(implementer, dict) and isinstance(evaluator, dict):
            implementer_connection = implementer.get("connection_id")
            evaluator_connection = evaluator.get("connection_id")
            if (
                evaluator.get("kind") == "agent"
                and evaluator_connection is not None
                and evaluator_connection == implementer_connection
            ):
                problems.append(f"{evaluation_id}: evaluator identity must remain distinct from implementer")

        metric_refs = evaluation_record.get("metric_refs", [])
        confidence_refs = evaluation_record.get("confidence_metric_refs", [])
        finding_refs = evaluation_record.get("finding_refs", [])

        for metric_ref in metric_refs:
            metric = metric_by_id.get(metric_ref)
            if metric is None:
                problems.append(f"{evaluation_id}: unknown metric ref {metric_ref}")
            elif metric.get("evaluation_id") != evaluation_id:
                problems.append(f"{evaluation_id}: metric {metric_ref} belongs to another evaluation")

        for confidence_ref in confidence_refs:
            metric = metric_by_id.get(confidence_ref)
            if confidence_ref not in metric_refs:
                problems.append(f"{evaluation_id}: confidence metric {confidence_ref} is not in metric_refs")
            if isinstance(metric, dict) and metric.get("dimension") not in confidence_dimensions:
                problems.append(f"{evaluation_id}: {confidence_ref} is not a confidence/evidence metric")

        for finding_ref in finding_refs:
            finding = finding_by_id.get(finding_ref)
            if finding is None:
                problems.append(f"{evaluation_id}: unknown finding ref {finding_ref}")
            elif finding.get("evaluation_id") != evaluation_id:
                problems.append(f"{evaluation_id}: finding {finding_ref} belongs to another evaluation")

    for metric_id, metric in metric_by_id.items():
        evaluation_id = metric.get("evaluation_id")
        owner = evaluation_by_id.get(evaluation_id)
        if owner is None:
            problems.append(f"{metric_id}: references unknown evaluation {evaluation_id}")
        elif metric_id not in owner.get("metric_refs", []):
            problems.append(f"{metric_id}: owning evaluation does not reference metric")

    for finding_id, finding in finding_by_id.items():
        evaluation_id = finding.get("evaluation_id")
        owner = evaluation_by_id.get(evaluation_id)
        if owner is None:
            problems.append(f"{finding_id}: references unknown evaluation {evaluation_id}")
        elif finding_id not in owner.get("finding_refs", []):
            problems.append(f"{finding_id}: owning evaluation does not reference finding")

        prior_finding = finding.get("prior_finding_id")
        if prior_finding is not None:
            if prior_finding == finding_id:
                problems.append(f"{finding_id}: finding cannot supersede itself")
            elif prior_finding not in finding_by_id:
                problems.append(f"{finding_id}: unknown prior finding {prior_finding}")

    for evaluation_id, evaluation_record in evaluation_by_id.items():
        lineage = evaluation_record.get("lineage", {})
        if not isinstance(lineage, dict):
            continue
        prior = lineage.get("prior_evaluation_id")
        if prior is None:
            continue
        if prior == evaluation_id:
            problems.append(f"{evaluation_id}: evaluation cannot reassess itself")
            continue
        prior_record = evaluation_by_id.get(prior)
        if prior_record is None:
            problems.append(f"{evaluation_id}: unknown prior evaluation {prior}")
            continue
        if prior_record.get("work_unit_id") != evaluation_record.get("work_unit_id"):
            problems.append(f"{evaluation_id}: reassessment crosses work units")

        seen = {evaluation_id}
        cursor = prior
        while cursor is not None:
            if cursor in seen:
                problems.append(f"{evaluation_id}: evaluation lineage contains a cycle at {cursor}")
                break
            seen.add(cursor)
            ancestor = evaluation_by_id.get(cursor)
            if not isinstance(ancestor, dict):
                break
            ancestor_lineage = ancestor.get("lineage", {})
            cursor = ancestor_lineage.get("prior_evaluation_id") if isinstance(ancestor_lineage, dict) else None

    run_evaluators: dict[tuple[str, str], set[tuple[str, object, str]]] = {}
    for evaluation_record in evaluations:
        if not isinstance(evaluation_record, dict):
            continue
        evaluator = evaluation_record.get("evaluator", {})
        if not isinstance(evaluator, dict):
            continue
        key = (evaluation_record.get("work_unit_id"), evaluation_record.get("run_id"))
        identity = (evaluator.get("kind"), evaluator.get("connection_id"), evaluator.get("name"))
        run_evaluators.setdefault(key, set()).add(identity)
    if not any(len(identities) >= 2 for identities in run_evaluators.values()):
        problems.append("fixture must demonstrate independent evaluators on the same run")

    if not any(
        isinstance(item, dict)
        and isinstance(item.get("lineage"), dict)
        and item["lineage"].get("prior_evaluation_id") is not None
        for item in evaluations
    ):
        problems.append("fixture must demonstrate immutable reassessment lineage")

    return problems


if isinstance(evaluations_v2, list) and isinstance(metrics_v1, list) and isinstance(findings_v1, list):
    for problem in evaluation_bundle_errors(evaluations_v2, metrics_v1, findings_v1):
        fail(f"evaluation-bundle:{problem}")

    unknown_score = copy.deepcopy(metrics_v1)
    unknown_score[1]["measurement"]["normalized_score"] = 1.0
    if not any("non-measured status carries a measurement" in item or "None was expected" in item
               for item in evaluation_bundle_errors(evaluations_v2, unknown_score, findings_v1)):
        fail("evaluation-bundle mutation: not-checked metric accepted a score")

    no_evidence = copy.deepcopy(metrics_v1)
    no_evidence[0]["evidence_refs"] = []
    if not any("measurement requires evidence refs" in item
               for item in evaluation_bundle_errors(evaluations_v2, no_evidence, findings_v1)):
        fail("evaluation-bundle mutation: scored metric without evidence was not rejected")

    self_reassessment = copy.deepcopy(evaluations_v2)
    self_reassessment[-1]["lineage"]["prior_evaluation_id"] = self_reassessment[-1]["id"]
    if not any("evaluation cannot reassess itself" in item
               for item in evaluation_bundle_errors(self_reassessment, metrics_v1, findings_v1)):
        fail("evaluation-bundle mutation: self-reassessment was not rejected")

    same_evaluator = copy.deepcopy(evaluations_v2)
    same_evaluator[1]["evaluator"]["connection_id"] = same_evaluator[1]["implementer"]["connection_id"]
    if not any("evaluator identity must remain distinct" in item
               for item in evaluation_bundle_errors(same_evaluator, metrics_v1, findings_v1)):
        fail("evaluation-bundle mutation: implementer/evaluator identity collapse was not rejected")

    ineligible_remediation = copy.deepcopy(findings_v1)
    ineligible_remediation[-1]["remediation"]["action_intents"] = ["remediate"]
    if not any("is expected to be empty" in item or "is too long" in item
               for item in evaluation_bundle_errors(evaluations_v2, metrics_v1, ineligible_remediation)):
        fail("evaluation-bundle mutation: ineligible remediation exposed an action")


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
            previous_state = delta.get("previous_state")
            next_state = delta.get("next_state")
            if not transition_allowed(entity_kind, previous_state, next_state):
                fail(
                    f"replay-events[{index}]: invalid {entity_kind} lifecycle transition "
                    f"{previous_state} -> {next_state}"
                )
                continue
            target["state"] = next_state
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
