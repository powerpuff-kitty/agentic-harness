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
ah design-system-components ./existing
ah design-system-components ./existing --write
ah gate audit.json --min-overall 80 --min-score security=80 --min-score design_system=85
ah validate .
ah security-scan .
```

## Layer model

Agentic Harness behaves like a package ecosystem layered onto an existing project, but the installed layers are development context and governance rather than application runtime dependencies.

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

Profiles currently include `startup`, `enterprise`, `agency`, and `open-source`. Policies cover dependencies, licensing, security, AI permissions, and quality gates.

Specialist packs include accessibility, analytics, auth, compliance, localization, observability, payments, performance, privacy, SEO, design-system, marketing, and the existing application/data/security packs. Specialist skills include threat modeling, migrations, dependency upgrades, API/database design, accessibility/performance audits, incident reviews, releases, documentation, competitive research, marketing, and design-system compliance.

## Design-system enforcement

When a project has or wants a design system, Agentic Harness treats it as an implementation constraint. `ah design-system-components` infers the likely component inventory from project evidence and `--write` creates `DESIGN_SYSTEM_COMPONENTS.md` for review. `ah audit` adds a `design_system` section and score when a design system is active, checking likely raw-control bypasses, hard-coded visual values outside component-library paths, and missing inferred components.

The deterministic compliance check complements visual regression, accessibility testing, Storybook/examples, and human design review; projects without a design system are not penalized.

## Repository shape

```text
.
├── Cargo.toml
├── src/
│   ├── main.rs
│   └── design_system.rs
├── templates/
├── presets/
├── profiles/
├── packs/
├── skills/
├── policies/
├── schema/
├── marketing/
├── docs/
└── .github/workflows/
```

Templates, presets, packs, skills, policies, and profiles are embedded into release binaries at compile time. Generated repositories are self-contained and do not depend on paths in the Agentic Harness source repository.
