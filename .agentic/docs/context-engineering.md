# Context engineering standard

Agentic Harness uses progressive disclosure: give an agent the smallest relevant context that lets it complete the current task safely and correctly.

## Canonical rules

1. Keep root `AGENTS.md` compact. It is an entrypoint and precedence map, not a complete operating manual.
2. Route from `AGENTS.md` to `.agentic/README.md` or an equivalent index, then load only task-relevant truth.
3. Do not require agents to read every architecture, design, security, testing, deployment, or decision document for routine work.
4. Skill descriptions must be narrow and trigger-oriented. A skill should say when it applies, not advertise itself for an entire domain.
5. Large procedures use progressive disclosure: `SKILL.md` remains concise and links to supporting references, scripts, or checklists that are loaded only when needed.
6. Prefer outcome-oriented constraints and completion conditions over step-by-step recipes when the model can safely choose the execution path.
7. Project truth is model- and vendor-independent. Vendor/model adapters may alter presentation, context density, or capability guidance, but may not redefine architecture, business rules, security policy, or accepted decisions.
8. Safe autonomy must be explicit. Agents should know which actions may be taken without approval and which require a user decision.
9. Completion must be explicit. A task is not complete merely because code was generated.

## Context routing pattern

A project context map should route by task signal, for example:

- frontend structure or module boundaries -> `.agentic/ARCHITECTURE.md`
- visual/UI changes -> `.agentic/DESIGN.md`
- auth, secrets, permissions, destructive operations -> `.agentic/SECURITY.md`
- accepted architectural/business choices -> `.agentic/decisions/`
- implementation plans -> `.agentic/plans/`
- reusable project procedures -> `.agents/skills/`

Routes should be conditional. Avoid instructions such as "read all files under `.agentic/` before every change."

## Completion contract

Unless a stricter project policy applies, completion means:

- the requested behavior is implemented;
- affected tests/validation have been run where available;
- relevant regressions found during verification are fixed or surfaced;
- unsafe/destructive actions were not taken without required approval;
- durable project truth or decision records are updated when the change alters them;
- unresolved compatibility, security, migration, or validation gaps are stated explicitly.

## Safe autonomy

Projects should separate:

- **allowed without approval:** local inspection, targeted edits, non-destructive validation, focused tests, documentation updates that reflect an already-approved change;
- **approval required:** destructive data operations, production/release actions, secret access/exposure, irreversible migrations, policy/business changes, or broad rewrites not implied by the task.

## Good and bad skill triggers

Bad:

> Database expert. Use for databases, SQL, persistence, PostgreSQL, backend work, and migrations.

Good:

> Create or review PostgreSQL schema migrations. Use when a task adds, modifies, rolls back, or validates a migration.

## Anti-patterns

- mandatory full-repository reading;
- duplicated rules in `AGENTS.md`, vendor files, skills, and docs;
- broad overlapping skills competing for the same task;
- model-specific project truth;
- recipes that unnecessarily constrain a capable model;
- completion rules that stop at "implementation produced" rather than verified outcome.
