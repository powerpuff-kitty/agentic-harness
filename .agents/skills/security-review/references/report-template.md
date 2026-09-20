# Human security report template

This is a scoped review document, not attested execution evidence or a compliance certificate.

## Scope

Repository/change identity; authorization boundary; inspected trust transitions; unavailable runtime/deployment state; relevant target policy references. State whether any tests ran and whether they used only synthetic local inputs.

## Finding

**ID / confirmed defect or conditional risk / severity / confidence**

Affected asset and actor capability: ...
Entrypoint and source-to-effect path, with exact file/ranges: ...
Expected control from accepted policy: ...
Observed missing/ineffective control: ...
Counterevidence checked and remaining prerequisites: ...
Impact, smallest remediation and proposed local regression: ...
Reproduction status: source-only / approved synthetic test actually executed / not verified.

Synthetic example: an authenticated read handler queries an object by a supplied ID without applying the accepted ownership predicate. Cite the handler, query and mandatory-route evidence; describe a regression using two invented owners. Do not claim the deployed service is exploitable without its routing/configuration evidence. Do not attach real objects or credentials.

Counterexample: the handler delegates to a query abstraction that always scopes by principal and tenant. Verify the abstraction and alternate routes; missing inline checks alone are not a confirmed defect.

## Checks and residual risk

Keep separate lists for confirmed defects, scanner-only signals, conditional risks and excluded/not-checked areas. For every executed tool, include version, invocation, source/lockfile identity, scope and exit classification. Redact values before public sharing. End with remediation priority and the evidence needed to resolve uncertainty, not a universal statement that the project is secure.
