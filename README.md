# Agentic Harness

Canonical architecture, templates, boilerplates, packs, policies, profiles, schemas, examples, and project guidance for agent-native software repositories.

This repository is the **source of truth** for what Agentic Harness projects are and how they should be structured. Agent behavior lives in [`agentic-harness-agents`](https://github.com/powerpuff-kitty/agentic-harness-agents); deterministic tooling lives in [`agentic-harness-cli`](https://github.com/powerpuff-kitty/agentic-harness-cli).

## Start here

```text
agentic-harness/
├── ARCHITECTURE.md       ecosystem and repository model
├── CONCEPTS.md           template/pack/policy/profile vocabulary
├── templates/            canonical project shapes
├── boilerplates/         opinionated starter compositions
├── presets/              machine-readable compositions
├── packs/                reusable knowledge and constraints
├── policies/             mandatory rules
├── profiles/             organization/team defaults
├── schema/               machine-readable contracts
├── examples/             reference outcomes and examples
├── docs/                 deeper architecture guidance
└── marketing/            Agentic Harness product messaging
```

## Templates

Current canonical templates:

- `templates/base`
- `templates/web-app`
- `templates/backend-api`
- `templates/saas`
- `templates/monorepo`
- `templates/library-sdk`

Templates define repository shape. They are deliberately easy to browse and are not hidden behind runtime implementation details.

## Boilerplates and presets

A **template** is a structural shape. A **boilerplate** is a documented, opinionated starting configuration built from a template plus packs, policies, profiles, and agent skills. Machine-readable preset definitions live in `presets/`.

See [`boilerplates/README.md`](boilerplates/README.md).

## Canonical-source rule

The other Agentic Harness repositories consume this repository rather than redefine its architecture:

```text
agentic-harness (canonical truth)
        ↓
agentic-harness-agents (skills / prompts / adapters)
        ↓
agentic-harness-cli (deterministic application / audit / validation)
```

If architecture, templates, packs, policies, profiles, or schemas change, change them here first. Agent prompts and CLI behavior should then adapt to that accepted source.

## Design systems

The design-system pack defines canonical design-system knowledge. Agent procedures should infer required components from product surfaces, prefer existing design-system components/tokens, and surface design-system compliance during audits when a design system is active.

## Related repositories

- **Agents:** https://github.com/powerpuff-kitty/agentic-harness-agents
- **CLI:** https://github.com/powerpuff-kitty/agentic-harness-cli
