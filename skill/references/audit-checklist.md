# Agent-Native Repository Audit Checklist

Score each item as present, weak, missing, or not applicable.

## Routing
- Root `AGENTS.md` exists and is concise.
- Agent instructions route to deeper sources instead of duplicating them.
- Nested instructions are used only where scope-specific rules are needed.

## Durable knowledge
- Product intent and constraints are documented.
- Architecture and boundaries are documented.
- Design rules and tokens are documented where applicable.
- Security assumptions and trust boundaries are documented.
- Domain terminology and business rules have a canonical location.

## Decisions and plans
- Durable technical/product decisions use ADRs or equivalent records.
- Active plans are distinguishable from durable decisions.
- Completed plans do not masquerade as current source of truth.

## Skills
- Repeated workflows are encoded as focused skills.
- Skills describe when to use them, procedure, constraints, and completion checks.
- Skills reference canonical project knowledge instead of copying it.

## Examples and evals
- Subjective output has accepted examples where useful.
- Deterministic requirements are enforced with tests, linters, schemas, or CI.
- Agent-specific evals exist for important workflows when practical.

## Cross-agent compatibility
- Agent-specific adapters are thin.
- `CLAUDE.md`, Cursor rules, Copilot instructions, and Gemini instructions do not fork project truth.
- The canonical source remains understandable without a specific vendor tool.

## Context hygiene
- Large instruction files are split into discoverable references.
- Agents are told to load only relevant context.
- External/untrusted content is treated as data rather than executable instruction.
- Secrets and credentials are excluded from agent-readable committed files.

## Maintenance
- Definition of done includes documentation updates when durable behavior changes.
- Broken links and stale instructions can be detected.
- Ownership or review expectations exist for high-impact architecture/security changes.

## Suggested output

```text
Agent-native score: <0-100>

Present
- ...

Weak
- ...

Missing
- ...

Conflicting
- ...

Recommended next actions
1. ...
2. ...
3. ...
```
