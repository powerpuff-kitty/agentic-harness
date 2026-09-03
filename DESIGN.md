# Design

This file is the design-system index and source of truth for interface work.

## Design principles

- Reuse established patterns before inventing new ones.
- Use named tokens instead of one-off values.
- Prefer consistency, accessibility, and hierarchy over decoration.
- Ask for clarification when the design system does not cover a case.
- When a new pattern is accepted, document it and add an exemplar.

## Tokens

Define canonical tokens in `docs/design/tokens.md`:

- color by semantic job, not hue name
- typography in real sizes
- spacing scale
- radii
- elevation
- motion
- breakpoints

## Components

Document component contracts in `docs/design/components.md`.

## Copy

Document voice, terminology, labels, and prohibited phrasing in `docs/design/copy.md`.

## Anti-patterns

Document recurring rejected design choices in `docs/design/anti-patterns.md`.

## Exemplars

Accepted visual examples live under `examples/design/`.

## Decision log

When a durable visual/product-design decision changes, add an ADR or update the relevant design document instead of relying on chat history.
