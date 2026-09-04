# Agentic project context

This directory contains project knowledge, governance, provenance, and agent-visible work state. `AGENTS.md` is the root router; this file is the map.

## Canonical map

| Path | Purpose | Read when | Update when |
| --- | --- | --- | --- |
| `manifest.yaml` | Machine-readable project configuration and permissions | Starting any task | Project type, maturity, modules, paths, or permissions change |
| `lock.json` | Resolved source revisions, module versions, and checksums | Reproducing or upgrading the harness | Modules are installed or upgraded |
| `PRODUCT.md` | Users, problem, scope, requirements, and non-goals | Changing behavior or scope | Accepted product truth changes |
| `ARCHITECTURE.md` | Current accepted system structure and boundaries | Changing components, dependencies, or data flow | Accepted architecture changes |
| `SECURITY.md` | Threat model, assets, trust boundaries, and security requirements | Touching data, auth, permissions, or deployment | Security assumptions or controls change |
| `DESIGN.md` | Optional design-system and interaction truth | Building user-facing interfaces | Accepted design direction changes |
| `REFERENCE.md` | Evidence, external sources, measurements, and provenance | Researching or validating a decision | Evidence is added, corrected, or expires |
| `decisions/` | Architecture Decision Records explaining durable choices | Reconsidering consequential choices | A decision is proposed, accepted, superseded, or rejected |
| `plans/` | Temporary multi-step implementation strategies | Beginning substantial work | A plan is created, revised, completed, or archived |
| `tasks/` | Active execution and coordination state | Coordinating current work | Task status or ownership changes |
| `docs/` | Supporting domain, API, data, testing, operations, and research documentation | The task needs deeper supporting context | Supporting knowledge changes |
| `evals/` | Outcome rubrics and deterministic/agent-assisted evaluations | Quality is subjective or requires explicit acceptance criteria | Evaluation criteria change |
| `packs/` | Installed reusable domain knowledge and constraints | A task touches an installed domain | A pack is installed or upgraded |
| `policies/` | Installed mandatory must/must-not rules | Before any consequential change | Policy installation or approved policy text changes |

## Information lifecycle

```text
REFERENCE / research evidence
        ↓
decisions/ADR-... records the accepted choice
        ↓
PRODUCT / ARCHITECTURE / DESIGN / SECURITY describes current truth
        ↓
plans/ describes temporary implementation strategy
        ↓
tasks/ tracks active execution
        ↓
implementation + validation
```

An ADR explains why a decision was made; it does not replace current-state documentation. When an accepted ADR and current truth conflict, report documentation drift instead of choosing silently.

## Required core

Every Agentic Harness project keeps `AGENTS.md`, this README, `manifest.yaml`, `PRODUCT.md`, `ARCHITECTURE.md`, `SECURITY.md`, and `decisions/`. Other sections are conditional on project type and maturity. Do not create empty folders merely to look complete; add their README when the capability becomes relevant.

## Precedence

1. Mandatory installed policies.
2. Current accepted project truth.
3. Accepted ADRs and explicitly approved exceptions.
4. Installed packs.
5. Skills and procedures.
6. One-off prompts.

A lower layer may guide execution but may not silently redefine a higher layer.
