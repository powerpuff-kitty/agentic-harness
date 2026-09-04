#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VARIANTS = {"base", "web-app", "backend-api", "saas", "monorepo", "library-sdk"}
LEGACY_ROOTS = {
    "base", "web-app", "backend-api", "saas", "monorepo", "library-sdk",
    "boilerplates", "templates", "modules", "presets", "schema", "docs",
    "packs", "policies", "profiles", "examples", "marketing", "crates", "packages",
}
LEGACY_TRUTH = {"PRODUCT.md", "ARCHITECTURE.md", "DESIGN.md", "REFERENCE.md", "agentic.yaml"}
CORE_CONTEXT = {"README.md", "manifest.yaml", "lock.json", "PRODUCT.md", "ARCHITECTURE.md", "SECURITY.md", "decisions"}
CORE_TARGET = {"README.md", "AGENTS.md", ".agentic"}
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
ADR_NAME = re.compile(r"^ADR-(\d{3,})-[a-z0-9][a-z0-9-]*\.md$")
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return None


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"unreadable text {path.relative_to(ROOT)}: {exc}")
        return ""


def yaml_list_values(path: Path, key: str) -> list[str]:
    values: list[str] = []
    lines = text(path).splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{key}:":
            continue
        indent = len(line) - len(line.lstrip())
        for candidate in lines[index + 1 :]:
            stripped = candidate.strip()
            if not stripped:
                continue
            current_indent = len(candidate) - len(candidate.lstrip())
            if current_indent <= indent:
                break
            if stripped.startswith("- "):
                values.append(stripped[2:].strip().strip('"\''))
        break
    return values


def validate_adr_directory(directory: Path) -> None:
    required = [directory / "README.md", directory / "index.yaml", directory / "ADR-000-template.md"]
    for path in required:
        if not path.is_file():
            fail(f"missing ADR artifact: {path.relative_to(ROOT)}")
    index = directory / "index.yaml"
    if not index.is_file():
        return
    index_text = text(index)
    indexed = set(re.findall(r"^\s*file:\s*(ADR-\d{3,}-[a-z0-9-]+\.md)\s*$", index_text, re.MULTILINE))
    actual = {p.name for p in directory.glob("ADR-*.md") if p.name != "ADR-000-template.md"}
    if indexed != actual:
        fail(f"ADR index mismatch in {directory.relative_to(ROOT)}: indexed={sorted(indexed)} actual={sorted(actual)}")
    for path in directory.glob("ADR-*.md"):
        if path.name == "ADR-000-template.md":
            continue
        match = ADR_NAME.match(path.name)
        if not match:
            fail(f"invalid ADR filename: {path.relative_to(ROOT)}")
            continue
        body = text(path)
        expected = f"# ADR-{match.group(1)}:"
        if not body.startswith(expected):
            fail(f"ADR heading does not match filename: {path.relative_to(ROOT)}")
        status = re.search(r"^- Status:\s*(\S+)", body, re.MULTILINE)
        if not status or status.group(1) not in {"proposed", "accepted", "rejected", "deprecated", "superseded"}:
            fail(f"invalid ADR status: {path.relative_to(ROOT)}")


def validate_target(target: Path, variant: str) -> None:
    for item in CORE_TARGET:
        if not (target / item).exists():
            fail(f"{variant} target missing {item}")
    for legacy in LEGACY_TRUTH:
        if (target / legacy).exists():
            fail(f"{variant} target leaks canonical truth at root: {legacy}")
    context = target / ".agentic"
    for item in CORE_CONTEXT:
        if not (context / item).exists():
            fail(f"{variant} target missing .agentic/{item}")
    router = text(target / "AGENTS.md")
    if ".agentic/README.md" not in router or ".agentic/manifest.yaml" not in router:
        fail(f"{variant} AGENTS.md is not a valid router")
    manifest = text(context / "manifest.yaml")
    for token in ["format_version: 1", "project:", "context:", "modules:", "permissions:", "canonical_router:"]:
        if token not in manifest:
            fail(f"{variant} manifest missing {token}")
    if f"type: {variant}" not in manifest and variant != "base":
        fail(f"{variant} manifest does not declare its type")
    lock = load_json(context / "lock.json")
    if isinstance(lock, dict) and lock.get("format_version") != 1:
        fail(f"{variant} lockfile format_version must be 1")
    validate_adr_directory(context / "decisions")
    for directory in ["plans", "tasks", "docs", "evals", "packs", "policies"]:
        path = context / directory
        if path.exists() and not (path / "README.md").is_file():
            fail(f"{variant} .agentic/{directory} missing README.md")
    copilot = target / ".github" / "copilot-instructions.md"
    if copilot.exists():
        adapter = text(copilot)
        if "AGENTS.md" not in adapter or ".agentic" not in adapter or len(adapter) > 1000:
            fail(f"{variant} Copilot adapter is not thin/canonical")


for name in sorted(LEGACY_ROOTS):
    if (ROOT / name).exists():
        fail(f"deprecated root path exists: {name}/")
for name in LEGACY_TRUTH:
    if (ROOT / name).exists():
        fail(f"canonical project truth must not be at root: {name}")
for path in [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / ".agentic", ROOT / "catalog"]:
    if not path.exists():
        fail(f"missing required root path: {path.relative_to(ROOT)}")

validate_target(ROOT, "self")
if len(list((ROOT / ".agentic" / "decisions").glob("ADR-*.md"))) < 6:
    fail("self-hosting project must include real ADR examples, not only the template")

catalog = ROOT / "catalog"
manifest = load_json(catalog / "manifest.json")
if isinstance(manifest, dict):
    if manifest.get("format_version") != 1:
        fail("catalog manifest format_version must be 1")
    if set(manifest.get("variants", [])) != VARIANTS:
        fail("catalog manifest variant list mismatch")

pack_root = catalog / "packs"
policy_root = catalog / "policies"
profile_root = catalog / "profiles"
preset_root = catalog / "presets"
variant_root = catalog / "variants"
schema_root = catalog / "schema"

packs = {p.name for p in pack_root.iterdir() if p.is_dir()} if pack_root.is_dir() else set()
policies = {p.stem for p in policy_root.glob("*.md") if p.name != "README.md"} if policy_root.is_dir() else set()
profiles = {p.name for p in profile_root.iterdir() if p.is_dir()} if profile_root.is_dir() else set()

for pack in sorted(packs):
    if not (pack_root / pack / "PACK.md").is_file():
        fail(f"pack missing PACK.md: catalog/packs/{pack}")
pack_manifest = load_json(pack_root / "manifest.json")
if isinstance(pack_manifest, dict):
    declared = set((pack_manifest.get("modules") or {}).keys())
    if declared != packs:
        fail(f"pack manifest mismatch: declared={sorted(declared)} actual={sorted(packs)}")

variants: dict[str, dict] = {}
for name in sorted(VARIANTS):
    directory = variant_root / name
    metadata = load_json(directory / "variant.json")
    if not isinstance(metadata, dict):
        continue
    variants[name] = metadata
    if metadata.get("name") != name:
        fail(f"variant name mismatch: {name}")
    if metadata.get("format_version") != 1:
        fail(f"unsupported variant format: {name}")
    version = metadata.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        fail(f"invalid variant version {name}: {version!r}")
    parent = metadata.get("extends")
    if parent is not None and parent not in VARIANTS:
        fail(f"{name} extends unknown variant: {parent}")
    for pack in metadata.get("default_packs", []):
        if pack not in packs:
            fail(f"{name} references unknown pack: {pack}")
    for policy in metadata.get("default_policies", []):
        if policy not in policies:
            fail(f"{name} references unknown policy: {policy}")
    validate_target(directory / "files", name)

for start in variants:
    seen: set[str] = set()
    current = start
    while current in variants and variants[current].get("extends"):
        if current in seen:
            fail(f"variant inheritance cycle involving {start}")
            break
        seen.add(current)
        current = variants[current]["extends"]

for preset_path in sorted(preset_root.glob("*.json")):
    data = load_json(preset_path)
    if not isinstance(data, dict):
        continue
    if data.get("format_version") != 1:
        fail(f"preset missing format_version 1: {preset_path.relative_to(ROOT)}")
    if data.get("boilerplate") not in VARIANTS:
        fail(f"preset references unknown boilerplate: {preset_path.relative_to(ROOT)}")
    for pack in data.get("packs", []):
        if pack not in packs:
            fail(f"preset references unknown pack {pack}: {preset_path.relative_to(ROOT)}")
    for policy in data.get("policies", []):
        if policy not in policies:
            fail(f"preset references unknown policy {policy}: {preset_path.relative_to(ROOT)}")

for profile in sorted(profiles):
    data = load_json(profile_root / profile / "profile.json")
    if not isinstance(data, dict):
        continue
    for pack in data.get("packs", []):
        if pack not in packs:
            fail(f"profile {profile} references unknown pack: {pack}")
    for policy in data.get("policies", []):
        if policy not in policies:
            fail(f"profile {profile} references unknown policy: {policy}")

required_schemas = {"manifest.schema.json", "lock.schema.json", "variant.schema.json", "adr-index.schema.json", "migration-report.schema.json", "codebase-audit.schema.json", "profile.schema.json"}
for name in required_schemas:
    if not (schema_root / name).is_file():
        fail(f"missing schema: catalog/schema/{name}")
for schema_path in sorted(schema_root.glob("*.json")):
    load_json(schema_path)

root_adapter = ROOT / ".github" / "copilot-instructions.md"
if root_adapter.exists():
    adapter = text(root_adapter)
    if "AGENTS.md" not in adapter or ".agentic" not in adapter or len(adapter) > 1000:
        fail("root Copilot adapter is not thin/canonical")

if errors:
    print("Catalog validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"Catalog valid: {len(variants)} variants, {len(packs)} packs, "
    f"{len(policies)} policies, {len(profiles)} profiles; self-hosting contract valid"
)
