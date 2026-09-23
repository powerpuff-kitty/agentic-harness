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
    "work-evaluation": WORK / "evaluation.v1.schema.json",
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
evaluation = load(FIXTURES / "evaluation.v1.json")
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


def connection_v2_semantic_errors(value) -> list[str]:
    problems: list[str] = []
    if not isinstance(value, list):
        return ["expected an array of AgentConnection v2 records"]

    validator = validators.get("agent-connection-v2")
    by_id: dict[str, dict] = {}
    capability_for_permission = {
        "read": "read_repo",
        "write": "write_repo",
        "execute": "execute",
        "commit": "commit",
        "create_pr": "create_pr",
    }

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
        if not isinstance(capabilities, dict):
            continue
        if capabilities.get("commit") == "supported" and capabilities.get("write_repo") != "supported":
            problems.append(f"{connection_id}: commit support requires write_repo support")
        if capabilities.get("create_pr") == "supported" and capabilities.get("commit") != "supported":
            problems.append(f"{connection_id}: create_pr support requires commit support")

        repositories = candidate.get("repositories", [])
        if isinstance(repositories, list):
            seen_repositories: set[str] = set()
            for access in repositories:
                if not isinstance(access, dict):
                    continue
                repository = access.get("repository")
                if isinstance(repository, str):
                    if repository in seen_repositories:
                        problems.append(f"{connection_id}: duplicate repository access {repository}")
                    seen_repositories.add(repository)
                permissions = access.get("permissions", {})
                if isinstance(permissions, dict):
                    for permission, capability in capability_for_permission.items():
                        if permissions.get(permission) is True and capabilities.get(capability) != "supported":
                            problems.append(
                                f"{connection_id}: repository {repository} grants {permission} without {capability} support"
                            )

        tools = candidate.get("tools", [])
        if isinstance(tools, list):
            tool_ids: set[str] = set()
            for tool in tools:
                if not isinstance(tool, dict):
                    continue
                tool_id = tool.get("id")
                if isinstance(tool_id, str):
                    if tool_id in tool_ids:
                        problems.append(f"{connection_id}: duplicate tool id {tool_id}")
                    tool_ids.add(tool_id)
            if tools and capabilities.get("tool_calls") != "supported":
                problems.append(f"{connection_id}: connected tools require tool_calls support")

        readiness = candidate.get("readiness", {})
        if isinstance(readiness, dict) and readiness.get("status") == "ready":
            if readiness.get("checked_at") is None or not readiness.get("evidence_refs"):
                problems.append(f"{connection_id}: ready status requires checked_at and evidence")

        usage = candidate.get("usage", {})
        if isinstance(usage, dict) and usage.get("status") == "observed":
            if usage.get("captured_at") is None:
                problems.append(f"{connection_id}: observed usage requires captured_at")
            if all(usage.get(field) is None for field in ("input_tokens", "output_tokens", "cost")):
                problems.append(f"{connection_id}: observed usage requires at least one measured value")

        limits = candidate.get("rate_limits", {})
        if isinstance(limits, dict) and limits.get("status") == "observed":
            if limits.get("captured_at") is None:
                problems.append(f"{connection_id}: observed rate limits require captured_at")
            if all(limits.get(field) is None for field in ("limit", "remaining", "reset_at")):
                problems.append(f"{connection_id}: observed rate limits require at least one measured value")
            limit = limits.get("limit")
            remaining = limits.get("remaining")
            if isinstance(limit, int) and isinstance(remaining, int) and remaining > limit:
                problems.append(f"{connection_id}: remaining rate limit exceeds limit")

        continuation = candidate.get("continuation", {})
        if isinstance(continuation, dict):
            support = continuation.get("support")
            capability = capabilities.get("continue_session")
            if support == "supported" and capability != "supported":
                problems.append(f"{connection_id}: continuation support requires continue_session support")
            if support == "unsupported" and capability == "supported":
                problems.append(f"{connection_id}: continuation contract contradicts continue_session support")

        auth = candidate.get("auth", {})
        if isinstance(auth, dict) and auth.get("mode") == "api_key_ref" and auth.get("credential_ref") is None:
            problems.append(f"{connection_id}: api_key_ref auth requires an opaque credential reference")

    return problems


def action_connection_eligibility_errors(actions, connections) -> list[str]:
    problems: list[str] = []
    if not isinstance(actions, list) or not isinstance(connections, list):
        return problems

    by_id = {
        item.get("id"): item
        for item in connections
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    capability_for_permission = {
        "read": "read_repo",
        "write": "write_repo",
        "execute": "execute",
        "commit": "commit",
        "create_pr": "create_pr",
    }

    for action in actions:
        if not isinstance(action, dict):
            continue
        action_id = action.get("id")
        connection_id = action.get("agent_connection_id")
        connection = by_id.get(connection_id)
        if not isinstance(connection, dict):
            problems.append(f"{action_id}: unknown agent connection {connection_id}")
            continue

        readiness = connection.get("readiness", {})
        if not isinstance(readiness, dict) or readiness.get("status") != "ready":
            problems.append(f"{action_id}: agent connection {connection_id} is not ready")

        capabilities = connection.get("capabilities", {})
        permissions = action.get("permissions", {})
        if isinstance(capabilities, dict) and isinstance(permissions, dict):
            for permission, capability in capability_for_permission.items():
                if permissions.get(permission) is True and capabilities.get(capability) != "supported":
                    problems.append(
                        f"{action_id}: requested {permission} permission is not supported by {connection_id}"
                    )

        approval = action.get("approval", {})
        if isinstance(approval, dict) and approval.get("required") is True:
            if not isinstance(capabilities, dict) or capabilities.get("approvals") != "supported":
                problems.append(f"{action_id}: approval-gated action requires approvals capability")

        if action.get("continuation") == "same_session":
            continuation = connection.get("continuation", {})
            if not isinstance(continuation, dict) or "same_session" not in continuation.get("modes", []):
                problems.append(f"{action_id}: same_session continuation is not supported by {connection_id}")

    return problems


if isinstance(connections_v2, list):
    for problem in connection_v2_semantic_errors(connections_v2):
        fail(f"agent-connections-v2:{problem}")

    if isinstance(action_lineage, list):
        for problem in action_connection_eligibility_errors(action_lineage, connections_v2):
            fail(f"action-eligibility:{problem}")

        unavailable = copy.deepcopy(connections_v2)
        unavailable[0]["readiness"]["status"] = "unavailable"
        if not any("is not ready" in item for item in action_connection_eligibility_errors(action_lineage, unavailable)):
            fail("agent-connections-v2 mutation: unavailable connection remained action-eligible")

        underpowered = copy.deepcopy(connections_v2)
        underpowered[1]["capabilities"]["write_repo"] = "unsupported"
        if not any("requested write permission" in item for item in action_connection_eligibility_errors(action_lineage, underpowered)):
            fail("agent-connections-v2 mutation: unsupported write capability remained action-eligible")

    over_scoped = copy.deepcopy(connections_v2)
    over_scoped[0]["repositories"][0]["permissions"]["write"] = True
    if not any("grants write without write_repo support" in item for item in connection_v2_semantic_errors(over_scoped)):
        fail("agent-connections-v2 mutation: repository permission exceeded capability support")

    false_ready = copy.deepcopy(connections_v2)
    false_ready[0]["readiness"]["evidence_refs"] = []
    if not any("ready status requires checked_at and evidence" in item for item in connection_v2_semantic_errors(false_ready)):
        fail("agent-connections-v2 mutation: unsupported ready claim was not rejected")


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
