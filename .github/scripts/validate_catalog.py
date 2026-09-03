#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_BOILERPLATES = {"base", "web-app", "backend-api", "saas", "monorepo", "library-sdk"}
FORBIDDEN_ROOTS = {"boilerplates", "templates", "packs", "policies", "profiles", "examples", "marketing", "crates", "packages"}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return None


for name in FORBIDDEN_ROOTS:
    if (ROOT / name).exists():
        fail(f"deprecated root path exists: {name}/")

for required in ["README.md", "ARCHITECTURE.md", "CONCEPTS.md", "modules", "presets", "schema", "docs"]:
    if not (ROOT / required).exists():
        fail(f"missing required root path: {required}")

pack_root = ROOT / "modules" / "packs"
policy_root = ROOT / "modules" / "policies"
profile_root = ROOT / "modules" / "profiles"

for path in [pack_root, policy_root, profile_root]:
    if not path.is_dir():
        fail(f"missing module family: {path.relative_to(ROOT)}/")

packs = {p.name for p in pack_root.iterdir() if p.is_dir()} if pack_root.is_dir() else set()
policies = {p.stem for p in policy_root.glob("*.md") if p.name != "README.md"} if policy_root.is_dir() else set()
profiles = {p.name for p in profile_root.iterdir() if p.is_dir()} if profile_root.is_dir() else set()

for pack in sorted(packs):
    if not (pack_root / pack / "PACK.md").is_file():
        fail(f"pack missing PACK.md: modules/packs/{pack}")

manifest_path = pack_root / "manifest.json"
if manifest_path.is_file():
    manifest = load_json(manifest_path)
    if isinstance(manifest, dict):
        declared = set((manifest.get("modules") or {}).keys())
        if declared != packs:
            fail(f"pack manifest mismatch: declared={sorted(declared)} actual={sorted(packs)}")
else:
    fail("missing modules/packs/manifest.json")

boilerplates: dict[str, dict] = {}
for name in sorted(EXPECTED_BOILERPLATES):
    directory = ROOT / name
    metadata_path = directory / "boilerplate.json"
    if not directory.is_dir():
        fail(f"missing boilerplate directory: {name}/")
        continue
    if not metadata_path.is_file():
        fail(f"missing boilerplate metadata: {name}/boilerplate.json")
        continue
    data = load_json(metadata_path)
    if not isinstance(data, dict):
        continue
    boilerplates[name] = data
    if data.get("name") != name:
        fail(f"boilerplate name mismatch in {name}/boilerplate.json")
    if data.get("format_version") != 1:
        fail(f"unsupported format_version in {name}/boilerplate.json")
    version = data.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        fail(f"invalid version in {name}/boilerplate.json: {version!r}")
    for pack in data.get("default_packs", []):
        if pack not in packs:
            fail(f"{name} references unknown pack: {pack}")

for name, data in boilerplates.items():
    parent = data.get("extends")
    if parent is not None and parent not in boilerplates:
        fail(f"{name} extends unknown boilerplate: {parent}")

for start in boilerplates:
    seen: set[str] = set()
    current = start
    while current in boilerplates and boilerplates[current].get("extends"):
        if current in seen:
            fail(f"boilerplate inheritance cycle involving {start}")
            break
        seen.add(current)
        current = boilerplates[current]["extends"]

base = boilerplates.get("base", {})
for rel in base.get("required_core", []):
    if not (ROOT / "base" / rel).exists():
        fail(f"base required_core missing: base/{rel}")

for preset_path in sorted((ROOT / "presets").glob("*.json")):
    data = load_json(preset_path)
    if not isinstance(data, dict):
        continue
    boilerplate = data.get("boilerplate")
    if boilerplate not in boilerplates:
        fail(f"{preset_path.relative_to(ROOT)} references unknown boilerplate: {boilerplate}")
    for pack in data.get("packs", []):
        if pack not in packs:
            fail(f"{preset_path.relative_to(ROOT)} references unknown pack: {pack}")
    for policy in data.get("policies", []):
        if policy not in policies:
            fail(f"{preset_path.relative_to(ROOT)} references unknown policy: {policy}")
    profile = data.get("profile")
    if profile is not None and profile not in profiles:
        fail(f"{preset_path.relative_to(ROOT)} references unknown profile: {profile}")

for profile in sorted(profiles):
    path = profile_root / profile / "profile.json"
    if not path.is_file():
        fail(f"profile missing profile.json: modules/profiles/{profile}")
        continue
    data = load_json(path)
    if not isinstance(data, dict):
        continue
    for pack in data.get("packs", []):
        if pack not in packs:
            fail(f"profile {profile} references unknown pack: {pack}")
    for policy in data.get("policies", []):
        if policy not in policies:
            fail(f"profile {profile} references unknown policy: {policy}")

for schema_path in sorted((ROOT / "schema").glob("*.json")):
    load_json(schema_path)

if errors:
    print("Catalog validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(f"Catalog valid: {len(boilerplates)} boilerplates, {len(packs)} packs, {len(policies)} policies, {len(profiles)} profiles")
