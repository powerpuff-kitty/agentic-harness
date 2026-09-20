---
name: release
description: "Prepare and execute an approved software or package release: versioning, changelog, tests, artifacts, checksums, tagging, publishing, rollout, and rollback verification. Use when the user explicitly wants to create or publish a release. Do not use merely to review release readiness or to upgrade dependencies without releasing."
---
# Release

## Objective

Produce a reproducible release from an approved commit while respecting publication approvals and preserving traceability.

## Inputs

Required: target repository and intended version/release scope. Optional: release channel, artifact targets, changelog range, rollout strategy, signing/checksum requirements, and approval evidence.

## Context

Read release/versioning docs, manifest/package versions, CI/release workflow, relevant changelog/ADRs, and project permissions. Do not read unrelated product docs unless release notes require them.

## Procedure

1. Confirm release authorization, clean source state, version, and target commit.
2. Run required release-review/quality gates and repository-native tests/builds.
3. Synchronize version metadata and changelog without inventing changes.
4. Build reproducible artifacts and generate checksums/signatures where supported.
5. Verify artifacts locally or in CI before publishing.
6. Create/tag/publish using the repository's approved mechanism; do not bypass branch/release protection.
7. Verify release availability, asset integrity, and rollout/rollback signals.

## Output

Return version/commit/tag, checks performed, artifacts/checksums, publication result, release notes summary, rollout state, and unresolved post-release risks.

## Completion

The release is traceable to one commit, required gates passed, artifacts are verified, publication was explicitly authorized, and rollback/monitoring expectations are clear.
