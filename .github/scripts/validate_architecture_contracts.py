#!/usr/bin/env python3
"""Validate the public Architecture Graph v1 contract and semantic graph invariants."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

import architecture_graph as graph_analysis

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "catalog/schema/architecture-graph.v1.schema.json").read_text())
FIXTURE = json.loads((ROOT / ".agentic/evals/fixtures/architecture-graph.v1.json").read_text())
FIXTURE_DIR = ROOT / ".agentic/evals/fixtures/architecture"
ANALYSIS_SCHEMA = json.loads((ROOT / "catalog/schema/architecture-analysis.v1.schema.json").read_text())
DERIVATIVES_SCHEMA = json.loads((ROOT / "catalog/schema/architecture-derivatives.v1.schema.json").read_text())
DRIFT_SCHEMA = json.loads((ROOT / "catalog/schema/architecture-drift.v1.schema.json").read_text())
WEB_FIXTURE = json.loads((FIXTURE_DIR / "architecture-graph.web-ts.v1.json").read_text())
RUST_FIXTURE = json.loads((FIXTURE_DIR / "architecture-graph.rust-workspace.v1.json").read_text())
MIXED_FIXTURE = json.loads((FIXTURE_DIR / "architecture-graph.mixed-stack.v1.json").read_text())
DUPLICATE_FIXTURE = json.loads((FIXTURE_DIR / "architecture-graph.duplicate-capability.v1.json").read_text())
WEB_TARGET_FIXTURE = json.loads((FIXTURE_DIR / "architecture-graph.web-ts-target.v1.json").read_text())
WEB_MERMAID = (FIXTURE_DIR / "architecture-diagram.web-ts.mmd").read_text()
WEB_SUMMARY = (FIXTURE_DIR / "architecture-summary.web-ts.md").read_text()
Draft202012Validator.check_schema(SCHEMA)
Draft202012Validator.check_schema(ANALYSIS_SCHEMA)
Draft202012Validator.check_schema(DERIVATIVES_SCHEMA)
Draft202012Validator.check_schema(DRIFT_SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
ANALYSIS_VALIDATOR = Draft202012Validator(ANALYSIS_SCHEMA)
DERIVATIVES_VALIDATOR = Draft202012Validator(DERIVATIVES_SCHEMA)
DRIFT_VALIDATOR = Draft202012Validator(DRIFT_SCHEMA)


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

    def test_three_structurally_different_graphs_validate(self):
        for name, fixture in (
            ("web-ts", WEB_FIXTURE),
            ("rust-workspace", RUST_FIXTURE),
            ("mixed-stack", MIXED_FIXTURE),
        ):
            with self.subTest(name=name):
                VALIDATOR.validate(fixture)
                self.assertEqual(semantic_errors(fixture), [])

    def test_web_task_paths_resolve_to_capability_context(self):
        result = graph_analysis.resolve_task_context(
            WEB_FIXTURE,
            [
                "apps/web/src/features/catalog/Grid.vue",
                "packages/search/src/query.ts",
            ],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["ambiguous_paths"], [])
        self.assertEqual(result["unresolved_paths"], [])
        by_id = {item["id"]: item for item in result["capabilities"]}
        self.assertEqual(set(by_id), {"capability.catalog", "capability.search"})
        self.assertEqual(by_id["capability.catalog"]["owner_path"], "packages/catalog")
        self.assertEqual(by_id["capability.catalog"]["contract_ids"], ["contract.catalog"])
        self.assertEqual(by_id["capability.catalog"]["surface_ids"], ["surface.catalog-ui"])

    def test_rust_adapter_routes_through_contract_to_capability_owner(self):
        result = graph_analysis.resolve_task_context(
            RUST_FIXTURE,
            ["crates/postgres/orders/repository.rs"],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(
            [item["id"] for item in result["capabilities"]],
            ["capability.orders"],
        )
        self.assertEqual(
            result["capabilities"][0]["owner_path"],
            "crates/orders",
        )

    def test_mixed_language_engine_and_provider_route_without_special_cases(self):
        result = graph_analysis.resolve_task_context(
            MIXED_FIXTURE,
            [
                "engines/vector/src/lib.rs",
                "infra/kafka/client/consumer.py",
            ],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(
            {item["id"] for item in result["capabilities"]},
            {"capability.index", "capability.ingest"},
        )

    def test_ambiguous_and_unresolved_paths_remain_explicit(self):
        result = graph_analysis.resolve_task_context(
            WEB_FIXTURE,
            ["apps/web/src/main.ts", "docs/unknown.md"],
        )
        self.assertFalse(result["complete"])
        self.assertEqual(result["unresolved_paths"], ["docs/unknown.md"])
        self.assertEqual(
            result["ambiguous_paths"],
            [{
                "path": "apps/web/src/main.ts",
                "capability_ids": ["capability.catalog", "capability.search"],
            }],
        )

    def test_duplicate_capability_is_review_candidate_not_violation(self):
        candidates = graph_analysis.duplicate_capability_candidates(DUPLICATE_FIXTURE)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate["identity"], "listing")
        self.assertEqual(candidate["identity_source"], "metadata.capability_key")
        self.assertEqual(candidate["status"], "review_required")
        self.assertIn("not proof", candidate["reason"])
        self.assertEqual(
            candidate["capability_ids"],
            ["capability.listing.api", "capability.listing.web"],
        )

    def test_analysis_output_is_schema_valid_and_deterministic(self):
        paths = ["apps/web/src/features/catalog/Grid.vue"]
        first = graph_analysis.analyze(WEB_FIXTURE, paths)
        ANALYSIS_VALIDATOR.validate(first)

        reordered = copy.deepcopy(WEB_FIXTURE)
        reordered["nodes"] = list(reversed(reordered["nodes"]))
        reordered["edges"] = list(reversed(reordered["edges"]))
        second = graph_analysis.analyze(reordered, paths)
        self.assertEqual(
            graph_analysis.stable_json(first),
            graph_analysis.stable_json(second),
        )

    def test_generated_summary_matches_committed_fixture_exactly(self):
        generated = graph_analysis.render_markdown(WEB_FIXTURE)
        self.assertEqual(generated, WEB_SUMMARY)
        self.assertTrue(graph_analysis.check_markdown(WEB_FIXTURE, WEB_SUMMARY))
        self.assertFalse(
            graph_analysis.check_markdown(
                WEB_FIXTURE,
                WEB_SUMMARY.replace("surface.catalog-ui", "surface.catalog-screen"),
            )
        )

    def test_task_paths_must_be_relative_posix_paths(self):
        for path in ("/absolute/file.ts", "../escape.ts", r"src\windows.ts"):
            with self.subTest(path=path):
                with self.assertRaises(graph_analysis.ArchitectureAnalysisError):
                    graph_analysis.resolve_task_context(WEB_FIXTURE, [path])


    def test_guardrail_plan_derives_ready_path_prefixes_without_enforcement_claim(self):
        output = graph_analysis.derive_graph_outputs(WEB_FIXTURE)
        DERIVATIVES_VALIDATOR.validate(output)
        plan = output["guardrail_plan"]
        self.assertEqual(plan["ready_count"], 1)
        self.assertEqual(plan["unresolved_count"], 0)
        self.assertFalse(plan["enforcement_claim"])
        entry = plan["entries"][0]
        self.assertEqual(entry["constraint_id"], "boundary.web-no-catalog-adapter")
        self.assertEqual(entry["effect"], "forbid")
        self.assertEqual(entry["subject_path"], "apps/web")
        self.assertEqual(entry["target_path"], "packages/catalog/src/adapters/api")
        self.assertEqual(entry["plan_status"], "ready")
        self.assertFalse(entry["enforcement_claim"])

    def test_guardrail_missing_path_stays_unresolved(self):
        graph = copy.deepcopy(WEB_FIXTURE)
        graph["constraints"].append({
            "id": "boundary.catalog-no-authority-import",
            "kind": "forbidden-dependency",
            "subject": "capability.catalog",
            "target": "authority.catalog-store",
            "status": "declared",
            "mechanism": None,
            "evidence_refs": [],
            "description": "Synthetic missing-path guardrail case.",
        })
        plan = graph_analysis.derive_guardrail_plan(graph)
        entry = next(
            item for item in plan["entries"]
            if item["constraint_id"] == "boundary.catalog-no-authority-import"
        )
        self.assertEqual(entry["plan_status"], "unresolved")
        self.assertEqual(entry["unresolved_reasons"], ["target-path-missing"])
        self.assertFalse(entry["enforcement_claim"])

    def test_surface_inventory_does_not_treat_internal_capability_as_violation(self):
        inventory = {
            item["capability_id"]: item
            for item in graph_analysis.surface_inventory(RUST_FIXTURE)
        }
        self.assertEqual(inventory["capability.orders"]["status"], "exposed")
        self.assertEqual(
            inventory["capability.orders"]["surface_ids"],
            ["surface.orders-http"],
        )
        self.assertEqual(
            inventory["capability.payments"],
            {
                "capability_id": "capability.payments",
                "surface_ids": [],
                "status": "internal_or_unexposed",
            },
        )

    def test_mermaid_output_matches_committed_fixture_exactly(self):
        generated = graph_analysis.render_mermaid(WEB_FIXTURE)
        self.assertEqual(generated, WEB_MERMAID)
        self.assertTrue(graph_analysis.check_mermaid(WEB_FIXTURE, WEB_MERMAID))
        self.assertFalse(
            graph_analysis.check_mermaid(
                WEB_FIXTURE,
                WEB_MERMAID.replace("Catalog<br/>capability", "Catalogue<br/>capability"),
            )
        )

    def test_graph_drift_reports_structural_and_evidence_changes(self):
        VALIDATOR.validate(WEB_TARGET_FIXTURE)
        self.assertEqual(semantic_errors(WEB_TARGET_FIXTURE), [])
        drift = graph_analysis.compare_graphs(WEB_FIXTURE, WEB_TARGET_FIXTURE)
        DRIFT_VALIDATOR.validate(drift)

        self.assertEqual(
            drift["node_changes"]["added_ids"],
            ["capability.recommendations", "surface.recommendations-ui"],
        )
        catalog_change = next(
            item for item in drift["node_changes"]["changed"]
            if item["id"] == "capability.catalog"
        )
        self.assertEqual(
            catalog_change["fields"],
            [{
                "field": "path",
                "before": "packages/catalog",
                "after": "packages/catalog-core",
            }],
        )
        self.assertEqual(
            drift["edge_changes"]["added"],
            [
                "app.web|composes|capability.recommendations",
                "capability.recommendations|depends-on|capability.catalog",
                "capability.recommendations|exposes|surface.recommendations-ui",
            ],
        )
        constraint_change = drift["constraint_changes"]["changed"][0]
        self.assertEqual(constraint_change["id"], "boundary.web-no-catalog-adapter")
        self.assertEqual(
            [item["field"] for item in constraint_change["fields"]],
            ["status", "mechanism", "evidence_refs"],
        )
        self.assertTrue(drift["coverage_changed"])
        self.assertTrue(drift["not_checked_added"])
        self.assertTrue(drift["not_checked_removed"])

    def test_graph_drift_is_stable_under_input_reordering(self):
        first = graph_analysis.compare_graphs(WEB_FIXTURE, WEB_TARGET_FIXTURE)
        before = copy.deepcopy(WEB_FIXTURE)
        after = copy.deepcopy(WEB_TARGET_FIXTURE)
        before["nodes"].reverse()
        before["edges"].reverse()
        before["constraints"].reverse()
        after["nodes"].reverse()
        after["edges"].reverse()
        after["constraints"].reverse()
        second = graph_analysis.compare_graphs(before, after)
        self.assertEqual(
            graph_analysis.stable_json(first),
            graph_analysis.stable_json(second),
        )

    def test_reverse_drift_reports_removals(self):
        reverse = graph_analysis.compare_graphs(WEB_TARGET_FIXTURE, WEB_FIXTURE)
        self.assertEqual(
            reverse["node_changes"]["removed_ids"],
            ["capability.recommendations", "surface.recommendations-ui"],
        )
        self.assertEqual(len(reverse["edge_changes"]["removed"]), 3)

    def test_graph_drift_rejects_different_projects(self):
        other = copy.deepcopy(WEB_TARGET_FIXTURE)
        other["project"]["id"] = "fixture.other-project"
        with self.assertRaises(graph_analysis.ArchitectureAnalysisError):
            graph_analysis.compare_graphs(WEB_FIXTURE, other)



if __name__ == "__main__":
    unittest.main()
