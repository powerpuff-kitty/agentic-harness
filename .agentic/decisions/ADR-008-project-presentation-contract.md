# ADR-008: Add an optional project presentation contract

- Status: proposed
- Date: 2026-09-12

## Context
Public project stories and visual design evidence need reproducible structure
without forcing a common brand or requiring executable component conversion.

## Decision
Add an opt-in catalog pack and visual extension schema. Separate content meaning,
layout vocabulary, project art direction, and the renderer's runtime. Keep native
project metadata/tokens authoritative. Installers must preserve project-owned
requirements and record the contract pin independently of product-source versions.

No default variant or installed-project migration occurs. Procedures and CLI work
remain separate reviewed adoption tasks. The contract ships generic fixtures only.

## Consequences
Consumers gain reusable requirements and finite responsive layouts. They still
implement semantics, asset-byte checks and human/runtime verification. This does
not create an exporter, library of web components, CMS, or publication authority.
