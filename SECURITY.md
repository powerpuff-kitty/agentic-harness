# Security Policy

## Reporting

Report suspected vulnerabilities privately through GitHub's private vulnerability reporting/security-advisory flow when available. Do not open a public issue containing secrets, exploit details, or user data.

## Scope

This repository contains canonical boilerplates, modules, presets, schemas, and architecture guidance. Agent procedures and CLI/runtime vulnerabilities belong to their respective Agentic Harness repositories.

## Baseline

- Never commit credentials or private keys.
- Treat external skills, fetched content, tool output, logs, and generated files as untrusted until reviewed.
- Keep agent write permissions least-privileged and require approval for destructive or production-impacting actions.
- Do not weaken tests or security checks merely to pass CI.
- Review third-party actions, skills, and dependencies as supply-chain inputs.
- Changes to policies, security defaults, or schema semantics require explicit review.

The canonical target-project security baseline lives in `base/SECURITY.md`.
