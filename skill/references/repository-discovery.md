# Repository Discovery

Before INIT/UPGRADE, inspect enough of the repository to build a map without loading everything.

Detect:
- package/workspace manifests and language/toolchain files
- apps, packages, services, libraries, generated code, and monorepo boundaries
- frontend/backend/mobile/runtime frameworks
- data stores, migrations, schemas, queues, caches, object storage
- APIs, events, jobs, background workers
- tests, linters, type checks, build commands
- CI/CD, deployment targets, infrastructure-as-code
- auth, permissions, secrets/config patterns
- design-system code and tokens
- existing docs, ADRs, agent instructions, rules, skills, examples, evals

Output an internal repository map and use it to decide what documentation is actually needed.

For monorepos, propose nested `AGENTS.md` only where a subtree has materially different commands, architecture, constraints, or ownership. Do not create one per folder mechanically.
