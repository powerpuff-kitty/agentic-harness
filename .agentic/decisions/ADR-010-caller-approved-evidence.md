# ADR-010: Begin imported evidence trust with caller-approved exact digests

- Status: accepted
- Date: 2026-09-18
- Deciders: project owner, explicit session decision
- Supersedes: none
- Superseded by: none

## Context

Governance evidence shape and hashes cannot authenticate a producer. The first consuming gate needs a trust boundary distinct from imported claims and command authorization.

## Decision

Use explicit caller-approved report digests first; signed producers follow later. A reviewed evidence manifest binds the run report, governance producer identities and immutable reference digests. An explicit CLI digest approves the exact manifest bytes and therefore those exact bindings. No manifest field or repository setting grants itself approval. Do not automatically derive and approve the manifest in an agent workflow.

The read-only gate recomputes required outcomes and current input identities. Its separate v1 verdict is scoped to declared checks and required controls under caller trust; it does not change the executor's always-false global completion field or existing audit/gate semantics. Producer authentication remains false.

## Alternatives and consequences

Requiring signed producers immediately was deferred by the owner. Trusting a producer name or checksum without caller approval is rejected. The manifest makes reference digests and producer-version bindings reviewable along with report digests. The caller must assess provenance and assertions: approval cannot prove that an untrusted producer told the truth.

Same-host exact executor/tool/source revalidation limits portability intentionally. Undeclared inputs, transient reverted mutations and changes after evaluation remain outside the guarantee. No installed-project migration is required; the new artifacts and command are opt-in.

See [the contract](../docs/project/check-completion-v1.md).
