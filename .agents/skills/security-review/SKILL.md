# Security Review Skill

Use for authentication, authorization, payments, secrets, personal data, uploads, webhooks, agent tools, external integrations, execution, and other trust-boundary changes.

## Procedure

1. Read `SECURITY.md` and the relevant architecture docs.
2. Identify assets, actors, trust boundaries, entry points, and side effects.
3. Review authentication and authorization independently.
4. Trace untrusted input from entry to storage/output/action.
5. Check tenant/user isolation.
6. Check secret handling and log exposure.
7. For agents, assess prompt injection, tool scope, confirmation boundaries, and data exfiltration paths.
8. Verify destructive/external actions are intentional, auditable, and ideally idempotent.
9. Add tests for discovered security invariants where practical.
10. Report remaining risks explicitly.

Do not claim a change is secure merely because tests pass.
