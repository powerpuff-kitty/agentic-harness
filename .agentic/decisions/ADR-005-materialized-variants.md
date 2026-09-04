# ADR-005: Publish complete materialized catalog variants

- Status: accepted
- Date: 2026-09-04
- Deciders: project maintainer
- Supersedes: hidden overlay-only catalog structure
- Superseded by: none

## Context

Overlay-only boilerplates were efficient for a generator but difficult for a person to browse. Users could not see the complete structure of a selected project type without mentally composing multiple directories.

## Decision

Store complete materialized target trees under `catalog/variants/<name>/files/`. Metadata may describe inheritance and defaults, but each public variant remains directly inspectable and usable without hidden composition.

## Consequences

The catalog is easier to teach and audit at the cost of some duplicated authoring content. Validation must detect divergence in mandatory core files.

## Verification

Catalog CI checks every variant for the complete core contract, valid metadata, source-path consistency, and cross-references.
