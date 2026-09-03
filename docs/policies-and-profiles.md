# Policies and Profiles

Agentic Harness layers have distinct responsibilities:

- **boilerplate** — canonical initial repository shape
- **pack** — technical/domain knowledge and constraints
- **skill** — repeatable agent procedure (owned by `agentic-harness-agents`)
- **policy** — mandatory must/must-not rule
- **profile** — organization/team defaults that compose packs, skills, and policies
- **preset** — named composition, usually boilerplate + modules + skills
- **eval/test/schema** — evidence and machine contracts

In this repository, packs, policies, and profiles are grouped under `modules/` because they are reusable across the root boilerplates. Profiles provide defaults such as startup, enterprise, agency, and open source. Policies remain explicit project artifacts after installation so agents can inspect the exact rules applying to the target repository.
