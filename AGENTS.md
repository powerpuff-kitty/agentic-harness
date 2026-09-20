# Agent instructions

This repository is a self-hosting Agentic Harness project and the canonical catalog source.

1. Read [`.agentic/README.md`](.agentic/README.md) for the project-context map.
2. Read [`.agentic/manifest.yaml`](.agentic/manifest.yaml) for paths, modules, permissions, and source ownership.
3. Load only the relevant canonical truth, ADRs, supporting docs, packs, policies, and skills.
4. Apply precedence: policies; current project truth; accepted ADRs; packs; skills; one-off prompts.
5. `catalog/` owns reusable variants and modules. Changes to the target-project contract must update schemas, validation, ADRs/current truth, agent procedures, CLI source pins, and migration tests as applicable.
6. Do not recreate legacy root-level project truth, `docs/decisions`, hidden overlay-only public variants, or duplicated vendor instructions.
7. Preserve project-authored truth, keep changes scoped and reversible, and never expose secrets or perform destructive/release actions without the approvals in the manifest.
8. Run catalog validation and relevant downstream tests before declaring a cross-repository change complete.
9. State unresolved compatibility, migration, security, and validation gaps explicitly.
10. Follow the [public-surface policy](.agentic/docs/project/public-surface.md) for files and collaboration metadata; never identify internal consumers in public content or fixtures.
11. For bounded evidence-support judgments or typed task classification, use [decision-intelligence](.agents/skills/decision-intelligence/SKILL.md); for instruction/context optimisation, use [agentic-improvement](.agents/skills/agentic-improvement/SKILL.md). These are conditional procedures, not mandatory wrappers for ordinary tasks.
12. For actual TypeSafe/Jev integration, use the independently installed [TypeSafe skill](.agents/skills/typesafe-ai/SKILL.md) and its live-documentation workflow. Guidance alone does not require a provider call. Deterministic rules and authorisation remain project-owned.
13. For lifecycle, review, documentation or explicitly approved release work, select the relevant procedure from the [installed skill index](.agents/skills/README.md); do not load the whole collection.

Vendor adapters must remain thin and point back to this file and `.agentic/`; they may not redefine canonical architecture.
