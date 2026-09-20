# security-critical

Use when compromise, privacy loss, fraud, or integrity failure has high impact.

This pack supplements `SECURITY.md`; it does not replace application-specific threat analysis or establish runtime restrictions.

## Decisions to record

| Decision | Required project detail |
| --- | --- |
| Assets and data classification | Identify sensitive fields, integrity-critical actions, storage locations, retention and deletion behavior. |
| Trust boundaries | Map actor → entry point → authorization decision → resource; name tenant, process and external-provider boundaries where applicable. |
| Least privilege | Record who can perform each consequential action, where permission is enforced, and how revocation takes effect. |
| Secrets and dependencies | Name the approved secret delivery mechanism and dependency review process; never include secret values in context or evidence. |
| Audit and recovery | Define safe event fields, access/retention, recovery ownership and the last exercised restore/revocation scenario. |
| Change authorization | Identify security-boundary changes requiring approval under project policy and how that approval is mediated. |

Keep unknown controls explicit. A statement such as “authorization required” needs a mechanism and test evidence before it can be reported as checked or enforced.

## Example and anti-patterns

In a synthetic document service, the server checks the authenticated actor's access to the requested document on every read and write. An object ID from the browser is untrusted input. Test an authorized actor, an unrelated actor, revoked access and an absent session against the same resource. Logs may record an action and opaque resource identifier according to retention policy; they must not capture document contents or credentials by default.

Avoid relying on hidden buttons as authorization, reusing access decisions across tenants, granting broad credentials to simplify tests, or publishing raw request/response captures as proof. A repository permission declaration is not a sandbox; process separation alone does not restrict filesystem or network access.

## Evidence and completion

- Update the affected threat model and trace each changed trust boundary to a control and an adversarial test.
- Test denial paths as well as success, including malformed input, cross-resource access and revoked privileges where relevant.
- Review dependency changes and sensitive output/logging paths; state scanner coverage and skipped inputs.
- Exercise the relevant recovery path with synthetic data in an authorized environment. Document untested recovery separately.
- Report approval, instruction delivery, executed checks and enforced restrictions independently, with evidence identities and known limits.

Missing tools, unexecuted tests or an unknown enforcement mechanism remain unresolved. They cannot become a passing security claim because this pack was installed.
