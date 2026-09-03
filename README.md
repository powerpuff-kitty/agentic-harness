# Agentic Repo Harness

A composable development harness for making software repositories agent-native, governable, auditable, and secure.

## CLI

```bash
./arh init ./app --template web-app
./arh init ./saas --preset vue-saas --name my-saas --maturity production
./arh init ./api --template backend-api --pack postgres
./arh upgrade ./existing --template monorepo
./arh audit ./existing > audit.json
./arh compare before.json after.json
./arh gate audit.json --min-overall 80 --min-score security=80
```

## Composition model

```text
template   = initial repository shape
preset     = named template + packs + skills composition
pack       = knowledge and constraints
skill      = repeatable procedure
example    = accepted outcome
eval       = success measurement
schema     = machine contract
script     = deterministic enforcement
```

Templates currently include `base`, `web-app`, `backend-api`, `saas`, `monorepo`, and `library-sdk`. Templates inherit from `base` (or another template) and add focused overlays, avoiding duplicated boilerplate. Presets currently include `vue-saas`, `api-postgres`, and `secure-saas`.

`INIT` may apply template overlays because it creates a new repository. `UPGRADE` preserves existing files and only fills missing template content. Explicitly selected packs and skills are installed into `.agentic/packs/` and `.agents/skills/`.

## Repository shape

```text
.
├── arh
├── templates/
│   ├── base/
│   ├── web-app/
│   ├── backend-api/
│   ├── saas/
│   ├── monorepo/
│   └── library-sdk/
├── presets/
├── packs/
├── skills/
├── schema/
├── scripts/
├── tests/
├── docs/
└── .github/workflows/
```

Use `skills/agentic-app/SKILL.md` for guided INIT/UPGRADE and `skills/codebase-audit/SKILL.md` for evidence-backed repository audits. Security covers both conventional application risks and agent-specific risks such as prompt injection, excessive tool permissions, data exfiltration, unsafe generated code, untrusted retrieval, and destructive actions.
