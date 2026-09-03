# Security Policy

## Reporting

Please report suspected vulnerabilities privately through GitHub's private vulnerability reporting/security-advisory flow when available. Do not open a public issue containing secrets, exploit details, or user data.

## Scope

Security includes the canonical boilerplates, reusable packs, policies, profiles, presets, schemas, and architecture guidance in this repository, plus dependent agent and CLI implementations in their respective repositories.

## Baseline

- Never commit credentials or private keys.
- Treat external skills, fetched content, tool output, logs and generated files as untrusted until reviewed.
- Keep agent write permissions least-privileged and require approval for destructive or production-impacting actions.
- Do not weaken tests/security checks merely to pass CI.
- Review third-party actions, skills and dependencies as supply-chain inputs.

The canonical target-project security baseline lives in `boilerplates/base/SECURITY.md`.
