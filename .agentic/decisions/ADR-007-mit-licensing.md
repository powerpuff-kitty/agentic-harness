# ADR-007: Use MIT for authored CLI, catalog and agent content

- Status: accepted
- Date: 2026-09-11
- Deciders: project owner
- Supersedes: none
- Superseded by: none

## Context

Production-core release preparation found undeclared licenses in the CLI and its
embedded canonical and agent sources. The owner requested a recommendation and
then explicitly instructed implementation of MIT across those authored sources.
The intended fit is broad adoption and reuse of Harness templates and skills.

## Considered options

- MIT: permissive reuse with copyright and license notice retention.
- Apache-2.0: explicit contributor patent grants with additional redistribution terms.
- Proprietary terms: restricted reuse, inconsistent with the accepted recommendation.

## Decision

Use the unmodified MIT terms with an Agentic Harness contributors copyright notice
for authored content in `agentic-harness-cli`, `agentic-harness` (including its
registry) and `agentic-harness-agents`. Declare `license = "MIT"` in the CLI package.
Keep every third-party license and required notice under its original terms.

Every materialized variant includes `.agentic/THIRD_PARTY_NOTICES.md` covering the
copied Harness material. Do not install a root application LICENSE or replace an
existing user license. Independently authored application code may use other terms.
Manual copying of substantial Harness material must likewise retain the MIT notice.

## Consequences

Commercial and proprietary reuse of Harness content is permitted under MIT's notice
conditions; downstream changes need not be shared. This decision does not grant
rights in third-party material, create an explicit MIT patent grant, or authorize
publishing a release. CLI source pins and candidate attribution must refer to the
licensed revisions, including the separately pinned model registry.

## Evidence

- Owner instruction: implement the MIT recommendation, 2026-09-11.
- https://opensource.org/license/mit
- https://www.apache.org/licenses/LICENSE-2.0
- https://github.com/powerpuff-kitty/agentic-harness-cli/issues/53
