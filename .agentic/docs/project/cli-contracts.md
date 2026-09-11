# Production-core CLI contracts

These contracts support the accepted CLI production-core roadmap ([CLI #49](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/49)). They version machine-readable evidence independently from the project filesystem format. The filesystem manifest remains version 1.

## Evidence and score compatibility

`catalog/schema/codebase-audit.v2.schema.json` adds explicit `format_version: 2` and `kind: codebase-audit`. Scores and readiness dimensions accept explicit null for unmeasured evidence. File presence alone cannot establish test quality, security, performance, or production readiness. Any reported numeric indicator must describe its formula and coverage. Null is unknown, not zero or success.

The unversioned legacy codebase-audit schema remains available unchanged. Readers may accept complete legacy artifacts for comparison and explicit gates. They must reject malformed shapes, unsupported versions, non-finite thresholds, and out-of-range scores. Comparisons require matching versions. A numeric threshold on a null/missing metric fails. A scan explicitly marked incomplete cannot receive an unqualified passing gate. Passing a requested policy is not release approval.

`catalog/schema/agentic-readiness.v2.schema.json` separates an experimental structural heuristic from verified readiness. Universal readiness stays null; model compatibility requires evidence that the heuristic does not supply.

`catalog/schema/design-system-discovery.schema.json` describes optional `.agentic/design-system.json` configuration. Roots and exception entries are repository-relative paths. Required capabilities are explicit; static native-control observations are suggestions. Aliases map a required capability name to an observed component capability. These observations do not prove visual, accessibility, or runtime conformance.

`audit-comparison.v1.schema.json` and `audit-gate.v1.schema.json` define comparison and policy result envelopes. Both add `format_version: 1` and a `kind` discriminator to the existing result fields. Comparison values and deltas retain explicit nulls for unknown metrics; gate results distinguish passed policy from textual failure reasons. Consumers must allow additive fields within a supported version.

## Commands and errors

The installed `ah` executable owns composition, validation, audit/gate, architecture, static design, and experimental agentic inspection/preview commands. An upstream source checkout, Rust, network, and companion executable must not be runtime prerequisites. `--version` reports package and pinned source identities.

Exit 0 means the requested operation/policy succeeded. Exit 1 reports findings or a failed validation/policy. Exit 2 means invalid input, unsupported operations, or execution failure. Help exits 0; unknown flags, missing operands, invalid directories, unsupported model IDs and unimplemented apply modes cannot silently succeed. Invalid input diagnostics belong on stderr; machine-readable results belong on stdout.

Architecture exceptions use valid ISO calendar dates and remain valid through the expiry day. The default clock is UTC; architecture analysis/enforcement accepts `--as-of YYYY-MM-DD` for reproducible evidence. Expired exceptions remain visible and cannot suppress findings.

## Composition and compatibility

New projects consume complete `catalog/variants/<name>/files/` trees. Variant metadata stays outside generated projects. Manifest context paths are relative to `.agentic/manifest.yaml`; optional DESIGN/REFERENCE routes may be null. Resolved source commits and installed-content checksums belong in `.agentic/lock.json`.

Upgrades preserve user content, report conflicts, stage additions, and restore changed managed metadata if a recoverable write fails. Existing checksums retain the original installed content's identity so local customization stays detectable. Filesystem operations cannot promise crash-wide transactions across multiple files; backups remain the recovery mechanism for process/system interruption.

Legacy `agentic.yaml` layouts remain readable for inspection. Current composition must refuse an implicit legacy layout migration; the separate migration procedure provides the explicit plan, backup, conflict review, and restoration path. Mixed manifests are an error.
