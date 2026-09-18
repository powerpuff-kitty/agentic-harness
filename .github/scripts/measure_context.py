#!/usr/bin/env python3
"""Measure authored context trees; does not simulate CLI composition or tokens."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STARTUP = ("AGENTS.md", ".agentic/README.md", ".agentic/manifest.yaml")


def measure(path: Path) -> dict:
    files = sorted(p for p in path.rglob("*") if p.is_file())
    contents = [p.read_bytes() for p in files]
    startup = [(path / name).read_bytes() for name in STARTUP]
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "files": len(files),
        "utf8_bytes": sum(len(content) for content in contents),
        "whitespace_words": sum(len(content.decode("utf-8").split()) for content in contents),
        "startup_route_files": len(STARTUP),
        "startup_route_utf8_bytes": sum(len(content) for content in startup),
        "startup_route_whitespace_words": sum(len(content.decode("utf-8").split()) for content in startup),
    }


def main() -> None:
    paths = sorted((ROOT / "catalog/variants").glob("*/files"))
    paths.append(ROOT / ".agentic/evals/fixtures/context/reading-list")
    print(json.dumps({
        "scope": "authored source trees; excludes CLI-added modules, skills and host adapters",
        "startup_scope": "router/map/manifest only; task-specific truth and mandatory policies are additional",
        "trees": [measure(path) for path in paths],
    }, indent=2))


if __name__ == "__main__":
    main()
