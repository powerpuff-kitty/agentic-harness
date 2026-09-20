# Repository discovery

Inspect before asking questions.

1. Detect the repository root, language/tooling manifests, source, tests, CI, deployment, and ownership files.
2. Read root `AGENTS.md` when present.
3. Inspect `.agentic/README.md`, `.agentic/manifest.yaml`, `.agentic/lock.json`, canonical truth, decisions, installed packs/policies, and relevant docs.
4. Inspect `.agents/skills/` and vendor adapters without treating them as project truth.
5. Detect legacy root-level truth, `agentic.yaml`, `docs/decisions`, `docs/plans`, `docs/tasks`, or root `evals`; report migration state rather than assuming both layouts are valid.
6. Identify duplicate/conflicting canonical documents, stale router links, declared-but-missing modules, and maturity requirements.
7. Separate repository facts, evidence-based inference, unresolved decisions, and information that requires the user.
