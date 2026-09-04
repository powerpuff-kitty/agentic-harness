# Agentic Harness project context

This is a real, self-hosting Agentic Harness installation. The repository demonstrates the same project contract that the catalog and CLI generate.

## Canonical map

| Path | Purpose | Read when | Update when |
| --- | --- | --- | --- |
| `manifest.yaml` | Project type, maturity, context paths, installed modules, skills, and permissions | Starting any task | Project configuration changes |
| `lock.json` | Resolved source revisions and installed content | Reproducing or upgrading the harness | Source or module pins change |
| `PRODUCT.md` | Product purpose, users, scope, non-goals, and success criteria | Changing product behavior or scope | Accepted product truth changes |
| `ARCHITECTURE.md` | Current three-repository architecture and target-project contract | Changing boundaries, source ownership, or composition | Accepted architecture changes |
| `SECURITY.md` | Supply-chain, instruction, permission, release, and data-safety model | Touching sources, automation, permissions, or releases | Security assumptions or controls change |
| `DESIGN.md` | Documentation UX, naming, discoverability, and design-system principles | Changing the public structure or documentation experience | Accepted design direction changes |
| `REFERENCE.md` | Evidence and provenance used by decisions | Researching or reviewing a choice | Evidence changes or expires |
| `decisions/` | Immutable Architecture Decision Records | Understanding why the ecosystem is structured this way | A consequential decision is proposed or accepted |
| `plans/` | Temporary implementation strategies | Executing substantial changes | Plans start, change, finish, or archive |
| `tasks/` | Current local execution state | Coordinating active work | Task state changes |
| `docs/` | Supporting architecture, compatibility, migration, testing, operations, and research | More detail is needed | Supporting knowledge changes |
| `evals/` | Explicit quality and migration-safety criteria | Validating catalog or tooling changes | Acceptance criteria change |
| `packs/` | Packs installed for this repository itself | Applying domain constraints | Installed pack changes |
| `policies/` | Mandatory repository rules | Before consequential changes | Policy installation or approved policy text changes |

## Information lifecycle

```text
REFERENCE / research
        ↓
decisions/ADR records why a durable choice was accepted
        ↓
PRODUCT / ARCHITECTURE / DESIGN / SECURITY describes current truth
        ↓
plans/ describes temporary implementation strategy
        ↓
tasks/ tracks active execution
        ↓
implementation, tests, audit, release evidence
```

ADRs never replace current-state documents. When an accepted ADR and a current truth file disagree, report documentation drift and resolve it explicitly.

## Precedence

1. Installed mandatory policies.
2. Current accepted project truth.
3. Accepted ADRs and approved exceptions.
4. Installed packs.
5. Agent skills.
6. One-off prompts.

Lower layers may guide work but cannot silently redefine higher layers.

## Repository source layout

Reusable authoring material is under `../catalog/`. The sibling `agentic-harness-agents` repository owns procedures; `agentic-harness-cli` owns deterministic application and enforcement.
