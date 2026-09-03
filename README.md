# Agentic Harness

A composable framework for designing, generating, governing, auditing, and maintaining agent-native software projects.

## Native Rust CLI

Agentic Harness ships as the native `ah` binary. Precompiled releases require no Python, Node.js, or Rust runtime.

```bash
ah init ./app --template web-app
ah init ./saas --preset vue-saas --profile startup --name my-saas
ah init ./api --template backend-api --pack postgres --policy security
ah upgrade ./existing --profile enterprise
ah audit ./existing > audit.json
ah design-system-components ./existing --write
ah gate audit.json --min-overall 80 --min-score security=80 --min-score design_system=85
ah validate .
ah security-scan .
```

## Architecture

The repository is a monorepo with two different kinds of units:

```text
crates/    deterministic Rust engine boundaries
packages/  distributable agent knowledge, procedures and project overlays
```

The package model is analogous to a development-time package ecosystem, not application runtime dependencies.

```text
project source / framework
        +
template   repository shape
preset     project-type composition
profile    organization/team defaults
packs      knowledge + constraints
skills     procedures
policies   mandatory rules
examples   accepted outcomes
evals      success criteria
schemas    machine contracts
        +
ah         deterministic composition + audits + gates
```

Official packages remain bundled into release binaries for zero-runtime-dependency installs. Their layout is now isolated so they can later be versioned or distributed independently without changing project-local paths.

## Repository shape

```text
.
├── Cargo.toml                  # workspace + ah binary package
├── crates/
│   ├── ah-cli/
│   │   └── src/               # command orchestration
│   ├── ah-core/               # package model and shared contracts
│   ├── ah-audit/              # reusable audit primitives
│   └── ah-registry/           # package-source/reference model
├── packages/
│   ├── core/                  # official package-set contract
│   ├── templates/
│   ├── presets/
│   ├── profiles/
│   ├── packs/
│   ├── skills/
│   └── policies/
├── schema/                    # machine-readable public contracts
├── marketing/                 # Agentic Harness product messaging
├── docs/
└── .github/workflows/
```

The CLI source is physically under `crates/ah-cli/`; the root Cargo package owns the `ah` binary so release/install behavior remains stable while the internal workspace is decomposed.

## Package boundaries

`packages/core/package.json` declares the official package-set contract. The Rust `ah-core` crate exposes stable package kinds and paths, while `ah-registry` establishes a source-reference model for future official and third-party packages such as `official:observability` or `github:acme/harness#packs/security`.

For now, official packages are compiled into `ah`. A future registry can make them independently installable without forcing a multi-repository split today.

## Profiles and policies

Profiles currently include `startup`, `enterprise`, `agency`, and `open-source`. Policies cover dependencies, licensing, security, AI permissions, and quality gates.

Specialist packs include accessibility, analytics, auth, compliance, localization, observability, payments, performance, privacy, SEO, design-system, marketing, and application/data/security packs. Specialist skills include threat modeling, migrations, dependency upgrades, API/database design, accessibility/performance audits, incident reviews, releases, documentation, competitive research, marketing, and design-system compliance.

## Design-system enforcement

When a project has or wants a design system, Agentic Harness treats it as an implementation constraint. `ah design-system-components` infers the likely component inventory from project evidence and `--write` creates `DESIGN_SYSTEM_COMPONENTS.md` for review. `ah audit` adds a `design_system` score when a design system is active and checks structural evidence such as raw-control bypasses, hard-coded visual values, and missing inferred components.

Templates, presets, packs, skills, policies, and profiles are embedded into release binaries at compile time. Generated repositories are self-contained and do not depend on the Agentic Harness source checkout.
