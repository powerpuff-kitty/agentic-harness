#!/usr/bin/env python3
"""Portable stdlib-only baseline codebase audit.

This script intentionally reports structural evidence, not vulnerability/coverage claims.
Use the codebase-audit skill for deeper qualitative review and repository-native tools.
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKIP = {".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt", "target", ".venv", "venv", "coverage"}
CODE_EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".rs", ".go", ".java", ".kt", ".swift", ".rb", ".php", ".cs", ".c", ".cc", ".cpp", ".h", ".hpp"}
DOC_EXT = {".md", ".mdx", ".rst", ".txt"}


def files():
    for p in ROOT.rglob("*"):
        if p.is_file() and not any(part in SKIP for part in p.parts):
            yield p


def safe_text(p: Path) -> str:
    try:
        if p.stat().st_size > 2_000_000:
            return ""
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def exists_any(*paths: str) -> bool:
    return any((ROOT / p).exists() for p in paths)


def clamp(n):
    return max(0, min(100, round(n)))


def main() -> int:
    if not ROOT.exists():
        print(json.dumps({"error": f"target does not exist: {ROOT}"}, indent=2)); return 2

    fs = list(files())
    code = [p for p in fs if p.suffix.lower() in CODE_EXT]
    docs = [p for p in fs if p.suffix.lower() in DOC_EXT]
    manifests = [p for p in fs if p.name in {"package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json"}]
    lockfiles = [p for p in fs if p.name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "uv.lock", "poetry.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"}]

    loc = 0; large_files = []; todos = 0
    for p in code:
        text = safe_text(p); lines = text.splitlines(); loc += len(lines)
        if len(lines) > 800: large_files.append(str(p.relative_to(ROOT)))
        todos += len(re.findall(r"\b(?:TODO|FIXME|HACK|XXX)\b", text, flags=re.I))

    tests = [p for p in fs if re.search(r"(^|[/_.-])(test|tests|spec|specs)([/_.-]|$)", str(p.relative_to(ROOT)), re.I)]
    workflows = [p for p in fs if ".github/workflows" in p.as_posix()]
    agent_files = [p for p in fs if p.name in {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "agentic.yaml"} or "/skills/" in p.as_posix()]
    security_files = [p for p in fs if "security" in p.name.lower() or "/security" in p.as_posix().lower()]
    ops_files = [p for p in fs if any(x in p.as_posix().lower() for x in ["runbook", "deploy", "rollback", "observability", "monitor", "incident", "backup"])]

    has_ci = bool(workflows)
    has_tests = bool(tests)
    has_docs = exists_any("README.md", "docs") or bool(docs)
    has_security = exists_any("SECURITY.md", "docs/security") or bool(security_files)
    has_agent = exists_any("AGENTS.md", "agentic.yaml") or bool(agent_files)
    has_ops = bool(ops_files)
    has_lock = not manifests or bool(lockfiles)

    scores = {
        "code_quality": clamp(75 - 5*len(large_files) - min(15, todos)),
        "maintainability": clamp(72 - 4*len(large_files) + (5 if has_docs else -8)),
        "architecture": clamp(78 if exists_any("ARCHITECTURE.md", "docs/architecture") else 58),
        "testing": clamp(78 if has_tests and has_ci else (62 if has_tests else 38)),
        "security": clamp((72 if has_security else 48) + (6 if has_ci else -5)),
        "performance": clamp(70 if exists_any("docs/performance.md", "benchmarks") else 55),
        "dependency_health": clamp((78 if has_lock else 58) + (4 if has_ci else 0)),
        "documentation": clamp(82 if has_docs else 42),
        "agent_docs": clamp(86 if has_agent else 50),
        "operations": clamp(76 if has_ops and has_ci else (60 if has_ci else 40)),
    }
    weights = {"code_quality":12,"maintainability":12,"architecture":12,"testing":12,"security":16,"performance":6,"dependency_health":8,"documentation":8,"agent_docs":7,"operations":7}
    overall = round(sum(scores[k]*weights[k] for k in weights)/sum(weights.values()))

    findings = []
    def finding(sev, dim, msg, evidence=None, rec=None):
        item={"severity":sev,"dimension":dim,"message":msg}
        if evidence: item["evidence"]=evidence
        if rec: item["recommendation"]=rec
        findings.append(item)

    if not has_tests: finding("high","testing","No tests/spec files detected.", recommendation if False else None, "Add repository-native automated tests and run them in CI.")
    if not has_ci: finding("high","operations","No GitHub Actions workflow detected.", None, "Add deterministic CI for build/test/lint/security checks.")
    if manifests and not lockfiles: finding("medium","dependency_health","Dependency manifest detected without a recognized lockfile.", [str(p.relative_to(ROOT)) for p in manifests], "Use reproducible locked installs when the ecosystem supports them.")
    if large_files: finding("medium","maintainability","Large code files (>800 lines) detected.", large_files[:20], "Review for justified decomposition; do not split mechanically.")
    if not has_security: finding("high","security","No security guidance/configuration detected.", None, "Add a security baseline and automated security checks appropriate to the stack.")
    if not has_ops: finding("medium","operations","No deployment/rollback/runbook/observability material detected.", None, "Add operational documentation before production use.")

    readiness = {
        "prototype": clamp(overall + 15),
        "startup": clamp(overall + (3 if has_tests and has_ci else -8)),
        "production": clamp(overall - (8 if has_tests and has_ci and has_security and has_ops else 20)),
        "critical": clamp(overall - (22 if has_tests and has_ci and has_security and has_ops else 35)),
    }

    result = {
        "overall": overall,
        "target_maturity": "unknown",
        "scores": scores,
        "readiness": readiness,
        "profile": {"root":str(ROOT),"files":len(fs),"code_files":len(code),"code_loc":loc,"doc_files":len(docs),"tests_detected":len(tests),"workflows":len(workflows),"manifests":[str(p.relative_to(ROOT)) for p in manifests],"lockfiles":[str(p.relative_to(ROOT)) for p in lockfiles],"large_code_files":large_files,"todo_markers":todos},
        "findings": findings,
        "checks": {"performed":["repository structure","file/LOC scan","test/CI presence","docs/security/agent/operations presence","manifest/lockfile presence"],"not_checked":["build execution","test execution","coverage","dependency vulnerabilities","SAST/secret scan","runtime performance","branch protection","deployment environment","external service configuration"]}
    }
    print(json.dumps(result, indent=2))
    return 1 if any(f["severity"] in {"critical","high"} for f in findings) else 0

if __name__ == "__main__":
    raise SystemExit(main())
