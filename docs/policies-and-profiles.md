# Policies and Profiles

Agentic Harness layers now have distinct responsibilities:

- **template** — initial repository shape
- **pack** — technical/domain knowledge and constraints
- **skill** — repeatable procedure
- **policy** — mandatory must/must-not rule
- **profile** — organization/team defaults that compose packs, skills and policies
- **preset** — project-type composition, usually template + packs + skills
- **eval/test/schema** — deterministic evidence and contracts

Profiles are intended for defaults such as startup, enterprise, agency, and open-source. Policies remain explicit project artifacts after installation so agents can inspect the exact rules applying to the repository.
