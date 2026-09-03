# Agentic Harness

A canonical catalog of agent-native **boilerplates**, reusable packs, policies, profiles, presets, schemas, and architecture guidance.

This repository is the **source of truth** for what Agentic Harness projects are and how they should be structured. Agent behavior lives in [`agentic-harness-agents`](https://github.com/powerpuff-kitty/agentic-harness-agents); deterministic tooling lives in [`agentic-harness-cli`](https://github.com/powerpuff-kitty/agentic-harness-cli).

## Start here

```text
agentic-harness/
├── ARCHITECTURE.md       ecosystem and repository model
├── CONCEPTS.md           boilerplate/pack/policy/profile vocabulary
├── boilerplates/         canonical project starting points
├── presets/              machine-readable compositions
├── packs/                reusable knowledge and constraints
├── policies/             mandatory rules
├── profiles/             organization/team defaults
├── schema/               machine-readable contracts
├── docs/                 deeper architecture guidance
└── marketing/            Agentic Harness product messaging
```

## Boilerplate catalog

Current canonical boilerplates:

- [`boilerplates/base`](boilerplates/base)
- [`boilerplates/web-app`](boilerplates/web-app)
- [`boilerplates/backend-api`](boilerplates/backend-api)
- [`boilerplates/saas`](boilerplates/saas)
- [`boilerplates/monorepo`](boilerplates/monorepo)
- [`boilerplates/library-sdk`](boilerplates/library-sdk)

Each boilerplate is a real project starting point rather than a demo application. It defines a coherent initial repository shape and may be composed with packs, policies, profiles, presets, and agent skills.

There is intentionally no generic `examples/` directory here. Full demonstration applications belong in a separate examples repository if they become useful later.

## Presets

Presets are machine-readable named compositions that select a boilerplate and useful modules. They reduce configuration without creating a separate boilerplate for every stack variation.

## Canonical-source rule

```text
agentic-harness (canonical truth + boilerplates)
        ↓
agentic-harness-agents (skills / prompts / adapters)
        ↓
agentic-harness-cli (deterministic application / audit / validation)
```

If boilerplates, packs, policies, profiles, presets, or schemas change, change them here first. Agent prompts and CLI behavior should then adapt to the accepted source.

## Design systems

The design-system pack defines canonical design-system knowledge. Agent procedures should infer required components from product surfaces, prefer existing design-system components/tokens, and surface design-system compliance during audits when a design system is active.

## Related repositories

- **Agents:** https://github.com/powerpuff-kitty/agentic-harness-agents
- **CLI:** https://github.com/powerpuff-kitty/agentic-harness-cli
