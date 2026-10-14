# ADR-014: Keep the skills source limited to skill folders

- Status: accepted
- Date: 2026-10-14
- Deciders: project owner
- Supersedes: none

## Context

After renaming the procedure source, the owner explicitly selected strictly skill
folders instead of skills accompanied by collection-level documentation, tests and
package metadata.

## Decision

Keep only `skills/<name>/` directories in the skills repository's tracked tree.
Each contains `SKILL.md`, its MIT `LICENSE`, and only supporting references,
helpers, assets or tests belonging to that skill. Move native context adapter
resources into `adapter-sync`. Remove root project context, standalone prompts,
plugin/marketplace manifests, collection packaging, CI/release workflows and other
collection-level content. Preserve history, published assets and existing tags.

Canonical ecosystem truth and this decision remain in `agentic-harness`. The CLI
consumes the skill-folder layout, verifies relocated adapter bytes and attributes
each skill at its own root. Existing project installations retain their reviewed
pins and checksums until separately upgraded.

## Alternatives

Retain supporting documentation and tooling alongside skills. The owner selected
the stricter folder-only source layout.

## Consequences

Every current skill can be copied independently with its resources and license.
Current source no longer supplies an aggregate plugin or automatic collection CI;
individual skill checks and downstream integration verification remain available.
Historical plugin versions remain unchanged. This does not change target-project
contracts or authorize releases, host configuration changes or automatic upgrades.
