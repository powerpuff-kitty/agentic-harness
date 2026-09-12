# Audit remediation: public trust and one complete adoption path

Date: 2026-09-12. Status: implementation started; not a release-readiness claim.

## Goal and scope

Keep architecture, design intent and verification consistent across coding agents without replacing those agents. Retain the public contract/procedure/CLI responsibility split. Finish one reproducible workflow before expanding catalog breadth.

Canonical roadmap: [#87](https://github.com/powerpuff-kitty/agentic-harness/issues/87).

| Priority | Work | Tracking |
| --- | --- | --- |
| P0 | Public-only source and editable metadata | [#82](https://github.com/powerpuff-kitty/agentic-harness/issues/82) |
| P0 | Truthful onboarding and capability descriptions | [#83](https://github.com/powerpuff-kitty/agentic-harness/issues/83) |
| P0 | Installed examples, compatibility and public-safe source pins | [CLI #56](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/56) |
| P1 | Minimal context and deeper selected packs | [#84](https://github.com/powerpuff-kitty/agentic-harness/issues/84) |
| P1 | Declared/delivered/checked/enforced evidence | [#85](https://github.com/powerpuff-kitty/agentic-harness/issues/85) |
| P1 | Native host integrations | [Agents #24](https://github.com/powerpuff-kitty/agentic-harness-agents/issues/24) |
| P1 | Flagship skill depth and standalone dependencies | [Agents #25](https://github.com/powerpuff-kitty/agentic-harness-agents/issues/25) |
| P1 | Approved check execution and evidence freshness | [CLI #55](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/55) |
| P1 | Executed routing and task-outcome evaluation | [Agents #26](https://github.com/powerpuff-kitty/agentic-harness-agents/issues/26) |
| P1 | Synthetic Vue/TypeScript architecture/design demonstration | [#86](https://github.com/powerpuff-kitty/agentic-harness/issues/86) |
| P2 | Safe filesystem migration and ADR creation | [CLI #57](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/57) |

## First slice

Correct current public source and onboarding, document the manual migration boundary, add a public-name allowlist/quick-start consistency validator and synthetic negative tests, and preserve the existing catalog structural validation. Review editable issue metadata separately. Current-tree removal does not erase Git history or old diffs.

The CLI must separately verify exact upstream pins and installed commands before updated distribution claims. Its existing [release issue #50](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/50) remains the candidate/publication gate; this plan does not authorize publication.

## Completion criteria

A developer can install a compatible version, configure accepted project rules, load them in a supported host, detect seeded violations, execute approved checks and inspect current evidence. Missing tools, failures, unsupported coverage and unexecuted model evaluations remain visible. No invented pass rates or quality scores.

No runtime reinvention, repository consolidation, mandatory paid APIs, scripts-per-skill quota or GitHub Actions redesign. Existing workflows may run their existing validation entrypoints. Public records contain only approved public identifiers and synthetic fixtures.
