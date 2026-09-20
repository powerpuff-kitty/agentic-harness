# Security model

## Assets and boundaries

Titles and links may reveal personal interests. They remain in memory for the tab lifetime and must not be sent to analytics, logs, storage or external APIs. This reduces persistence; it does not protect against a compromised browser or extension.

Form text and link targets are untrusted. Browser rendering and external-link navigation are the relevant boundaries. There is no authentication, server or multi-user authorization surface in this scenario.

## Controls and abuse cases

Render titles through escaped text bindings, never raw HTML. Validate URLs as absolute HTTP(S) links and reject script/data schemes. Open external links with explicit opener isolation and no referrer; explain that following a link contacts an external site and is outside the app's data boundary. Do not fetch previews.

Test markup-like titles, invalid schemes, malformed URLs and length limits with synthetic values. Test that mutations affect only the selected entry and that reload clears session content. Inspect outbound requests and persistent storage before claiming the data-handling boundary is verified.

## Approval and recovery

Publication, destructive actions and production changes require approval; secret access is forbidden by the manifest. These are declared instructions, not host-enforced restrictions. No secrets are required by this scenario.

Reload resets state; there is deliberately no recovery after reload. Adding recovery/persistence or telemetry requires a reviewed product/security decision. Dependency review and relevant browser security checks remain pending until an implementation exists.
