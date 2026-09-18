# ADR-009: Separate context file selection from organization profiles

- Status: accepted
- Date: 2026-09-18
- Deciders: implementation agent within the authorized issue #84 continuation
- Supersedes: none
- Superseded by: none

## Context

Issue #84 calls for minimal context without losing inspectability, mandatory truth, attribution or authored content. Organization profiles already select maturity, modules and skills; reusing them for file selection conflates two decisions.

## Decision

Define catalog-owned full/minimal selection and persist it in an optional manifest composition mapping. Keep full as the compatibility default. Minimal retains the 12-file core plus context needed by visual variants and selected modules. Complete materialized source variants remain as required by ADR-005.

Mode changes add missing files only. Existing files and routes, including explicit null routes, remain project-owned. Inherit installed selection and variant for ordinary upgrades. Native host adapters remain separately selected in minimal mode.

## Alternatives and consequences

Removing optional files from all variants would change existing defaults and reduce source inspectability. A separate minimal variant would conflate project type with context density. A CLI-only allowlist would duplicate catalog authority. The chosen approach requires coordinated schema, CLI and procedure updates.

The baseline budget does not constrain module contents or user documents. Existing maps may require explicit reconciliation after mode changes. No pruning migration or behavioral-quality claim is introduced.

## Verification

Catalog validation checks schema, path safety, core coverage and references. CLI tests must establish preserved bytes/routes, valid output, repeatability, failure behavior and installed-binary operation. Pins must reference committed catalog/procedure content. See the [contract](../docs/project/context-selection-v1.md) and [plan](../plans/active/2026-09-18-minimal-context.md).
