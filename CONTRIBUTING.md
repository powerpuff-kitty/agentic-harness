# Contributing

Changes should preserve the repository boundaries: templates are generated project shape, packs are knowledge, skills are procedures, schemas are machine contracts, and scripts are deterministic enforcement.

Before opening a PR run:

```bash
python3 -m py_compile scripts/*.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_repo.py .
python3 scripts/agentic_audit.py templates/base
python3 scripts/security_scan.py .
```

New skills require `skills/<name>/SKILL.md`; new packs require `packs/<name>/PACK.md` and a manifest entry. Avoid adding third-party runtime dependencies unless the capability cannot reasonably be implemented with the standard library and the tradeoff is documented.
