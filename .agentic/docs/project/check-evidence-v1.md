# Check planning and independent governance evidence v1

Status: experimental, additive contracts for catalog #85 and CLI #55. Existing audit/gate versions and exit meanings are unchanged. Canonical schema: `catalog/schema/checks.v1.schema.json`.

## Three separate records

`check-policy` declares explicit input roots/files, check argument arrays, working directories, required flags, time/output limits, required governance capabilities and an evidence age limit. At least one check must be required. It is not execution authorization.

`check-plan` is a read-only preview of that policy against current declared inputs. It includes the exact requested arguments and limits, file/directory fingerprints, policy/planner/review digests, source pins and explicit unverified controls. It must contain `execution_permitted: false`, `checks_executed: false` and `executable_identity_verified: false`. A successful preview means planning succeeded, not that any test passed.

`governance-evidence` records independent producer assertions. Each claim names a rule and exactly one capability: **declared**, **delivered**, **checked** or **enforced**. Its status is **verified**, **unverified**, **unsupported** or **failed**. Verifying a declaration does not verify delivery; running a detector does not prove blocking. No automatic maturity ladder or universal readiness score is defined.

Verified claims need a mechanism and evidence references. Verified delivery/enforcement additionally needs a versioned host identity. Producer, optional adapter, source/policy identities, scope, timestamp, optional revision and explicit unchecked areas retain provenance. Null revision is not permission to omit content identity.

## Planning semantics

The experimental CLI slice uses `.agentic/checks.json` by default, with an explicit project-relative config override. No scripts are discovered or executed. There is no apply, run, approval, evidence-ingestion or completion-gate operation in this slice.

Inputs are literal normalized relative ASCII paths, not globs. The root input `.` is deliberately unsupported; `.` is valid as a working directory. Reject empty, parent/dot segments, absolute/drive/backslash paths, boundary spaces, trailing dots, `.git`, `.env` and `.env.*` components. This narrow known-sensitive-name block is not a secret scanner; do not select credential stores or sensitive data under other names. Every selected path must exist; symlinks are rejected rather than followed. Overlapping inputs are deduplicated. Declared inputs do not inherit advisory scanner ignore rules: missing/unreadable/oversized/unsupported input is an error, not successful partial coverage. Binary files and empty directories are fingerprinted.

Planning bounds: 262144 policy bytes, 2000000 bytes/file, 64000000 total file bytes, 10000 entries, depth 64. Each policy has 1-64 inputs and checks, unique check IDs, up to 64 distinct rule/capability requirements, a required check, positive timeout at most 300000 ms, output bound at most 1048576 bytes and evidence age at most 86400000 ms. Numeric lexemes must be unsigned integers. Arguments are nonempty bounded strings without control characters. Executable names are unresolved host requests; even `sh -c` in an argument array cannot run during a preview.

The preview includes the parsed policy; review it alongside the raw input bytes. It is not a signed statement or a capability token. No policy is installed merely because a file exists. Planning assumes a non-hostile, quiescent working tree: two snapshots and metadata checks detect ordinary concurrent changes, not every malicious filesystem race. It is not an operating-system sandbox.

## Digest framing

All hashes are SHA-256 rendered as `sha256:` followed by 64 lowercase hexadecimal characters. `policy_digest` hashes exact policy-file bytes, including whitespace. File digests hash exact file bytes; neither line endings nor encodings are normalized.

The framed function hashes a domain byte string followed by each field's unsigned 64-bit big-endian byte length and then the field bytes. It is not JSON canonicalization or JCS.

- `source_digest`: domain `ah-check-inputs-v1` plus NUL; entries sorted by normalized path, each contributing path UTF-8, kind (`file` or `directory`) and digest text (empty for a directory). Empty directories are entries.
- `planner_digest`: domain `ah-check-planner-v1` plus NUL; the planner module bytes, snapshot module bytes and upstream lock bytes, in that order. This identifies the preview implementation inputs, not the identity of a future check executable.
- `review_digest`: domain `ah-check-plan-v1` plus NUL; policy digest text, source digest text and planner digest text.

Changes to inputs, policy bytes or preview implementation invalidate the review digest. Files outside declared scope are not verified. A Git revision alone cannot replace dirty-worktree/content identity. Commands that depend on undeclared files need a more complete approved input policy before actual execution.

## Required evaluator and runner work — not yet delivered

JSON Schema verifies shape only. It cannot establish referenced evidence existence, producer authenticity, non-conflicting claims, current source identity, freshness, clock validity or actual host enforcement. Synthetic fixtures explicitly retain this distinction.

A future evaluator must reject missing, duplicate/conflicting, stale, mismatched, failed, unsupported or unverified required evidence; bind its policy, scope and exact before/after content identities; and use an explicit producer trust decision. Hashes alone do not authenticate a producer. Do not map a verified `declared` claim to a required `enforced` claim.

Before execution, a runner must separately resolve and identify executables, review command/config changes, enforce time/output/process-tree limits on supported platforms, control environment/working directories, record versions and outcomes, and reject changes during/after execution. A preview digest alone does not grant this approval. Preserve passed/failed/skipped/unsupported/timeout/execution-error distinctions. Do not silently turn repository script discovery into trust or claim shell-free invocation is a sandbox.

Public fixtures and diagnostics must remain public-safe; no internal consumer names, credentials, or private-name denylists. The schema and preview are not production-readiness or model-performance evidence.
