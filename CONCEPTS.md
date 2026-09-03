# Concepts

## Boilerplate
A canonical initial repository starting point, such as `web-app`, `backend-api`, `saas`, or `monorepo`. A boilerplate defines coherent project shape and durable harness structure. It is intended to be browsable and usable directly by humans, agents, and tooling.

## Preset
A machine-readable named composition that selects a boilerplate plus useful packs and other modules. Presets reduce setup choices without creating a separate boilerplate for every stack combination.

## Pack
Reusable knowledge and constraints. A pack describes what agents need to know about a technical or product domain.

## Skill
A repeatable agent procedure. Skills are maintained in `agentic-harness-agents`, not here.

## Policy
A mandatory organizational or project rule suitable for deterministic or review-time enforcement.

## Profile
A coherent set of defaults for an organization/team/project posture, such as startup, enterprise, agency, or open source.

## Schema
A machine-readable contract for manifests, audit output, configuration, or package metadata.

## Eval
A test or rubric for whether an outcome satisfies a desired behavior or quality bar. Agent-facing eval procedures belong primarily in `agentic-harness-agents`; deterministic enforcement belongs in `agentic-harness-cli`.

## Example applications
Complete demo/reference applications are not part of this canonical repository. If maintained later, they should live in a dedicated examples repository so this repo remains a focused boilerplate catalog and source of truth.
