# Agentic Harness

A composable framework for designing, generating, governing, auditing, and maintaining agent-native software projects.

## Native Rust CLI

Agentic Harness is implemented as a Rust CLI and ships as the `ah` binary. End users do not need Python, Node.js, or a Rust runtime when using a precompiled release binary.

```bash
ah init ./app --template web-app
ah init ./saas --preset vue-saas --name my-saas --maturity production
ah init ./api --template backend-api --pack postgres
ah upgrade ./existing --template monorepo
ah audit ./existing > audit.json
ah compare before.json after.json
ah gate audit.json --min-overall 80 --min-score security=80
ah validate .
ah security-scan .
ah harness-audit templates/base
```

The binary embeds templates, presets, packs, and skills at compile time, so generated repositories do not depend on a Python runtime or on source-repository paths.

## Installation

Precompiled release binaries are the preferred distribution mechanism. From a source checkout, `./ah` runs an existing Rust build or falls back to `cargo run` when Cargo is available.

To install an existing binary globally:

```bash
./install.sh --binary /path/to/ah
```

If `ah` is already used on the machine, choose another command name:

```bash
./install.sh --binary /path/to/ah --command agentic
./install.sh --binary /path/to/ah --command agh
AGENTIC_HARNESS_COMMAND=my-ah ./install.sh --binary /path/to/ah
```

When building from source:

```bash
cargo build --release
./install.sh
```

Rust is required only to build from source, not to run a precompiled binary.

## Composition model

```text
template   = initial repository shape
preset     = named template + packs + skills composition
pack       = knowledge and constraints
skill      = repeatable procedure
example    = accepted outcome
eval       = success measurement
schema     = machine contract
Rust CLI   = deterministic composition, audits, validation and gates
```

Templates currently include `base`, `web-app`, `backend-api`, `saas`, `monorepo`, and `library-sdk`. Templates inherit from `base` (or another template) and add focused overlays, avoiding duplicated boilerplate. Presets currently include `vue-saas`, `api-postgres`, and `secure-saas`.

`INIT` may apply template overlays because it creates a new repository. `UPGRADE` preserves existing files and only fills missing template content. Explicitly selected packs and skills are installed into `.agentic/packs/` and `.agents/skills/`.

## Repository shape

```text
.
├── Cargo.toml
├── src/
│   └── main.rs
├── ah
├── install.sh
├── templates/
├── presets/
├── packs/
├── skills/
├── schema/
├── docs/
└── .github/workflows/
```

The former Python implementation and Python test suite have been removed. `cargo test` is the canonical deterministic test command.

Use `skills/agentic-app/SKILL.md` for guided INIT/UPGRADE and `skills/codebase-audit/SKILL.md` for evidence-backed repository audits. Security covers both conventional application risks and agent-specific risks such as prompt injection, excessive tool permissions, data exfiltration, unsafe generated code, untrusted retrieval, and destructive actions.
