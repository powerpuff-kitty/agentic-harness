#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "registry" / "architectures"
SCHEMA = ARCH / "architecture-profile.schema.json"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")
KINDS = {"framework", "ecosystem", "tooling", "pattern"}
AUTHORITIES = {"official", "ecosystem-official", "harness", "community"}
SEVERITIES = {"error", "warning", "recommendation"}
ENFORCEABILITY = {"deterministic", "heuristic", "advisory"}
RULE_TYPES = {
    "organization",
    "path-role",
    "path-presence",
    "file-placement",
    "dependency-boundary",
    "module-boundary",
    "ownership",
    "tooling-role",
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


def expect_string(data: dict, key: str, path: Path) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        fail(f"{path.relative_to(ROOT)}: {key} must be a non-empty string")
        return None
    return value


if not SCHEMA.is_file():
    fail("missing registry/architectures/architecture-profile.schema.json")
else:
    load(SCHEMA)

profile_paths = sorted(
    path for path in ARCH.rglob("*.json")
    if path != SCHEMA
)
profiles: dict[str, Path] = {}
all_rule_ids: set[str] = set()

for path in profile_paths:
    data = load(path)
    if not isinstance(data, dict):
        continue

    if data.get("schema_version") != 1:
        fail(f"{path.relative_to(ROOT)}: schema_version must be 1")

    profile_id = expect_string(data, "id", path)
    if profile_id:
        if not ID.match(profile_id):
            fail(f"{path.relative_to(ROOT)}: invalid id {profile_id!r}")
        if profile_id in profiles:
            fail(f"duplicate architecture profile id {profile_id}: {profiles[profile_id].relative_to(ROOT)} and {path.relative_to(ROOT)}")
        profiles[profile_id] = path

    if data.get("kind") not in KINDS:
        fail(f"{path.relative_to(ROOT)}: invalid kind {data.get('kind')!r}")
    if data.get("authority") not in AUTHORITIES:
        fail(f"{path.relative_to(ROOT)}: invalid authority {data.get('authority')!r}")
    reviewed = data.get("reviewed_at")
    if not isinstance(reviewed, str) or not DATE.match(reviewed):
        fail(f"{path.relative_to(ROOT)}: reviewed_at must be YYYY-MM-DD")
    expect_string(data, "name", path)
    expect_string(data, "version_selector", path)

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        fail(f"{path.relative_to(ROOT)}: sources must be a non-empty list")
        source_ids: set[str] = set()
    else:
        source_ids = set()
        for source in sources:
            if not isinstance(source, dict):
                fail(f"{path.relative_to(ROOT)}: source must be an object")
                continue
            source_id = source.get("id")
            if not isinstance(source_id, str) or not ID.match(source_id):
                fail(f"{path.relative_to(ROOT)}: invalid source id {source_id!r}")
            elif source_id in source_ids:
                fail(f"{path.relative_to(ROOT)}: duplicate source id {source_id}")
            else:
                source_ids.add(source_id)
            if source.get("authority") not in AUTHORITIES:
                fail(f"{path.relative_to(ROOT)}: source {source_id!r} has invalid authority")
            url = source.get("url")
            if not isinstance(url, str) or not url.startswith("https://"):
                fail(f"{path.relative_to(ROOT)}: source {source_id!r} must use an https URL")
            date = source.get("reviewed_at")
            if not isinstance(date, str) or not DATE.match(date):
                fail(f"{path.relative_to(ROOT)}: source {source_id!r} reviewed_at must be YYYY-MM-DD")

    rules = data.get("rules")
    if not isinstance(rules, list):
        fail(f"{path.relative_to(ROOT)}: rules must be a list")
        continue
    local_rule_ids: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict):
            fail(f"{path.relative_to(ROOT)}: rule must be an object")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not ID.match(rule_id):
            fail(f"{path.relative_to(ROOT)}: invalid rule id {rule_id!r}")
        else:
            if rule_id in local_rule_ids:
                fail(f"{path.relative_to(ROOT)}: duplicate rule id {rule_id}")
            local_rule_ids.add(rule_id)
            if rule_id in all_rule_ids:
                fail(f"duplicate global architecture rule id: {rule_id}")
            all_rule_ids.add(rule_id)
        if rule.get("rule_type") not in RULE_TYPES:
            fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} has invalid rule_type")
        if rule.get("severity") not in SEVERITIES:
            fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} has invalid severity")
        if rule.get("enforceability") not in ENFORCEABILITY:
            fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} has invalid enforceability")
        if rule.get("authority") not in AUTHORITIES:
            fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} has invalid authority")
        if not isinstance(rule.get("constraints"), dict):
            fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} constraints must be an object")
        refs = rule.get("source_refs")
        if not isinstance(refs, list):
            fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} source_refs must be a list")
        else:
            for ref in refs:
                if ref not in source_ids:
                    fail(f"{path.relative_to(ROOT)}: rule {rule_id!r} references unknown source {ref!r}")

for profile_id, path in profiles.items():
    data = load(path)
    if not isinstance(data, dict):
        continue
    composes = data.get("composes_with", [])
    if not isinstance(composes, list):
        fail(f"{path.relative_to(ROOT)}: composes_with must be a list")
        continue
    for ref in composes:
        if ref not in profiles:
            fail(f"{path.relative_to(ROOT)}: composes_with references unknown profile {ref!r}")
        if ref == profile_id:
            fail(f"{path.relative_to(ROOT)}: profile cannot compose with itself")

if errors:
    print("Architecture registry validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(f"Architecture registry valid: {len(profiles)} profiles, {len(all_rule_ids)} unique rules")
