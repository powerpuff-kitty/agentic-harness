# ADR-004: Separate project truth from agent procedures

- Status: accepted
- Date: 2026-09-04
- Deciders: project maintainer
- Supersedes: none
- Superseded by: none

## Context

Prompts and skills can drift into architecture or policy documents, making it unclear whether a procedure or a project decision is authoritative.

## Decision

Canonical project truth and mandatory policies live under `.agentic/`; reusable procedures live under `.agents/skills/` and originate in `agentic-harness-agents`. Skills may explain how to use truth but cannot redefine it.

## Consequences

Precedence is explicit and vendor adapters remain replaceable. Cross-repository references and audits are required to detect duplicated or conflicting authority.

## Verification

Agent repository validation rejects canonical architecture duplication, and target audits identify adapters or skills that redefine project truth.
