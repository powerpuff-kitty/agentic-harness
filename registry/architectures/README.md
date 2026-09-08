# Architecture Registry

The Architecture Registry is the canonical, versioned source of software-architecture rules used by Agentic Harness analyzers, generators and agent guidance.

It deliberately separates four kinds of profiles:

- `framework/` — rules and conventions backed by framework documentation.
- `ecosystem/` — router, state-management and other official ecosystem conventions.
- `tooling/` — build/workspace/enforcement tooling capabilities; tooling does not automatically define application architecture.
- `patterns/` — Harness-owned architecture patterns such as feature-first, layered, Clean Architecture, hexagonal and vertical slices.

## Core principles

1. **Official guidance is not mixed with Harness opinion.** Every profile and rule declares its authority.
2. **Framework profiles are composable.** A Vue project may combine Vue + Vite + Pinia + Vue Router + a Harness architecture pattern.
3. **Folder names are weaker than dependency boundaries.** A directory recommendation should not be promoted to an error unless the underlying framework/runtime actually requires it.
4. **Deterministic rules are preferred for enforcement.** Heuristic and advisory rules remain visible but must not masquerade as certain violations.
5. **Rules have stable IDs.** Analyzer findings, generated lint rules and agent guidance should point back to the same registry rule IDs.
6. **Sources are versioned provenance.** Profiles record source URLs, authority and review dates so changes can be audited through Git history.

## Initial profiles

```text
framework/
  vue/3.json
  nuxt/4.json
  angular/current.json

ecosystem/
  pinia/3.json
  vue-router/current.json

tooling/
  vite/current.json
  nx/current.json

patterns/
  feature-first/1.json
```

Vite is intentionally represented as tooling rather than an application-architecture source. Angular's current official profile favors feature-oriented organization. Nuxt's profile contains deterministic `app/` / `server/` / `shared/` dependency-boundary rules that can eventually compile directly into CLI and ecosystem-native enforcement.

## Profile format

Profiles conform to `architecture-profile.schema.json`. Important rule fields include:

- `id`
- `rule_type`
- `severity`
- `enforceability`
- `authority`
- `source_refs`
- machine-readable `constraints`

The registry stores concise evidence summaries rather than copying documentation text.

## Planned consumers

- `ah architecture detect`
- `ah architecture analyze`
- `ah architecture enforce`
- `ah audit` architecture scoring
- ESLint / dependency-cruiser / Nx adapters
- generated project manifests and agent-facing architecture guidance
