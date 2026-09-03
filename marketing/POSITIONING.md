# Positioning

## Category

Agentic Harness is a composable development harness for agent-native software projects.

It is not an IDE, coding model, hosted agent, or framework replacement. It sits on top of a software project and gives coding agents structured project truth, reusable procedures, deterministic checks, and governed composition.

## Problem

Agentic development often starts as scattered instruction files, prompts, copied rules, and vendor-specific configuration. As projects grow, those sources drift, conflict, become stale, and are difficult to audit or reuse across tools.

## Primary value proposition

Describe or inspect a project, resolve the right templates/packs/skills, then install a durable agent-native structure that can be used by multiple coding agents while keeping important rules testable and reviewable.

## Differentiation

- Vendor-neutral project architecture rather than one-agent configuration.
- Clear separation of durable truth, procedures, examples, evals, and temporary execution state.
- Composable templates, presets, packs, and skills rather than one monolithic instruction file.
- Native deterministic CLI for generation, validation, security checks, audits, compare, and gates.
- Safe upgrade model that preserves existing project-specific truth.

## Target users

Initial focus:
- developers using multiple coding agents;
- solo builders and small teams that want repeatable project scaffolding;
- teams standardizing agent instructions across repositories;
- agencies or platform teams that need reusable repository patterns;
- maintainers auditing whether a repository is ready for effective agentic development.

## Non-goals

Agentic Harness should not become a replacement for source control, CI, package managers, application frameworks, or the coding agents themselves. It should compose and govern those systems rather than duplicate them.
