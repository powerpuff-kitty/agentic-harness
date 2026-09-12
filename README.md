# Agentic Harness

[![Status: Beta](https://img.shields.io/badge/status-beta-orange)](.agentic/PRODUCT.md#current-status)
[![Catalog validation](https://github.com/powerpuff-kitty/agentic-harness/actions/workflows/content-validation.yml/badge.svg)](https://github.com/powerpuff-kitty/agentic-harness/actions/workflows/content-validation.yml)
[![Agent native](https://img.shields.io/badge/agent--native-AGENTS.md-5c6ac4)](AGENTS.md)

A vendor-neutral project-context contract and catalog for coding-agent workflows.

Keep product truth, architecture, design intent and security expectations in your repository instead of repeatedly restating them to each agent. Root `AGENTS.md` is a compact router; durable context lives under `.agentic/`.

> **Beta:** context templates are not working application starters. Installing the structure does not configure your product decisions, execute your tests, or establish runtime enforcement. Schemas and CLI behavior may evolve before 1.0.

## Start here

This repository contains a self-hosting reference installation under [`.agentic/`](.agentic/README.md) and the canonical authoring source under [`catalog/`](catalog/README.md).

```text
agentic-harness/
├── README.md
├── AGENTS.md                    compact agent router
├── .agentic/                    this project's accepted context
│   ├── README.md                context map and precedence
│   ├── manifest.yaml            routes, modules and permissions
│   ├── lock.json                resolved sources and checksums
│   ├── PRODUCT.md
│   ├── ARCHITECTURE.md
│   ├── SECURITY.md
│   ├── DESIGN.md
│   ├── REFERENCE.md
│   ├── decisions/               durable ADR history
│   ├── plans/                   temporary implementation strategies
│   ├── tasks/                   current execution state
│   ├── docs/                    supporting documentation
│   ├── evals/                   acceptance criteria
│   ├── packs/                   installed knowledge
│   └── policies/                mandatory project rules
├── catalog/                     reusable context templates and contracts
└── .github/                     repository validation and adapters
```

The lifecycle is evidence → accepted decision → current truth → plan/task → implementation and verification. A plan or rubric is not evidence that an operation has been executed.

## Project-context templates

Each variant has an inspectable, materialized context tree under `files/`. These files guide an existing or new project; they do **not** include a runnable Vue, SaaS or backend application. Fill in the project-specific decisions and select relevant modules before relying on the context.

| Variant | Context for |
| --- | --- |
| [`base`](catalog/variants/base/) | General agent-assisted projects |
| [`web-app`](catalog/variants/web-app/) | User-facing applications and design systems |
| [`backend-api`](catalog/variants/backend-api/) | APIs and deployed services |
| [`saas`](catalog/variants/saas/) | Multi-user products and tenant isolation |
| [`monorepo`](catalog/variants/monorepo/) | Multiple applications/packages |
| [`library-sdk`](catalog/variants/library-sdk/) | Libraries and SDKs |

The CLI flag remains `--boilerplate` for compatibility; this documentation clarification does not rename catalog IDs or installed paths.

## Quick start with `ah`

First follow the [CLI source-installation instructions](https://github.com/powerpuff-kitty/agentic-harness-cli#installation). Then use a new target directory:

<!-- ah-quick-start -->
```bash
ah init ./my-app --boilerplate web-app
ah validate ./my-app
ah audit ./my-app
```
<!-- /ah-quick-start -->

`init` installs context, not application code. `validate` checks the project contract. `audit` reports available evidence and checks not performed; findings may produce a nonzero exit status. Neither command runs your application's tests or proves production readiness.

These examples are mirrored in [`catalog/quick-start.json`](catalog/quick-start.json). Catalog validation checks documentation consistency; installed-command execution is a separate CLI test requirement.

### Existing projects

Back up an existing project and review its layout before making changes. For a current `.agentic/` installation, use the documented CLI `upgrade` workflow and reconcile reported conflicts. For legacy root-level context, follow the [manual migration procedure](.agentic/docs/project/migration-v1.md).

The current CLI does not implement filesystem `ah migrate --apply`, `ah doctor`, or `ah new adr`. Experimental `ah agentic migrate` previews model-profile changes; it is not filesystem migration.

## What is supported

The [CLI command/compatibility contract](https://github.com/powerpuff-kitty/agentic-harness-cli/blob/main/docs/cli-contracts.md) is authoritative for the version you install.

| Surface | Boundary |
| --- | --- |
| Context composition and validation | Installs/checks project-context structure; does not fill in product decisions. |
| Audit and explicit artifact gates | Reports measured/unknown evidence and evaluates requested policy; a no-threshold gate is not verified application completion. |
| Architecture and design analysis | Experimental, deterministic source analysis with explicit coverage limits. |
| Design preservation and compilation | Review-required candidate identity and task-specific context; observations do not become approved intent automatically. |
| Agent procedures and adapters | See the agents repository's actual distribution and compatibility guidance; host delivery/enforcement must be verified separately. |

Permission declarations express intended policy. They do not by themselves configure a host sandbox, block tools or establish that an agent obeyed a rule. Agent hosting/orchestration is outside this project's scope.

## Repository responsibilities

| Public repository | Owns |
| --- | --- |
| `agentic-harness` | Project contracts, context templates, packs, policies, profiles, presets and schemas |
| [`agentic-harness-agents`](https://github.com/powerpuff-kitty/agentic-harness-agents) | Reusable skills, prompts and host integration procedures |
| [`agentic-harness-cli`](https://github.com/powerpuff-kitty/agentic-harness-cli) | Deterministic composition, analysis, artifact validation and explicit checks |

`.agentic/` is project-owned truth. `.agents/` holds reusable procedures. Skills may guide work but cannot silently redefine accepted architecture or policy.

## Contributions and roadmap

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), the relevant current truth and ADRs. The [audit-remediation roadmap](.agentic/plans/audit-remediation-2026-09-12.md) prioritizes truthful onboarding, native integration and executed verification before more catalog breadth.

All public source and collaboration metadata must follow the [public-surface policy](.agentic/docs/project/public-surface.md).

## License

Authored code and content use the [MIT License](LICENSE). Third-party material retains its licenses and attribution. Copied Harness templates and skills retain their MIT notice; independently authored application code may use its own license.
