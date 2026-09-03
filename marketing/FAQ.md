# FAQ

## What is Agentic Harness?
A composable framework and native CLI for turning software projects into structured environments for coding agents.

## Is it another coding agent?
No. It organizes project truth, procedures, templates, policies, and deterministic checks that coding agents can use.

## Does it replace AGENTS.md or vendor-specific files?
No. It can use a concise `AGENTS.md` as a router and keep vendor-specific files as thin adapters to shared canonical truth.

## Does it require Rust?
Only when building Agentic Harness from source. End users should use precompiled binaries.

## Can it be added to an existing project?
Yes. The upgrade model is intended to inspect the repository and add missing harness structure without blindly overwriting project-specific knowledge.

## Is it tied to a framework or language?
No. Templates and packs can encode framework-specific knowledge, but the harness architecture is designed to remain framework-neutral.

## Is it a package manager?
Not exactly. It behaves more like a composable project overlay/generator: templates establish shape, packs add knowledge and constraints, skills add procedures, presets compose useful combinations, and `ah` validates/applies them.
