#!/usr/bin/env python3
"""Lightweight structural audit for a composed agentic-app repository. Stdlib only."""
from __future__ import annotations
import json
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = SOURCE_ROOT / "templates" / "base"
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_TARGET

CORE = [
    "AGENTS.md", "agentic.yaml", "PRODUCT.md", "ARCHITECTURE.md",
    "DESIGN.md", "REFERENCE.md", "SECURITY.md",
    "docs/decisions", "docs/plans", "evals", "examples",
]

RECOMMENDED = [
    "docs/testing", "docs/operations", "docs/research", "docs/tasks",
]


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def main() -> int:
    if not ROOT.exists():
        print(json.dumps({"error": f"target does not exist: {ROOT}"}, indent=2))
        return 2

    present = [p for p in CORE if exists(p)]
    missing = [p for p in CORE if not exists(p)]
    weak = [p for p in RECOMMENDED if not exists(p)]

    conflicts = []
    adapters = ["CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"]
    for adapter in adapters:
        p = ROOT / adapter
        if p.exists() and p.stat().st_size > 6000:
            conflicts.append(f"{adapter} is large; verify it is a thin adapter rather than duplicated canonical guidance")

    score = max(0, round(100 * (len(present) / len(CORE)) - min(20, len(weak) * 2) - min(20, len(conflicts) * 5)))
    result = {
        "target": str(ROOT),
        "score": score,
        "present": present,
        "weak": weak,
        "missing": missing,
        "conflicting": conflicts,
        "recommendations": [f"Add or resolve {p}" for p in missing + weak],
        "detected_stack": {},
        "recommended_packs": [],
        "unresolved_questions": [],
    }
    print(json.dumps(result, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
