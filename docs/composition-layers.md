# Composition Layers

Agentic Harness is designed to sit **on top of** a software project rather than replace the project's framework, package manager, source tree, or CI system.

A useful mental model is a stack of composable layers:

```text
existing/new software project
        +
base template / project shape
        +
domain & technical packs
        +
repeatable skills
        +
optional presets
        +
agent adapters and scoped instructions
        +
evals / tests / schemas / CI gates
        =
agent-native governed project
```

## Template

A template defines initial repository shape. Templates are best for structural differences such as a web app, backend API, monorepo, SaaS, or library/SDK. They are not packages installed at runtime.

## Pack

A pack contains reusable domain or technical knowledge and constraints. Examples include PostgreSQL, design systems, security-critical software, realtime systems, or marketing. Packs are copied into the target project so agents can use them locally without depending on the source Agentic Harness repository.

## Skill

A skill is a repeatable procedure: codebase audit, security review, product design, marketing, release review, implementation planning, etc. Skills describe how an agent should perform work, including workflow, evidence rules, safety boundaries, and completion criteria.

## Preset

A preset is a named composition of a template plus useful packs and skills. It reduces setup decisions without creating a new template for every framework/domain combination.

## Canonical project truth

Files such as `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, `SECURITY.md`, ADRs, and scoped `AGENTS.md` remain project-owned truth. Harness modules should support these files, not compete with them.

## Deterministic layer

The native `ah` CLI, schemas, tests, evals, and CI checks enforce what should not depend on model interpretation alone.

## New vs existing projects

For a new project, `ah init` may compose a template and selected modules into a useful starting repository. For an existing project, the harness should inspect first, preserve project-specific truth, add missing layers, and avoid destructive replacement.

## Package analogy

Agentic Harness modules are package-like because they are versionable, reusable, composable, and installable into projects. They are not runtime dependencies: once composed, the target repository contains the relevant knowledge/procedures locally. This makes the model closer to **development-policy/context packages + project overlays** than to npm/Cargo application dependencies.
