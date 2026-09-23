#!/usr/bin/env python3
"""Deterministic reference analysis for an already-declared Architecture Graph v1.

This module does not inspect a repository, resolve imports, authenticate graph claims,
or enforce architecture. It consumes supplied graph JSON and task paths only.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any

ACTIVE_LIFECYCLES = {"current", "target"}
CAPABILITY_RELATION_KINDS = {"composes", "adapts", "authoritative-for"}
TICK = chr(96)


class ArchitectureAnalysisError(ValueError):
    pass


def _repo_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ArchitectureAnalysisError("invalid-path")
    if "\\" in value or value.startswith("/"):
        raise ArchitectureAnalysisError("path-must-be-relative-posix")
    path = PurePosixPath(value)
    if ".." in path.parts or "." in path.parts:
        raise ArchitectureAnalysisError("path-must-be-normalized")
    normalized = str(path)
    if normalized in {"", "."}:
        raise ArchitectureAnalysisError("invalid-path")
    return normalized.rstrip("/")


def _index(graph: dict[str, Any]) -> tuple[dict[str, dict], list[dict]]:
    if not isinstance(graph, dict):
        raise ArchitectureAnalysisError("graph-must-be-object")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ArchitectureAnalysisError("graph-nodes-edges-required")
    by_id: dict[str, dict] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str):
            raise ArchitectureAnalysisError("invalid-node")
        node_id = node["id"]
        if node_id in by_id:
            raise ArchitectureAnalysisError("duplicate-node-id")
        by_id[node_id] = node
    for edge in edges:
        if not isinstance(edge, dict):
            raise ArchitectureAnalysisError("invalid-edge")
        if edge.get("from") not in by_id or edge.get("to") not in by_id:
            raise ArchitectureAnalysisError("dangling-edge")
    return by_id, edges


def _path_matches(node_path: str, task_path: str) -> bool:
    return task_path == node_path or task_path.startswith(node_path + "/")


def _contracts_for(capability_id: str, by_id: dict[str, dict], edges: list[dict]) -> list[str]:
    return sorted(
        edge["to"]
        for edge in edges
        if edge.get("from") == capability_id
        and edge.get("kind") == "owns"
        and by_id.get(edge.get("to"), {}).get("kind") == "contract"
    )


def _surfaces_for(capability_id: str, by_id: dict[str, dict], edges: list[dict]) -> list[str]:
    return sorted(
        edge["to"]
        for edge in edges
        if edge.get("from") == capability_id
        and edge.get("kind") == "exposes"
        and by_id.get(edge.get("to"), {}).get("kind") == "surface"
    )


def _capabilities_for_node(
    node_id: str,
    by_id: dict[str, dict],
    edges: list[dict],
    visiting: set[str] | None = None,
) -> set[str]:
    node = by_id[node_id]
    if node.get("kind") == "capability":
        return {node_id}
    visiting = set() if visiting is None else set(visiting)
    if node_id in visiting:
        return set()
    visiting.add(node_id)
    result: set[str] = set()
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        kind = edge.get("kind")
        if source == node_id and kind in CAPABILITY_RELATION_KINDS:
            if by_id[target].get("kind") == "capability":
                result.add(target)
        if source == node_id and kind == "implements":
            if by_id[target].get("kind") == "contract":
                result.update(_capabilities_for_node(target, by_id, edges, visiting))
        if target == node_id and kind in {"owns", "exposes", "persists-to"}:
            if by_id[source].get("kind") == "capability":
                result.add(source)
        if node.get("kind") == "contract" and target == node_id and kind == "owns":
            if by_id[source].get("kind") == "capability":
                result.add(source)
    return result


def resolve_task_context(graph: dict[str, Any], paths: list[str]) -> dict[str, Any]:
    """Resolve explicit task paths to declared capabilities and owner context."""
    by_id, edges = _index(graph)
    if not isinstance(paths, list) or not paths:
        raise ArchitectureAnalysisError("task-paths-required")
    normalized_paths = [_repo_path(path) for path in paths]
    path_capabilities: dict[str, list[str]] = {}
    path_nodes: dict[str, list[str]] = {}

    for task_path in normalized_paths:
        matching: list[tuple[int, str]] = []
        for node_id, node in by_id.items():
            raw = node.get("path")
            if not isinstance(raw, str):
                continue
            node_path = _repo_path(raw)
            if _path_matches(node_path, task_path):
                matching.append((len(node_path), node_id))
        if not matching:
            path_nodes[task_path] = []
            path_capabilities[task_path] = []
            continue
        most_specific = max(length for length, _ in matching)
        selected_nodes = sorted(
            node_id for length, node_id in matching if length == most_specific
        )
        path_nodes[task_path] = selected_nodes
        capabilities: set[str] = set()
        for node_id in selected_nodes:
            capabilities.update(_capabilities_for_node(node_id, by_id, edges))
        path_capabilities[task_path] = sorted(capabilities)

    matched_paths_by_capability: dict[str, set[str]] = {}
    for task_path, capability_ids in path_capabilities.items():
        for capability_id in capability_ids:
            matched_paths_by_capability.setdefault(capability_id, set()).add(task_path)

    capabilities_output: list[dict[str, Any]] = []
    for capability_id in sorted(matched_paths_by_capability):
        capability = by_id[capability_id]
        capabilities_output.append(
            {
                "id": capability_id,
                "name": capability.get("name"),
                "owner_path": capability.get("path"),
                "matched_paths": sorted(matched_paths_by_capability[capability_id]),
                "contract_ids": _contracts_for(capability_id, by_id, edges),
                "surface_ids": _surfaces_for(capability_id, by_id, edges),
            }
        )

    ambiguous = [
        {"path": path, "capability_ids": ids}
        for path, ids in sorted(path_capabilities.items())
        if len(ids) > 1
    ]
    unresolved = sorted(path for path, ids in path_capabilities.items() if not ids)
    return {
        "paths": normalized_paths,
        "capabilities": capabilities_output,
        "ambiguous_paths": ambiguous,
        "unresolved_paths": unresolved,
        "matched_node_ids": sorted(
            {node_id for nodes in path_nodes.values() for node_id in nodes}
        ),
        "complete": not ambiguous and not unresolved,
    }


def _normalized_capability_identity(node: dict[str, Any]) -> tuple[str, str]:
    metadata = node.get("metadata")
    if isinstance(metadata, dict):
        key = metadata.get("capability_key")
        if isinstance(key, str) and key.strip():
            return key.strip().casefold(), "metadata.capability_key"
    name = node.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ArchitectureAnalysisError("capability-name-required")
    return re.sub(r"\s+", " ", name.strip()).casefold(), "normalized-name"


def duplicate_capability_candidates(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Return review-required duplicate candidates, never automatic violations."""
    by_id, edges = _index(graph)
    grouped: dict[str, list[tuple[str, str]]] = {}
    for node_id, node in by_id.items():
        if node.get("kind") != "capability":
            continue
        if node.get("lifecycle") not in ACTIVE_LIFECYCLES:
            continue
        identity, source = _normalized_capability_identity(node)
        grouped.setdefault(identity, []).append((node_id, source))

    result: list[dict[str, Any]] = []
    for identity, members in sorted(grouped.items()):
        if len(members) < 2:
            continue
        capability_ids = sorted(node_id for node_id, _ in members)
        paths = sorted(
            {
                by_id[node_id]["path"]
                for node_id in capability_ids
                if isinstance(by_id[node_id].get("path"), str)
            }
        )
        if len(paths) < 2:
            continue
        sources = {source for _, source in members}
        surface_ids = sorted(
            {
                surface_id
                for node_id in capability_ids
                for surface_id in _surfaces_for(node_id, by_id, edges)
            }
        )
        result.append(
            {
                "identity": identity,
                "identity_source": (
                    "metadata.capability_key"
                    if sources == {"metadata.capability_key"}
                    else "normalized-name"
                ),
                "capability_ids": capability_ids,
                "paths": paths,
                "surface_ids": surface_ids,
                "status": "review_required",
                "reason": (
                    "Multiple active capability nodes share one declared/logical "
                    "identity at different paths. This is a duplicate candidate, "
                    "not proof that behavior is duplicated."
                ),
            }
        )
    return result


def render_markdown(graph: dict[str, Any]) -> str:
    by_id, edges = _index(graph)
    project = graph.get("project", {})
    project_id = project.get("id", "unknown")
    lines = [
        f"# Architecture Summary — {project_id}",
        "",
        f"- Graph state: {TICK}{graph.get('graph_state')}{TICK}",
        f"- Nodes: {len(by_id)}",
        f"- Edges: {len(edges)}",
        "",
        "## Capabilities",
        "",
    ]
    capabilities = sorted(
        (
            (node_id, node)
            for node_id, node in by_id.items()
            if node.get("kind") == "capability"
        ),
        key=lambda item: item[0],
    )
    if not capabilities:
        lines.append("- None declared.")
    for node_id, node in capabilities:
        path = node.get("path")
        path_text = f"{TICK}{path}{TICK}" if isinstance(path, str) else "no path"
        lines.append(f"- {TICK}{node_id}{TICK} — {node.get('name')} — {path_text}")
        dependencies = sorted(
            edge["to"]
            for edge in edges
            if edge.get("from") == node_id and edge.get("kind") == "depends-on"
        )
        contracts = _contracts_for(node_id, by_id, edges)
        surfaces = _surfaces_for(node_id, by_id, edges)
        lines.append(
            "  - Depends on: "
            + (", ".join(f"{TICK}{item}{TICK}" for item in dependencies) or "none")
        )
        lines.append(
            "  - Contracts: "
            + (", ".join(f"{TICK}{item}{TICK}" for item in contracts) or "none")
        )
        lines.append(
            "  - Surfaces: "
            + (", ".join(f"{TICK}{item}{TICK}" for item in surfaces) or "none")
        )

    lines.extend(["", "## Constraints", ""])
    constraints = sorted(graph.get("constraints", []), key=lambda item: item.get("id", ""))
    if not constraints:
        lines.append("- None declared.")
    for constraint in constraints:
        lines.append(
            f"- {TICK}{constraint.get('id')}{TICK} — {constraint.get('kind')} — "
            f"{constraint.get('status')} — "
            f"{TICK}{constraint.get('subject')}{TICK} → {TICK}{constraint.get('target')}{TICK}"
        )

    coverage = graph.get("coverage", {})
    lines.extend(
        [
            "",
            "## Coverage",
            "",
            f"- Declared nodes: {coverage.get('nodes_declared')}",
            f"- Declared edges: {coverage.get('edges_declared')}",
            f"- Checked paths: {coverage.get('paths_checked')}",
            f"- Complete: {str(bool(coverage.get('complete'))).lower()}",
            "",
            "## Not checked",
            "",
        ]
    )
    not_checked = graph.get("not_checked", [])
    if not not_checked:
        lines.append("- None declared.")
    else:
        lines.extend(f"- {item}" for item in not_checked)
    return "\n".join(lines) + "\n"


def check_markdown(graph: dict[str, Any], markdown: str) -> bool:
    return isinstance(markdown, str) and markdown == render_markdown(graph)


def analyze(graph: dict[str, Any], paths: list[str]) -> dict[str, Any]:
    summary = render_markdown(graph)
    return {
        "format_version": 1,
        "kind": "architecture-analysis",
        "project_id": graph.get("project", {}).get("id"),
        "graph_state": graph.get("graph_state"),
        "task_context": resolve_task_context(graph, paths),
        "duplicate_capability_candidates": duplicate_capability_candidates(graph),
        "summary": {
            "sha256": "sha256:" + hashlib.sha256(summary.encode("utf-8")).hexdigest(),
            "bytes": len(summary.encode("utf-8")),
        },
        "not_checked": [
            "Repository path existence and import conformance are not inspected.",
            "Duplicate-capability candidates require review; equal declared identity is not proof of duplicated behavior.",
        ],
    }



def derive_guardrail_plan(graph: dict[str, Any]) -> dict[str, Any]:
    by_id, _ = _index(graph)
    entries: list[dict[str, Any]] = []
    for constraint in sorted(graph.get("constraints", []), key=lambda item: item.get("id", "")):
        if constraint.get("kind") not in {"allowed-dependency", "forbidden-dependency"}:
            continue
        subject_id = constraint.get("subject")
        target_id = constraint.get("target")
        subject = by_id.get(subject_id, {})
        target = by_id.get(target_id, {})
        subject_path = subject.get("path") if isinstance(subject.get("path"), str) else None
        target_path = target.get("path") if isinstance(target.get("path"), str) else None
        reasons: list[str] = []
        if subject_path is None:
            reasons.append("subject-path-missing")
        if target_path is None:
            reasons.append("target-path-missing")
        entries.append(
            {
                "constraint_id": constraint.get("id"),
                "effect": "allow" if constraint.get("kind") == "allowed-dependency" else "forbid",
                "subject_id": subject_id,
                "target_id": target_id,
                "subject_path": subject_path,
                "target_path": target_path,
                "source_status": constraint.get("status"),
                "plan_status": "unresolved" if reasons else "ready",
                "unresolved_reasons": reasons,
                "enforcement_claim": False,
            }
        )
    return {
        "entries": entries,
        "ready_count": sum(item["plan_status"] == "ready" for item in entries),
        "unresolved_count": sum(item["plan_status"] == "unresolved" for item in entries),
        "enforcement_claim": False,
    }


def surface_inventory(graph: dict[str, Any]) -> list[dict[str, Any]]:
    by_id, edges = _index(graph)
    result: list[dict[str, Any]] = []
    for node_id, node in sorted(by_id.items()):
        if node.get("kind") != "capability":
            continue
        surfaces = _surfaces_for(node_id, by_id, edges)
        result.append(
            {
                "capability_id": node_id,
                "surface_ids": surfaces,
                "status": "exposed" if surfaces else "internal_or_unexposed",
            }
        )
    return result


def _mermaid_id(node_id: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", node_id)


def _mermaid_label(value: Any) -> str:
    text = str(value).replace('"', "'")
    return text.replace("\n", " ")


def render_mermaid(graph: dict[str, Any]) -> str:
    by_id, edges = _index(graph)
    lines = ["flowchart LR"]
    for node_id, node in sorted(by_id.items()):
        label = _mermaid_label(node.get("name"))
        kind = _mermaid_label(node.get("kind"))
        lines.append(f'  {_mermaid_id(node_id)}["{label}<br/>{kind}"]')
    for edge in sorted(
        edges,
        key=lambda item: (item.get("from", ""), item.get("kind", ""), item.get("to", "")),
    ):
        lines.append(
            f"  {_mermaid_id(edge['from'])} -->|{edge['kind']}| {_mermaid_id(edge['to'])}"
        )
    return "\n".join(lines) + "\n"


def check_mermaid(graph: dict[str, Any], mermaid: str) -> bool:
    return isinstance(mermaid, str) and mermaid == render_mermaid(graph)


def derive_graph_outputs(graph: dict[str, Any]) -> dict[str, Any]:
    mermaid = render_mermaid(graph)
    return {
        "format_version": 1,
        "kind": "architecture-derivatives",
        "project_id": graph.get("project", {}).get("id"),
        "graph_state": graph.get("graph_state"),
        "guardrail_plan": derive_guardrail_plan(graph),
        "surface_inventory": surface_inventory(graph),
        "diagram": {
            "format": "mermaid",
            "sha256": "sha256:" + hashlib.sha256(mermaid.encode("utf-8")).hexdigest(),
            "bytes": len(mermaid.encode("utf-8")),
        },
        "not_checked": [
            "Guardrail entries are plans derived from declared paths; no source imports were inspected or enforced.",
            "Surface inventory is descriptive and does not require every capability to be externally exposed.",
        ],
    }


def _edge_signature(edge: dict[str, Any]) -> str:
    return f"{edge.get('from')}|{edge.get('kind')}|{edge.get('to')}"


def _entity_changes(
    before_items: list[dict[str, Any]],
    after_items: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> dict[str, Any]:
    before = {
        item["id"]: item
        for item in before_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    after = {
        item["id"]: item
        for item in after_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    changed: list[dict[str, Any]] = []
    for item_id in sorted(set(before) & set(after)):
        differences = []
        for field in fields:
            left = before[item_id].get(field)
            right = after[item_id].get(field)
            if left != right:
                differences.append({"field": field, "before": left, "after": right})
        if differences:
            changed.append({"id": item_id, "fields": differences})
    return {
        "added_ids": sorted(set(after) - set(before)),
        "removed_ids": sorted(set(before) - set(after)),
        "changed": changed,
    }


def compare_graphs(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    _index(before)
    _index(after)
    before_project = before.get("project", {}).get("id")
    after_project = after.get("project", {}).get("id")
    if before_project != after_project:
        raise ArchitectureAnalysisError("project-id-mismatch")

    before_edges = {_edge_signature(edge) for edge in before.get("edges", [])}
    after_edges = {_edge_signature(edge) for edge in after.get("edges", [])}
    node_fields = ("kind", "name", "lifecycle", "path", "description", "metadata")
    constraint_fields = (
        "kind",
        "subject",
        "target",
        "status",
        "mechanism",
        "evidence_refs",
        "description",
    )
    before_coverage = before.get("coverage", {})
    after_coverage = after.get("coverage", {})
    before_not_checked = set(before.get("not_checked", []))
    after_not_checked = set(after.get("not_checked", []))
    return {
        "format_version": 1,
        "kind": "architecture-drift",
        "project_id": before_project,
        "before_state": before.get("graph_state"),
        "after_state": after.get("graph_state"),
        "node_changes": _entity_changes(before.get("nodes", []), after.get("nodes", []), node_fields),
        "edge_changes": {
            "added": sorted(after_edges - before_edges),
            "removed": sorted(before_edges - after_edges),
        },
        "constraint_changes": _entity_changes(
            before.get("constraints", []),
            after.get("constraints", []),
            constraint_fields,
        ),
        "coverage_changed": before_coverage != after_coverage,
        "coverage_before": before_coverage,
        "coverage_after": after_coverage,
        "not_checked_added": sorted(after_not_checked - before_not_checked),
        "not_checked_removed": sorted(before_not_checked - after_not_checked),
    }


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
