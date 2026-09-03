#!/usr/bin/env python3
"""Lightweight structural audit for the agentic-app harness. Stdlib only."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORE = [
    "AGENTS.md", "agentic.yaml", "PRODUCT.md", "ARCHITECTURE.md",
    "DESIGN.md", "REFERENCE.md", "SECURITY.md", "skill/SKILL.md",
    "docs/decisions", "docs/plans", "evals", "examples", "packs",
]

RECOMMENDED = [
    "docs/testing", "docs/operations", "docs/research", "docs/tasks",
    "skill/references/repository-discovery.md",
    "skill/references/setup-questionnaire.md",
    "skill/references/security-for-agents.md",
]


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def main() -> int:
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
