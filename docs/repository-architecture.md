# Repository Architecture

Agentic Harness is intentionally a single monorepo with explicit boundaries between executable code and distributable agent packages.

```text
crates/                       deterministic Rust implementation
  ah-cli/src/                 command orchestration and embedded official bundle
  ah-core/                    package kinds and compatibility primitives
  ah-audit/                   reusable audit primitives
  ah-registry/                package source/reference model

packages/                     official distributable content
  core/                       package-set metadata
  templates/                  initial repository shapes
  presets/                    named compositions
  profiles/                   team/organization defaults
  packs/                      knowledge and constraints
  skills/                     repeatable procedures
  policies/                   enforceable development rules

schema/                       public machine-readable contracts
docs/                         Agentic Harness engineering documentation
marketing/                    Agentic Harness positioning and go-to-market truth
```

## Why one repository now

The CLI and official package set still evolve together. A monorepo gives atomic compatibility changes, one CI gate, simple release binaries, and easy refactoring. The package boundary avoids coupling their filesystem organization to the Rust implementation.

## When to split repositories

Split a package collection only when it needs genuinely independent ownership, release cadence, access control, community governance, or distribution. Do not create separate repositories merely because content is modular.

## Compatibility

The Rust engine should depend on package contracts rather than hard-coded knowledge of every package. Official packages may be embedded for zero-dependency distribution, but generated repositories must remain self-contained. Future registry support should preserve the same package kinds and target-project paths.
