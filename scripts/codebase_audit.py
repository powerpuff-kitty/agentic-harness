#!/usr/bin/env python3
"""Portable stdlib-only baseline codebase audit.

Reports structural evidence only. It deliberately does not claim vulnerability,
coverage, performance, or runtime correctness without executing dedicated tools.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKIP = {".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt", "target", ".venv", "venv", "coverage"}
CODE_EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".rs", ".go", ".java", ".kt", ".swift", ".rb", ".php", ".cs", ".c", ".cc", ".cpp", ".h", ".hpp"}
DOC_EXT = {".md", ".mdx", ".rst", ".txt"}
MANIFESTS = {"package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json"}
LOCKFILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "uv.lock", "poetry.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not any(part in SKIP for part in path.relative_to(root).parts):
            yield path


def safe_text(path: Path) -> str:
    try:
        if path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def audit(root: Path) -> dict:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(root)

    files = list(iter_files(root))
    code = [p for p in files if p.suffix.lower() in CODE_EXT]
    docs = [p for p in files if p.suffix.lower() in DOC_EXT]
    manifests = [p for p in files if p.name in MANIFESTS]
    lockfiles = [p for p in files if p.name in LOCKFILES]

    loc = 0
    large_files: list[str] = []
    todos = 0
    for path in code:
        text = safe_text(path)
        lines = text.splitlines()
        loc += len(lines)
        if len(lines) > 800:
            large_files.append(str(path.relative_to(root)))
        todos += len(re.findall(r"\b(?:TODO|FIXME|HACK|XXX)\b", text, flags=re.I))

    def rel(path: Path) -> str:
        return str(path.relative_to(root))

    tests = [p for p in files if re.search(r"(^|[/_.-])(test|tests|spec|specs)([/_.-]|$)", rel(p), re.I)]
    workflows = [p for p in files if rel(p).startswith(".github/workflows/")]
    agent_files = [p for p in files if p.name in {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "agentic.yaml"} or "/skills/" in f"/{rel(p)}"]
    security_files = [p for p in files if "security" in rel(p).lower()]
    ops_files = [p for p in files if any(term in rel(p).lower() for term in ("runbook", "deploy", "rollback", "observability", "monitor", "incident", "backup"))]

    exists_any = lambda *paths: any((root / p).exists() for p in paths)
    has_ci = bool(workflows)
    has_tests = bool(tests)
    has_docs = exists_any("README.md", "docs") or bool(docs)
    has_security = exists_any("SECURITY.md", "docs/security") or bool(security_files)
    has_agent = exists_any("AGENTS.md", "agentic.yaml") or bool(agent_files)
    has_ops = bool(ops_files)
    has_lock = not manifests or bool(lockfiles)

    scores = {
        "code_quality": clamp(75 - 5 * len(large_files) - min(15, todos)),
        "maintainability": clamp(72 - 4 * len(large_files) + (5 if has_docs else -8)),
        "architecture": clamp(78 if exists_any("ARCHITECTURE.md", "docs/architecture", "templates/base/ARCHITECTURE.md") else 58),
        "testing": clamp(78 if has_tests and has_ci else (62 if has_tests else 38)),
        "security": clamp((72 if has_security else 48) + (6 if has_ci else -5)),
        "performance": clamp(70 if exists_any("docs/performance.md", "benchmarks", "templates/base/docs/performance.md") else 55),
        "dependency_health": clamp((78 if has_lock else 58) + (4 if has_ci else 0)),
        "documentation": clamp(82 if has_docs else 42),
        "agent_docs": clamp(86 if has_agent else 50),
        "operations": clamp(76 if has_ops and has_ci else (60 if has_ci else 40)),
    }
    weights = {"code_quality": 12, "maintainability": 12, "architecture": 12, "testing": 12, "security": 16, "performance": 6, "dependency_health": 8, "documentation": 8, "agent_docs": 7, "operations": 7}
    overall = round(sum(scores[k] * weights[k] for k in weights) / sum(weights.values()))

    findings: list[dict] = []
    def finding(severity: str, dimension: str, message: str, evidence=None, recommendation=None):
        item = {"severity": severity, "dimension": dimension, "message": message}
        if evidence:
            item["evidence"] = evidence
        if recommendation:
            item["recommendation"] = recommendation
        findings.append(item)

    if not has_tests:
        finding("high", "testing", "No tests/spec files detected.", recommendation="Add repository-native automated tests and run them in CI.")
    if not has_ci:
        finding("high", "operations", "No GitHub Actions workflow detected.", recommendation="Add deterministic CI for build/test/lint/security checks.")
    if manifests and not lockfiles:
        finding("medium", "dependency_health", "Dependency manifest detected without a recognized lockfile.", [rel(p) for p in manifests], "Use reproducible locked installs when the ecosystem supports them.")
    if large_files:
        finding("medium", "maintainability", "Large code files (>800 lines) detected.", large_files[:20], "Review for justified decomposition; do not split mechanically.")
    if not has_security:
        finding("high", "security", "No security guidance/configuration detected.", recommendation="Add a security baseline and automated security checks appropriate to the stack.")
    if not has_ops:
        finding("medium", "operations", "No deployment/rollback/runbook/observability material detected.", recommendation="Add operational documentation before production use when applicable.")

    readiness = {
        "prototype": clamp(overall + 15),
        "startup": clamp(overall + (3 if has_tests and has_ci else -8)),
        "production": clamp(overall - (8 if has_tests and has_ci and has_security and has_ops else 20)),
        "critical": clamp(overall - (22 if has_tests and has_ci and has_security and has_ops else 35)),
    }

    return {
        "overall": overall,
        "target_maturity": "unknown",
        "scores": scores,
        "readiness": readiness,
        "profile": {
            "root": str(root), "files": len(files), "code_files": len(code), "code_loc": loc,
            "doc_files": len(docs), "tests_detected": len(tests), "workflows": len(workflows),
            "manifests": [rel(p) for p in manifests], "lockfiles": [rel(p) for p in lockfiles],
            "large_code_files": large_files, "todo_markers": todos,
        },
        "findings": findings,
        "checks": {
            "performed": ["repository structure", "file/LOC scan", "test/CI presence", "docs/security/agent/operations presence", "manifest/lockfile presence"],
            "not_checked": ["build execution", "test execution", "coverage", "dependency vulnerabilities", "SAST/secret scan", "runtime performance", "branch protection", "deployment environment", "external service configuration"],
        },
    }


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    try:
        result = audit(root)
    except FileNotFoundError:
        print(json.dumps({"error": f"target does not exist: {root.resolve()}"}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if any(f["severity"] in {"critical", "high"} for f in result["findings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
