# Security Policy

## Reporting

Please report suspected vulnerabilities privately through GitHub's private vulnerability reporting/security-advisory flow when available. Do not open a public issue containing secrets, exploit details, or user data.

## Scope

Security includes the source repository, composition CLI, audit tooling, bundled templates, reusable skills, packs, schemas, and agent/tool permission guidance.

## Baseline

- Never commit credentials or private keys.
- Treat external skills, fetched content, tool output, logs and generated files as untrusted until reviewed.
- Keep agent write permissions least-privileged and require approval for destructive or production-impacting actions.
- Do not weaken tests/security checks merely to pass CI.
- Review third-party actions, skills and dependencies as supply-chain inputs.

The bundled target-project security baseline lives in `templates/base/SECURITY.md`.
