#!/usr/bin/env python3
"""Validate selection paths and references without composing target projects."""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
CORE = {
    "README.md", "AGENTS.md", ".agentic/README.md", ".agentic/manifest.yaml",
    ".agentic/lock.json", ".agentic/PRODUCT.md", ".agentic/ARCHITECTURE.md",
    ".agentic/SECURITY.md", ".agentic/THIRD_PARTY_NOTICES.md",
    ".agentic/decisions/README.md", ".agentic/decisions/index.yaml",
    ".agentic/decisions/ADR-000-template.md",
}


def validate(root: Path, data: dict) -> list[str]:
    errors = []
    if (set(data) != {"format_version", "kind", "default", "minimal"}
            or type(data.get("format_version")) is not int or data["format_version"] != 1
            or data.get("kind") != "context-profiles" or data.get("default") != "full"):
        return ["invalid context profile header"]
    minimal = data.get("minimal")
    required = {"core_files", "design_variants", "design_packs", "design_fallback_variant", "module_routers"}
    if not isinstance(minimal, dict) or set(minimal) != required:
        return ["invalid minimal context profile fields"]
    for key in ("core_files", "design_variants", "design_packs"):
        values = minimal[key]
        if (not isinstance(values, list) or not all(isinstance(v, str) for v in values)
                or len(set(values)) != len(values)):
            return [f"invalid or duplicate context selection: {key}"]
    paths = minimal["core_files"]
    if set(paths) != CORE:
        errors.append("minimal profile must retain the exact 12-file core")
    routers = minimal["module_routers"]
    if routers != {"packs": ".agentic/packs/README.md", "policies": ".agentic/policies/README.md",
                   "skills": ".agents/skills/README.md"}:
        return errors + ["invalid module routers"]
    for relative in paths + list(routers.values()):
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or "\\" in relative or ":" in relative:
            return errors + ["unsafe context selection path"]
    variants = json.loads((root / "catalog/manifest.json").read_text())["variants"]
    for name in variants:
        for relative in paths + list(routers.values()):
            if not (root / "catalog/variants" / name / "files" / relative).is_file():
                errors.append(f"missing selected file in variant {name}: {relative}")
    if not set(minimal["design_variants"]).issubset(variants):
        errors.append("unknown visual variant")
    fallback = minimal["design_fallback_variant"]
    if not isinstance(fallback, str) or fallback not in variants:
        errors.append("unknown design fallback variant")
    elif not (root / "catalog/variants" / fallback / "files/.agentic/DESIGN.md").is_file():
        errors.append("missing fallback design context")
    packs = json.loads((root / "catalog/packs/manifest.json").read_text())["modules"]
    if not set(minimal["design_packs"]).issubset(packs):
        errors.append("unknown design pack")
    template = (root / "catalog/context/minimal-map.md").read_text()
    if any(template.count(marker) != 1 for marker in ("{{routes}}", "{{modules}}")):
        errors.append("minimal map requires exactly one routes and modules placeholder")
    return errors


if __name__ == "__main__":
    failures = validate(ROOT, json.loads((ROOT / "catalog/context/profiles.v1.json").read_text()))
    if failures:
        raise SystemExit("\n".join(failures))
    print("Context profile paths, budget and references valid")
