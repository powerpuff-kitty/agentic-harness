# Quality Registry

The Quality Registry is the canonical, versioned source of code-quality rules and tool capabilities used by Agentic Harness analyzers, checks and agent guidance.

It complements the Architecture Registry. Architecture defines dependency/ownership boundaries; Quality defines formatting, linting, type-safety, maintainability and implementation-coherence evidence. Consumers should reuse shared dependency-graph evidence instead of implementing competing graphs.

## Profile kinds

- `language/` — language semantics and officially documented compiler/type-system quality controls.
- `framework/` — framework-specific quality rules that are not already architecture rules.
- `tooling/` — formatter/linter/analyzer capabilities. Tool presence does **not** make the tool a project authority.
- `patterns/` — explicit Harness-owned maintainability/naming/documentation policies.

## Core principles

1. **Detect before enforcing.** Existing project-native tools and accepted project contracts are preserved.
2. **Discovery is not execution.** A config or package script only proves that it was discovered.
3. **Not checked is never pass.** Unsupported, blocked and unexecuted checks remain explicit.
4. **Rules have stable IDs.** Native diagnostic codes are preserved alongside Harness IDs when tools execute.
5. **Authority stays explicit.** Official language/tool guidance is not mixed with Harness preference.
6. **Autofix is bounded.** `analyze` is read-only; fix capability does not authorize a write.
7. **Thresholds are contextual.** Complexity/size/naming thresholds are project or selected-profile policy, not universal taste.
8. **Legacy debt remains visible.** Future baselines/ratchets may prevent new regressions but must not serialize historical findings as clean.

## Initial profiles

```text
language/
  typescript/current.json
  rust/current.json

tooling/
  eslint/current.json
  prettier/current.json
  rustfmt/current.json
  clippy/current.json
```

Additional JavaScript, Python, Go, Biome, Ruff and gofmt/go vet profiles are tracked by the quality roadmap.

## Machine contracts

- `quality-profile.schema.json` defines canonical profile/rule/source metadata.
- `quality-analysis.schema.json` defines normalized read-only analysis output.

A normalized finding carries the stable Harness rule ID, optional native diagnostic code, category, severity, enforceability, exact evidence and remediation. Reports separately list performed, not-checked and unsupported capability.

## Planned consumers

- `ah quality detect`
- `ah quality analyze`
- `ah quality check`
- `ah quality baseline`
- `ah quality diff`
- `ah quality fix`
- `ah audit` quality coverage
- `ah verify`
- agent quality-review/remediation procedures
