#!/usr/bin/env python3
"""Inspect declared DecisionGraph v1 dependencies; never execute or authorize them.

Python 3.10+ standard library. Review only a named, non-secret local graph.
This deliberately supports a bounded subset, not general schema validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

MAX_BYTES = 65_536
MAX_NODES = 128
MAX_REDUCERS = 32
MAX_EDGES = 4096
ID = re.compile(r"[a-z0-9][a-z0-9._/-]*\Z")


class GraphError(ValueError):
    """Only fixed diagnostic codes; no input contents or rejected paths."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise GraphError(code)


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def linked(meta: os.stat_result) -> bool:
    return stat.S_ISLNK(meta.st_mode) or bool(getattr(meta, "st_file_attributes", 0) & 0x400)


def read_graph(path: Path) -> bytes:
    # Observed-path protection, not a hostile-filesystem or atomic-snapshot guarantee.
    require(".." not in path.parts, "invalid-input-path")
    absolute = Path(os.path.abspath(path))
    try:
        for parent in reversed(absolute.parents):
            meta = parent.lstat()
            require(stat.S_ISDIR(meta.st_mode) and not linked(meta), "linked-parent")
        before = absolute.lstat()
        require(stat.S_ISREG(before.st_mode) and not linked(before), "nonregular-input")
        require(before.st_size <= MAX_BYTES, "input-size-limit")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
        with os.fdopen(os.open(absolute, flags), "rb") as stream:
            opened = os.fstat(stream.fileno())
            require(stat.S_ISREG(opened.st_mode) and (before.st_dev, before.st_ino) ==
                    (opened.st_dev, opened.st_ino), "changed-input")
            data = stream.read(MAX_BYTES + 1)
            after = os.fstat(stream.fileno())
        final = absolute.lstat()
        identity = lambda m: (m.st_dev, m.st_ino, m.st_size, m.st_mtime_ns)
        require(not linked(final) and stat.S_ISREG(final.st_mode) and
                identity(before) == identity(after) == identity(final) and
                len(data) == before.st_size and len(data) <= MAX_BYTES, "changed-input")
        return data
    except (OSError, ValueError) as exc:
        if isinstance(exc, GraphError):
            raise
        raise GraphError("unavailable-input") from None


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-key")
        result[key] = value
    return result


def nonfinite(_):
    raise GraphError("nonfinite-json")


def fields(value: Any, required: set[str], optional: set[str] | None = None) -> None:
    require(isinstance(value, dict) and required <= set(value), "invalid-shape")
    require(set(value) <= required | (optional or set()), "unsupported-fields")


def label(value: Any, node_id: bool = False) -> None:
    require(isinstance(value, str) and 0 < len(value) <= 256 and
            all(32 <= ord(c) and not 127 <= ord(c) < 160 for c in value), "invalid-identifier")
    if node_id:
        require(bool(ID.fullmatch(value)), "invalid-node-identifier")


def revision(value: Any) -> None:
    require(type(value) is int and 1 <= value <= 2**31 - 1, "invalid-revision")


def labels(values: Any, nonempty: bool = False) -> None:
    require(isinstance(values, list) and (not nonempty or bool(values)) and
            len(values) <= MAX_NODES, "invalid-reference-list")
    for value in values:
        label(value)
    require(len(values) == len(set(values)), "duplicate-reference")


def inspect(data: bytes, group_size: int = 4) -> dict[str, Any]:
    require(type(group_size) is int and 1 <= group_size <= 32, "invalid-group-size")
    require(isinstance(data, bytes) and len(data) <= MAX_BYTES, "input-size-limit")
    try:
        graph = json.loads(data.decode("utf-8"), object_pairs_hook=unique, parse_constant=nonfinite)
    except GraphError:
        raise
    except (UnicodeError, ValueError, RecursionError):
        raise GraphError("invalid-json") from None
    fields(graph, {"format_version", "kind", "id", "revision", "nodes"}, {"reducers"})
    require(type(graph["format_version"]) is int and graph["format_version"] == 1 and
            graph["kind"] == "decision-graph", "unsupported-contract")
    label(graph["id"], True)
    require(len(graph["id"]) >= 3, "invalid-graph-identifier")
    revision(graph["revision"])
    nodes, reducers = graph["nodes"], graph.get("reducers", [])
    require(isinstance(nodes, list) and 1 <= len(nodes) <= MAX_NODES, "node-count-limit")
    require(isinstance(reducers, list) and len(reducers) <= MAX_REDUCERS, "reducer-count-limit")
    dependencies, specs = {}, {}
    edges = 0
    for node in nodes:
        fields(node, {"id", "spec_id", "spec_revision", "depends_on"})
        label(node["id"], True)
        label(node["spec_id"])
        revision(node["spec_revision"])
        labels(node["depends_on"])
        require(node["id"] not in dependencies, "duplicate-node")
        dependencies[node["id"]] = set(node["depends_on"])
        specs.setdefault((node["spec_id"], node["spec_revision"]), []).append(node["id"])
        edges += len(node["depends_on"])
    require(edges <= MAX_EDGES, "edge-count-limit")
    known = set(dependencies)
    problems = set()
    for name, deps in dependencies.items():
        if name in deps:
            problems.add("self-dependency")
        if deps - known:
            problems.add("unknown-dependency")
    reducer_names = set()
    for reducer in reducers:
        fields(reducer, {"id", "type", "inputs"}, {"output"})
        label(reducer["id"])
        require(reducer["type"] == "deterministic", "unsupported-reducer")
        labels(reducer["inputs"], True)
        if "output" in reducer:
            label(reducer["output"])
        if reducer["id"] in reducer_names:
            problems.add("duplicate-reducer")
        reducer_names.add(reducer["id"])
        if set(reducer["inputs"]) - known:
            problems.add("unknown-reducer-input")
    layers, depths, remaining = [], {}, set(known)
    if not problems:
        while remaining:
            ready = sorted(name for name in remaining if not dependencies[name] & remaining)
            if not ready:
                problems.add("cycle-or-cycle-blocked-nodes")
                break
            depth = len(layers)
            layers.append({"depth": depth, "groups": [ready[i:i + group_size]
                           for i in range(0, len(ready), group_size)]})
            depths.update({name: depth for name in ready})
            remaining.difference_update(ready)
    # No partial review groups if any semantic failure was found.
    return {
        "kind": "decision-graph-review", "format_version": 1,
        "source": {"sha256": "sha256:" + hashlib.sha256(data).hexdigest(), "bytes": len(data)},
        "graph": {"id": graph["id"], "revision": graph["revision"]},
        "status": "blocked" if problems else "reviewable",
        "problems": sorted(problems),
        "counts": {"nodes": len(nodes), "dependency_edges": edges, "reducers": len(reducers)},
        "group_size": group_size, "layers": [] if problems else layers,
        "repeated_spec_references": [
            {"spec_id": spec, "spec_revision": rev, "nodes": sorted(names)}
            for (spec, rev), names in sorted(specs.items()) if len(names) > 1],
        "reducers": [] if problems else [
            {"id": item["id"], "inputs": sorted(item["inputs"]),
             "declared_inputs_after_layer": max(depths[name] for name in item["inputs"]),
             "execution": "not-performed"}
            for item in sorted(reducers, key=lambda item: item["id"])],
        "boundaries": {
            "scope": "declared-dependencies-only", "canonical_schema_validation": False,
            "state_equivalence_checked": False, "spec_contents_checked": False,
            "evidence_sufficiency_checked": False, "provider_compatibility_checked": False,
            "execution": "not-performed", "batching_authorized": False,
            "consequence_authorized": False, "token_savings_verified": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="explicitly reviewed non-secret DecisionGraph JSON")
    parser.add_argument("--group-size", type=int, default=4, help="display width, not execution concurrency (1..32)")
    args = parser.parse_args()
    try:
        result = inspect(read_graph(args.graph), args.group_size)
        output = encoded(result)
        require(len(output) <= 4 * MAX_BYTES, "report-size-limit")
    except (GraphError, OSError, UnicodeError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, GraphError) else "unavailable-input"
        sys.stderr.buffer.write(encoded({"kind": "decision-graph-review-error", "code": code}))
        return 2
    sys.stdout.buffer.write(output)
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
