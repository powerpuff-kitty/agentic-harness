# Security

Security is a cross-cutting product requirement, not a final checklist.

## Baseline rules

- Never commit secrets, credentials, private keys, or production tokens.
- Validate and authorize server-side; never trust client assertions.
- Use least-privilege access for users, services, and automation.
- Treat external input, tool output, retrieved documents, and model output as untrusted.
- Protect against prompt injection when agents consume external content.
- Separate read capabilities from write capabilities where practical.
- Require explicit user intent for destructive or externally visible actions.
- Log security-relevant actions without logging secrets or unnecessary personal data.
- Keep dependencies and runtime versions supported and patched.

## Agent-specific threats

For agentic functionality, review:

1. Prompt injection and indirect prompt injection.
2. Excessive tool permissions.
3. Data exfiltration through tools, logs, or model context.
4. Confused-deputy behavior across users/tenants.
5. Unsafe execution of generated code or shell commands.
6. Insecure persistence of agent memory.
7. Untrusted retrieved content overriding repository/system policy.
8. Non-idempotent or destructive actions triggered autonomously.

## Required review

Use `.agents/skills/security-review/SKILL.md` for security-sensitive changes.

Project-specific threat models and controls should be added under `docs/architecture/` or a dedicated `docs/security/` directory when the project grows.
