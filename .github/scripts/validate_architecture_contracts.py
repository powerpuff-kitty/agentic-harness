#!/usr/bin/env python3
"""Validate the public Architecture Graph v1 contract and semantic graph invariants."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "catalog/schema/architecture-graph.v1.schema.json").read_text())
FIXTURE = json.loads((ROOT / ".agentic/evals/fixtures/architecture-graph.v1.json").read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


def semantic_errors(document: dict) -> list[str]:
    errors: list[str] = []
    nodes = document.get("nodes", [])
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]

    if len(ids) != len(set(ids)):
        errors.append("node ids must be unique")

    by_id = {
        node["id"]: node
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }

    constraint_ids: list[str] = []
    for edge in document.get("edges", []):
        source = edge.get("from")
        target = edge.get("to")
        if source not in by_id:
            errors.append(f"edge references unknown source: {source}")
        if target not in by_id:
            errors.append(f"edge references unknown target: {target}")
        if edge.get("kind") == "depends-on" and source in by_id and target in by_id:
            if by_id[source].get("kind") != "capability" or by_id[target].get("kind") != "capability":
                errors.append(f"depends-on edges must connect capabilities: {source} -> {target}")

    for constraint in document.get("constraints", []):
        constraint_id = constraint.get("id")
        if isinstance(constraint_id, str):
            constraint_ids.append(constraint_id)
        for field in ("subject", "target"):
            ref = constraint.get(field)
            if ref not in by_id:
                errors.append(f"constraint {constraint_id} references unknown {field}: {ref}")

    if len(constraint_ids) != len(set(constraint_ids)):
        errors.append("constraint ids must be unique")

    dependencies: dict[str, list[str]] = {
        node_id: [] for node_id, node in by_id.items() if node.get("kind") == "capability"
    }
    for edge in document.get("edges", []):
        if edge.get("kind") == "depends-on" and edge.get("from") in dependencies:
            target = edge.get("to")
            if target in dependencies:
                dependencies[edge["from"]].append(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str, stack: list[str]) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            try:
                start = stack.index(node_id)
            except ValueError:
                start = 0
            errors.append("capability dependency cycle: " + " -> ".join(stack[start:] + [node_id]))
            return
        visiting.add(node_id)
        for dependency in dependencies.get(node_id, []):
            visit(dependency, stack + [node_id])
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in dependencies:
        visit(node_id, [])

    coverage = document.get("coverage", {})
    if coverage.get("nodes_declared") != len(nodes):
        errors.append("coverage.nodes_declared must equal the number of nodes")
    if coverage.get("edges_declared") != len(document.get("edges", [])):
        errors.append("coverage.edges_declared must equal the number of edges")

    return errors


class ArchitectureGraphContracts(unittest.TestCase):
    def test_fixture_is_schema_valid_and_semantically_valid(self):
        VALIDATOR.validate(FIXTURE)
        self.assertEqual(semantic_errors(FIXTURE), [])

    def test_duplicate_node_is_rejected_semantically(self):
        bad = copy.deepcopy(FIXTURE)
        bad["nodes"].append(copy.deepcopy(bad["nodes"][0]))
        bad["coverage"]["nodes_declared"] += 1
        self.assertIn("node ids must be unique", semantic_errors(bad))

    def test_unresolved_edge_is_rejected_semantically(self):
        bad = copy.deepcopy(FIXTURE)
        bad["edges"][0]["to"] = "capability.missing"
        self.assertIn("edge references unknown target: capability.missing", semantic_errors(bad))

    def test_depends_on_must_connect_capabilities(self):
        bad = copy.deepcopy(FIXTURE)
        bad["edges"][0]["to"] = "contract.listing"
        self.assertIn(
            "depends-on edges must connect capabilities: capability.listing -> contract.listing",
            semantic_errors(bad),
        )

    def test_capability_cycle_is_rejected_semantically(self):
        bad = copy.deepcopy(FIXTURE)
        bad["edges"].append({
            "from": "capability.property",
            "to": "capability.search",
            "kind": "depends-on",
        })
        bad["coverage"]["edges_declared"] += 1
        self.assertTrue(any(error.startswith("capability dependency cycle:") for error in semantic_errors(bad)))

    def test_checked_constraint_requires_mechanism_and_evidence(self):
        bad = copy.deepcopy(FIXTURE)
        bad["constraints"][0]["status"] = "checked"
        self.assertFalse(VALIDATOR.is_valid(bad))
        bad["constraints"][0]["mechanism"] = "synthetic import-boundary check"
        bad["constraints"][0]["evidence_refs"] = ["fixture:boundary-check"]
        VALIDATOR.validate(bad)

    def test_coverage_counts_are_semantic_invariants(self):
        bad = copy.deepcopy(FIXTURE)
        bad["coverage"]["nodes_declared"] = 1
        self.assertIn(
            "coverage.nodes_declared must equal the number of nodes",
            semantic_errors(bad),
        )


if __name__ == "__main__":
    unittest.main()
