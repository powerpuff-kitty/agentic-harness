# Contributing

Read `AGENTS.md`, `.agentic/README.md`, relevant current truth and accepted ADRs before changing a contract.

Repository boundaries:

- `.agentic/` owns this repository's accepted project context.
- `catalog/variants/` contains materialized project-context templates, not application starters.
- Catalog packs/policies/profiles/presets contain reusable guidance and composition selections.
- `catalog/schema/` owns public machine contracts.

Before opening a PR:

```bash
python3 -m unittest discover -s .github/scripts -p 'test_public_surface.py'
python3 .github/scripts/validate_catalog.py
```

The validation entrypoint checks public text/quick-start consistency and then runs the original structural checks. Neither proves installed CLI behavior, policy enforcement or successful model tasks. Run relevant downstream tests and report unavailable checks explicitly.

A contract change must update applicable schemas, current truth/ADRs, migration guidance and downstream source pins/tests. Do not recreate root-level project truth or overlay-only public variants. Preserve user-authored content and keep vendor adapters thin but functional.

Follow the [public-surface policy](.agentic/docs/project/public-surface.md) in source, examples, diagrams, issue bodies, comments and PR descriptions. Public fixtures must be synthetic or explicitly approved; do not identify internal consumers. Review public allowlist changes rather than weakening the check to make it pass.

Agent procedures belong in `agentic-harness-agents`; deterministic application mechanics belong in `agentic-harness-cli`. The public remediation roadmap prioritizes complete, tested workflows over inventory growth. No new workflow infrastructure is required for these checks.

Submit contributions under MIT and retain third-party attribution.
