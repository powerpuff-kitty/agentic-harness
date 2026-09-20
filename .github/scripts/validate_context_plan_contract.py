#!/usr/bin/env python3
"""Validate compiled-context plan schema and semantic invariants."""
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (ROOT / "catalog/schema/compiled-context-plan.v1.schema.json").read_text()
)
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
DIGEST = "sha256:" + ("a" * 64)

FIXTURE = {
    "format_version": 1,
    "kind": "compiled-context-plan",
    "target": ".",
    "task": {
        "text": "add validation to GitHub project creation",
        "intent": None,
    },
    "compiler": {
        "id": "agentic-harness-cli/context-compiler",
        "version": "0.1.0",
        "deterministic": True,
    },
    "budget": {
        "estimator": {
            "id": "characters-div-4",
            "version": "1",
            "unit": "estimated-tokens",
            "disclaimer": "Portable estimate; not provider billing.",
        },
        "input": {"limit": 18000, "estimated": 120},
        "tool_output": {"limit": None, "estimated": None},
        "output": {"limit": None, "estimated": None},
        "over_budget": False,
    },
    "active_context_packs": [],
    "items": [
        {
            "id": "AGENTS.md",
            "source": {
                "kind": "router",
                "path": "AGENTS.md",
                "digest": DIGEST,
                "revision": None,
            },
            "authority": "project-truth",
            "mandatory": True,
            "stability": "stable",
            "disclosure": "router",
            "disposition": "included",
            "estimated_tokens": 120,
            "signals": {
                "relevance": {"score": 0, "method": "lexical-v1"},
                "confidence": None,
                "freshness": "current",
                "dependency_distance": None,
            },
            "context_packs": [],
            "reasons": ["mandatory-project-context"],
        },
        {
            "id": "src/github_project.rs",
            "source": {
                "kind": "repository-file",
                "path": "src/github_project.rs",
                "digest": DIGEST,
                "revision": None,
            },
            "authority": "repository-evidence",
            "mandatory": False,
            "stability": "volatile",
            "disclosure": "file",
            "disposition": "deferred",
            "estimated_tokens": 300,
            "signals": {
                "relevance": {"score": 25, "method": "lexical-v1"},
                "confidence": None,
                "freshness": "current",
                "dependency_distance": None,
            },
            "context_packs": [],
            "reasons": ["budget"],
        },
    ],
    "coverage": {
        "complete": True,
        "files_discovered": 2,
        "supported_text_files": 2,
        "unsupported_files": 0,
        "unreadable_files": 0,
        "required_unavailable": 0,
        "errors": [],
    },
    "not_checked": [
        "semantic dependency distance",
        "provider tokenizer billing",
    ],
}


def validate_semantics(value):
    VALIDATOR.validate(value)
    item_ids = [item["id"] for item in value["items"]]
    assert len(item_ids) == len(set(item_ids)), "context item IDs must be unique"

    active = set(value["active_context_packs"])
    for item in value["items"]:
        assert set(item["context_packs"]).issubset(active), (
            "item references an inactive context pack",
            item["id"],
        )

    selected = sum(
        item["estimated_tokens"]
        for item in value["items"]
        if item["disposition"] == "included"
    )
    assert selected == value["budget"]["input"]["estimated"], (
        "input estimate must equal included item estimates",
        selected,
        value["budget"]["input"]["estimated"],
    )
    limit = value["budget"]["input"]["limit"]
    assert value["budget"]["over_budget"] is (limit is not None and selected > limit)

    if value["coverage"]["required_unavailable"] > 0 or value["coverage"]["errors"]:
        assert value["coverage"]["complete"] is False


validate_semantics(FIXTURE)

invalid = copy.deepcopy(FIXTURE)
invalid["items"][0]["disposition"] = "deferred"
assert not VALIDATOR.is_valid(invalid), "mandatory context cannot be deferred"

invalid = copy.deepcopy(FIXTURE)
invalid["budget"]["input"]["estimated"] = 121
try:
    validate_semantics(invalid)
except AssertionError:
    pass
else:
    raise AssertionError("mismatched selected-token estimate was accepted")

invalid = copy.deepcopy(FIXTURE)
invalid["items"][1]["context_packs"] = ["web-app"]
try:
    validate_semantics(invalid)
except AssertionError:
    pass
else:
    raise AssertionError("inactive context-pack reference was accepted")

invalid = copy.deepcopy(FIXTURE)
invalid["coverage"]["required_unavailable"] = 1
invalid["coverage"]["complete"] = True
try:
    validate_semantics(invalid)
except AssertionError:
    pass
else:
    raise AssertionError("missing required context was marked complete")

print("Compiled context plan schema and semantic fixtures passed")
