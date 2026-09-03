# Composition Layers

Agentic Harness sits **on top of** a software project rather than replacing its framework, package manager, source tree, or CI system.

```text
existing/new software project
        +
boilerplate
        +
packs / policies / profile
        +
agent skills
        +
preset defaults
        +
deterministic checks
        =
agent-native governed project
```

## Boilerplate

A boilerplate defines the initial repository shape. Canonical boilerplates are the root catalog directories in this repository.

## Modules

Reusable cross-boilerplate layers live under `modules/`:

- packs provide domain/technical knowledge and constraints;
- policies provide mandatory rules;
- profiles provide organization/team defaults.

## Skill

A skill is a repeatable agent procedure such as codebase auditing, security review, product design, release review, or implementation planning. Skills are maintained in `agentic-harness-agents`.

## Preset

A preset is a named machine-readable composition of a boilerplate plus selected modules and skills. It reduces setup decisions without creating a new boilerplate for every framework/domain combination.

## Canonical project truth

Files such as `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, `SECURITY.md`, ADRs, and scoped `AGENTS.md` remain target-project-owned truth after generation. Harness content supports those files rather than competing with them.

## Deterministic layer

The native `ah` CLI and CI checks apply and validate canonical contracts that should not depend on model interpretation alone.

## New vs existing projects

For a new project, `ah init` composes a boilerplate and selected modules. For an existing project, the harness should inspect first, preserve project-specific truth, add missing layers, and avoid destructive replacement.
