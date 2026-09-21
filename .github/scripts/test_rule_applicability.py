#!/usr/bin/env python3
"""Applicability-map regressions; caller-resolved membership is not source discovery."""
import copy
import unittest

import rule_applicability as app

D = "sha256:" + "a" * 64


def rule(rule_id, key, statement, directive, include):
    return {
        "id": rule_id, "key": key, "statement": statement,
        "authority": "policy", "strength": "mandatory", "directive": directive,
        "scope": {"base": ".", "include": [include], "exclude": []},
        "conditions": [], "exceptions": [],
        "source": {"reference": "AGENTS.md", "sha256": D,
                   "start_line": int(rule_id[-1]), "end_line": int(rule_id[-1])}
    }


def inventory():
    return {
        "format_version": 1, "kind": "rule-inventory", "target": "fixture",
        "rules": [
            rule("r1", "http.boundary", "Views must use services.", "require", "src/views/**"),
            rule("r2", "http.boundary", "Views must not call HTTP directly.", "forbid", "src/**/*.vue"),
            rule("r3", "tests.required", "Run all required tests before completion.", "require", "**"),
            rule("r4", "tests.required", "Run every required test before completing.", "require", "src/**"),
            rule("r5", "release.approval", "Owner approval is required before release.", "require", "**"),
        ]
    }


def resolution():
    return {
        "format_version": 1, "kind": "rule-applicability-map",
        "target": "fixture", "semantics": "caller-resolved-targets-v1",
        "rules": [
            {"rule_id": "r1", "targets": ["src/views/home.vue"]},
            {"rule_id": "r2", "targets": ["src/views/home.vue"]},
            {"rule_id": "r3", "targets": ["src/views/home.vue", "src/service.ts"]},
            {"rule_id": "r4", "targets": ["src/views/home.vue"]},
            {"rule_id": "r5", "targets": ["release"]},
        ]
    }


class ApplicabilityReview(unittest.TestCase):
    def test_nonidentical_selectors_can_surface_declared_conflict(self):
        result = app.review_applicability(inventory(), resolution())
        conflict = next(item for item in result["overlaps"]
                        if item["rule_ids"] == ["r1", "r2"])
        self.assertEqual(conflict["review"], "declared-overlap-conflict")
        self.assertEqual(conflict["directive_relation"], "opposed")
        self.assertFalse(result["limits"]["selector_semantics_inferred"])
        self.assertFalse(result["limits"]["natural_language_conflicts_resolved"])

    def test_same_directive_near_duplicate_is_review_candidate_not_merge(self):
        result = app.review_applicability(inventory(), resolution(), similarity_threshold=.75)
        candidate = next(item for item in result["overlaps"]
                         if item["rule_ids"] == ["r3", "r4"])
        self.assertEqual(candidate["review"], "possible-equivalence")
        self.assertGreaterEqual(candidate["lexical_similarity"], .75)
        self.assertFalse(result["limits"]["automatic_merge"])
        self.assertFalse(result["limits"]["semantic_equivalence_verified"])

    def test_target_filter_uses_only_supplied_membership(self):
        result = app.review_applicability(inventory(), resolution(), target="src/service.ts")
        self.assertEqual(result["applicable_rule_ids"], ["r3"])
        result = app.review_applicability(inventory(), resolution(), target="unknown.ts")
        self.assertEqual(result["applicable_rule_ids"], [])

    def test_nonoverlap_does_not_create_pair(self):
        result = app.review_applicability(inventory(), resolution())
        pairs = {tuple(item["rule_ids"]) for item in result["overlaps"]}
        self.assertNotIn(("r1", "r5"), pairs)

    def test_conditions_or_exceptions_prevent_definite_conflict(self):
        value = inventory()
        value["rules"][1]["conditions"] = ["only in production"]
        result = app.review_applicability(value, resolution())
        conflict = next(item for item in result["overlaps"]
                        if item["rule_ids"] == ["r1", "r2"])
        self.assertEqual(conflict["review"], "scope-overlap-review")
        self.assertFalse(conflict["same_conditions_and_exceptions"])

    def test_resolution_must_cover_every_rule_exactly_once(self):
        current = resolution()
        current["rules"].pop()
        with self.assertRaisesRegex(app.ApplicabilityError, "applicability-rule-set-mismatch"):
            app.review_applicability(inventory(), current)
        current = resolution()
        current["rules"].append(copy.deepcopy(current["rules"][0]))
        with self.assertRaisesRegex(app.ApplicabilityError, "duplicate-applicability-rule-id"):
            app.review_applicability(inventory(), current)

    def test_extra_rule_id_is_rejected(self):
        current = resolution()
        current["rules"][-1]["rule_id"] = "extra"
        with self.assertRaisesRegex(app.ApplicabilityError, "applicability-rule-set-mismatch"):
            app.review_applicability(inventory(), current)

    def test_target_and_semantics_are_bound(self):
        current = resolution()
        current["target"] = "other"
        with self.assertRaisesRegex(app.ApplicabilityError, "applicability-target-mismatch"):
            app.review_applicability(inventory(), current)
        current = resolution()
        current["semantics"] = "glob-guessed"
        with self.assertRaisesRegex(app.ApplicabilityError, "invalid-applicability-map"):
            app.review_applicability(inventory(), current)

    def test_selector_strings_are_never_evaluated(self):
        value = inventory()
        value["rules"][0]["scope"]["include"] = ["this is not parsed /** [x]"]
        result = app.review_applicability(value, resolution())
        self.assertFalse(result["limits"]["selector_semantics_inferred"])
        self.assertEqual(result["summary"]["declared_overlap_conflicts"], 1)

    def test_map_identity_changes_with_membership(self):
        first = app.review_applicability(inventory(), resolution())["applicability_map_sha256"]
        current = resolution()
        current["rules"][0]["targets"].append("src/views/other.vue")
        second = app.review_applicability(inventory(), current)["applicability_map_sha256"]
        self.assertNotEqual(first, second)

    def test_lexical_cross_context_candidates_do_not_resolve_meaning(self):
        value = inventory()
        value["rules"][4]["statement"] = "Run every required test before completing."
        current = resolution()
        current["rules"][4]["targets"] = ["src/views/home.vue"]
        result = app.review_applicability(value, current, similarity_threshold=.75)
        candidates = {tuple(item["rule_ids"]) for item in result["lexical_review_candidates"]}
        self.assertIn(("r4", "r5"), candidates)
        self.assertFalse(result["limits"]["semantic_equivalence_verified"])

    def test_input_objects_are_not_mutated(self):
        value, current = inventory(), resolution()
        before = copy.deepcopy((value, current))
        app.review_applicability(value, current)
        self.assertEqual(before, (value, current))

    def test_budget_defers_whole_payload_not_overlap_rules(self):
        full = app.review_applicability(inventory(), resolution())
        tiny = app.review_applicability(inventory(), resolution(), budget_bytes=1)
        self.assertTrue(full["complete_payload_emitted"])
        self.assertFalse(tiny["complete_payload_emitted"])
        self.assertNotIn("overlaps", tiny)
        self.assertGreater(tiny["required_output_bytes"], 1)

    def test_threshold_and_budget_are_bounded(self):
        for threshold in (.49, 1.01, True, "0.8"):
            with self.subTest(threshold=threshold), self.assertRaises(app.ApplicabilityError):
                app.review_applicability(inventory(), resolution(), similarity_threshold=threshold)
        for budget in (0, True, 262145):
            with self.subTest(budget=budget), self.assertRaises(app.ApplicabilityError):
                app.review_applicability(inventory(), resolution(), budget_bytes=budget)

    def test_target_reference_count_is_bounded(self):
        current = resolution()
        current["rules"][0]["targets"] = [f"path-{i}" for i in range(257)]
        with self.assertRaisesRegex(app.ApplicabilityError, "invalid-applicability-map"):
            app.review_applicability(inventory(), current)


if __name__ == "__main__":
    unittest.main()
