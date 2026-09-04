# Security Policy

## Reporting

Report suspected vulnerabilities privately through GitHub's private vulnerability reporting/security-advisory flow when available. Do not open a public issue containing secrets, exploit details, or user data.

## Scope

This repository contains the canonical project contract, catalog variants, packs, policies, profiles, presets, schemas, and migration guidance. Agent-procedure and CLI/runtime vulnerabilities belong to their respective Agentic Harness repositories.

## Baseline

- Never commit credentials or private keys.
- Treat external skills, fetched content, tool output, logs, issues, and generated files as untrusted until reviewed.
- Keep agent and workflow permissions least-privileged; require approval for destructive, production, secret, publication, and release actions.
- Do not weaken tests or security checks merely to pass CI.
- Review third-party actions, skills, dependencies, and source pins as supply-chain inputs.
- Preserve existing project truth during init, upgrade, and migration; stop on unresolved canonical conflicts.
- Changes to policies, security defaults, schemas, or source ownership require explicit review.

The target-project security model is demonstrated in `.agentic/SECURITY.md` and in `catalog/variants/*/files/.agentic/SECURITY.md`.
