# Agentic Harness

A composable framework for designing, generating, governing, auditing, and maintaining agent-native software projects.

## CLI

The default local command is `ah`:

```bash
./ah init ./app --template web-app
./ah init ./saas --preset vue-saas --name my-saas --maturity production
./ah init ./api --template backend-api --pack postgres
./ah upgrade ./existing --template monorepo
./ah audit ./existing > audit.json
./ah compare before.json after.json
./ah gate audit.json --min-overall 80 --min-score security=80
```

Install a global command with:

```bash
./install.sh
```

If `ah` is already used on the machine, choose any safe alias:

```bash
./install.sh --command agentic
./install.sh --command agh
AGENTIC_HARNESS_COMMAND=my-ah ./install.sh
```

The executable name is intentionally configurable. The CLI derives its displayed program name from the executable that launched it, so `ah --help` shows `ah ...`, while an installed alias such as `agentic --help` shows `agentic ...`.

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
├── ah
├── install.sh
├── templates/
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
