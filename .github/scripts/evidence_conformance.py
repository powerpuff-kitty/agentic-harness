#!/usr/bin/env python3
"""Inspect the fixed shared corpus; never run its content or fetch its references."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from jsonschema import Draft202012Validator

import strict_json

ROOT = Path(__file__).resolve().parents[2]
CORPUS = "catalog/conformance/evidence-v1.json"
SCHEMA = "catalog/schema/codebase-audit.v2.schema.json"
SCHEMA_GIT_BLOB = "d85f59542b77adf74f04b37c8c31b836771c7c7d"


class ConformanceError(ValueError):
    """Fixed-code error for malformed test metadata, without echoing payloads."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ConformanceError(code)


def fields(value: object, expected: str) -> None:
    require(type(value) is dict and set(value) == set(expected.split()), "invalid-fields")


def input_bytes(case: dict) -> bytes:
    require(type(case["input"]) is str, "invalid-input-type")
    if case["encoding"] == "utf-8":
        raw = case["input"].encode("utf-8")
    elif case["encoding"] == "hex":
        require(re.fullmatch(r"(?:[0-9a-f]{2})*", case["input"]) is not None, "invalid-input-hex")
        raw = bytes.fromhex(case["input"])
    else:
        raise ConformanceError("invalid-input-encoding")
    require(len(raw) <= 4096, "case-size-limit")
    require(type(case["sha256"]) is str
            and hashlib.sha256(raw).hexdigest() == case["sha256"], "case-digest-mismatch")
    return raw


def validate_corpus(raw: bytes, schema_bytes: bytes) -> tuple[dict, Draft202012Validator]:
    try:
        value = strict_json.loads(raw)
    except strict_json.StrictJSONError as error:
        raise ConformanceError("corpus-" + str(error)) from None
    fields(value, "format_version kind id schema limits scope not_checked cases")
    require(type(value["format_version"]) is int and value["format_version"] == 1, "invalid-version")
    require(value["kind"] == "evidence-conformance-corpus"
            and value["id"] == "strict-json-audit-v2.1", "invalid-corpus-id")
    require(value["scope"] == "transport-and-audit-shape-only", "unsupported-scope")
    fields(value["limits"], "max_input_bytes")
    require(type(value["limits"]["max_input_bytes"]) is int
            and value["limits"]["max_input_bytes"] == 4096, "invalid-limits")
    fields(value["schema"], "path git_blob_sha sha256")
    require(value["schema"]["path"] == SCHEMA, "unsupported-schema-path")
    # The accepted schema is independently pinned; rehashing an arbitrary schema
    # cannot enable remote $ref resolution or silently change these test semantics.
    require(value["schema"]["git_blob_sha"] == SCHEMA_GIT_BLOB, "unsupported-schema-identity")
    require(type(schema_bytes) is bytes and len(schema_bytes) <= strict_json.MAX_BYTES, "invalid-schema-bytes")
    header = b"blob " + str(len(schema_bytes)).encode() + b"\0"
    require(hashlib.sha1(header + schema_bytes).hexdigest() == value["schema"]["git_blob_sha"]
            and hashlib.sha256(schema_bytes).hexdigest() == value["schema"]["sha256"], "schema-digest-mismatch")
    # This is a local, version-bound schema. References inside cases are never resolved.
    schema = strict_json.loads(schema_bytes)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    require(type(value["not_checked"]) is list and 1 <= len(value["not_checked"]) <= 16
            and all(type(x) is str and 0 < len(x) <= 1024 for x in value["not_checked"]), "missing-limitations")
    cases = value["cases"]
    require(type(cases) is list and 1 <= len(cases) <= 128, "invalid-cases")
    seen = set()
    families = set()
    for case in cases:
        fields(case, "id family input encoding sha256 expected category")
        require(type(case["id"]) is str and re.fullmatch(r"[a-z][a-z0-9.-]{0,127}", case["id"]) is not None, "invalid-case-id")
        require(case["id"] not in seen, "duplicate-case-id")
        seen.add(case["id"])
        require(case["family"] in ("strict-json", "codebase-audit-v2"), "unsupported-family")
        families.add(case["family"])
        require(type(case["expected"]) is bool, "invalid-expectation")
        require(case["category"] in ("transport", "schema"), "invalid-category")
        require(case["family"] != "strict-json" or case["category"] == "transport", "invalid-category")
        input_bytes(case)
    require(families == {"strict-json", "codebase-audit-v2"}, "missing-family")
    return value, validator


def inspect(raw: bytes, schema_bytes: bytes) -> dict:
    """Compare expected acceptance with the actual reference decoder/schema behavior."""
    corpus, validator = validate_corpus(raw, schema_bytes)
    results = []
    for case in sorted(corpus["cases"], key=lambda c: c["id"]):
        try:
            value = strict_json.loads(input_bytes(case), max_bytes=4096)
        except strict_json.StrictJSONError:
            actual, stage = False, "transport"
        else:
            actual = case["family"] == "strict-json" or validator.is_valid(value)
            stage = "accepted" if actual else "schema"
        matches = actual == case["expected"]
        if not case["expected"]:
            matches = matches and stage == case["category"]
        results.append({"id": case["id"], "family": case["family"], "sha256": case["sha256"],
                        "expected": case["expected"], "actual": actual, "stage": stage, "matches": matches})
    return {"format_version": 1, "kind": "evidence-conformance-result",
            "scope": corpus["scope"], "consumer": "python-reference",
            "corpus_sha256": hashlib.sha256(raw).hexdigest(),
            "schema_sha256": hashlib.sha256(schema_bytes).hexdigest(),
            "case_count": len(results), "conformant_with_corpus": all(c["matches"] for c in results),
            "results": results, "not_checked": corpus["not_checked"],
            "completion_verified": False, "release_verified": False}


def read_local(relative: str) -> bytes:
    require(relative in (CORPUS, SCHEMA), "unsupported-local-path")
    path = ROOT
    for part in relative.split("/"):
        path /= part
        require(not path.is_symlink(), "symlinked-input")
    with path.open("rb") as stream:
        return stream.read(strict_json.MAX_BYTES + 1)


def main() -> int:
    try:
        result = inspect(read_local(CORPUS), read_local(SCHEMA))
    except (ConformanceError, strict_json.StrictJSONError, OSError):
        print('{"kind":"conformance-error","code":"invalid-local-corpus"}')
        return 2
    print(strict_json.dumps(result).decode("utf-8"))
    return 0 if result["conformant_with_corpus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
