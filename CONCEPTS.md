# Concepts

## Boilerplate
A canonical initial repository starting point. Boilerplates live directly at the repository root (`base`, `web-app`, `backend-api`, `saas`, `monorepo`, `library-sdk`) and contain `boilerplate.json` metadata.

## Module
A reusable cross-boilerplate building block. The canonical module families are packs, policies, and profiles under `modules/`.

## Pack
Reusable knowledge and technical/product constraints. Packs describe what agents need to know about a domain.

## Policy
A mandatory organizational or project rule suitable for review-time or deterministic enforcement.

## Profile
A coherent set of organization/team/project defaults, such as startup, enterprise, agency, or open source.

## Preset
A machine-readable named composition that selects a boilerplate plus useful modules and skills. Presets reduce setup choices without multiplying boilerplates.

## Skill
A repeatable agent procedure. Skills are maintained in `agentic-harness-agents`, not here.

## Schema
A machine-readable public contract for boilerplate metadata, presets, profiles, manifests, or audit output.

## Eval
A test or rubric for whether an outcome satisfies a quality bar. Agent-facing eval procedures belong primarily in `agentic-harness-agents`; deterministic checks belong in `agentic-harness-cli`.

## Example applications
Complete demo/reference applications are intentionally outside this repository so the canonical catalog stays small and readable.
