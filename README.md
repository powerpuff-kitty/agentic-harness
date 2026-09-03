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

Agentic Harness sits on top of a new or existing software project. It does not replace the application framework, package manager, source tree, or CI system.

```text
project
  + template      initial repository shape
  + packs         reusable domain/technical knowledge and constraints
  + skills        repeatable agent procedures
  + presets       useful template + pack + skill compositions
  + project truth product / architecture / design / security / decisions
  + evals/tests   deterministic quality criteria
  + Rust CLI      composition, audits, validation and gates
  = agent-native governed project
```

Modules are package-like because they are reusable, versionable and composable, but they are not runtime dependencies. They are better understood as development-policy/context packages and project overlays. See `docs/composition-layers.md`.

Templates currently include `base`, `web-app`, `backend-api`, `saas`, `monorepo`, and `library-sdk`. Templates inherit from `base` (or another template) and add focused overlays, avoiding duplicated boilerplate. Presets currently include `vue-saas`, `api-postgres`, and `secure-saas`.

`INIT` may apply template overlays because it creates a new repository. `UPGRADE` preserves existing files and only fills missing template content. Explicitly selected packs and skills are installed into `.agentic/packs/` and `.agents/skills/`.

## Marketing layer

Marketing is deliberately separated from product and implementation truth. Agentic Harness now includes a reusable `marketing` pack and `marketing` skill, plus its own project marketing knowledge under `marketing/`.

A project using the marketing layer can maintain:

```text
marketing/
├── POSITIONING.md
├── MESSAGING.md
├── AUDIENCES.md
├── COMPETITORS.md
├── PRICING.md
├── LAUNCH.md
├── CHANNELS.md
├── CONTENT.md
└── FAQ.md
```

Use:

```bash
ah init ./product --template web-app --pack marketing --skill marketing
```

The marketing skill treats `PRODUCT.md` and other canonical product docs as authoritative for actual product behavior; marketing files control how that truth is positioned, communicated, launched and sold.

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
├── marketing/
├── docs/
└── .github/workflows/
```

The former Python implementation and Python test suite have been removed. `cargo test` is the canonical deterministic test command.

Use `skills/agentic-app/SKILL.md` for guided INIT/UPGRADE, `skills/codebase-audit/SKILL.md` for evidence-backed repository audits, and `skills/marketing/SKILL.md` for evidence-aware positioning and go-to-market work. Security covers both conventional application risks and agent-specific risks such as prompt injection, excessive tool permissions, data exfiltration, unsafe generated code, untrusted retrieval, and destructive actions.
