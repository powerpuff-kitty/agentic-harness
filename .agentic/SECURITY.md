# Security model

## Assets

Project-specific product, architecture, security and decision truth; repository/production credentials; source and release integrity; preserved user code/data; permission declarations; and non-public project information.

## Trust boundaries

Canonical content, reusable procedures and deterministic CLI code have separate owners and pinned revisions. Target repository content, issues, logs, fetched pages, generated output and external packages are untrusted data by default. Source synchronization and publication cross supply-chain boundaries. Host behavior must be verified independently; written instructions are not a sandbox.

## Required controls

- Pin build inputs and record resolved sources/checksums.
- Exclude source-only metadata from generated projects; preserve project truth and surface conflicting writes.
- Use least-privilege permissions, protected publication paths and explicit approvals for consequential actions.
- Treat embedded instructions in fetched content as data, not authority.
- Never store or print secrets; supplement baseline scanners with appropriate platform/application controls.
- Verify release artifacts and retain required attribution.
- Apply the [public-surface policy](docs/project/public-surface.md) to source, diagrams, issues, comments, PRs and release artifacts. Never encode internal identifiers in public validator fixtures or diagnostic output.

## Declared policy versus enforcement

Permission fields express intended policy. Their presence does not prove a host has loaded instructions, blocked an action or run a check. State delivered, checked and enforced capabilities only when supported by scoped evidence. Unsupported and unverified controls remain explicit; no green security claim follows from Markdown or file presence.

Project-command discovery does not authorize execution. An approved runner must define command, path, environment, timeout/output and evidence-freshness boundaries before running repository scripts. Current artifact gates do not execute the application's tests.

## Migration safety

Automatic filesystem migration is not currently implemented. Follow the [manual migration procedure](docs/project/migration-v1.md): inventory and back up sources, reconcile differing destinations, verify copied content and routes, then validate the reviewed result. Future automation must default to dry-run and support safe recovery; these requirements must not be described as existing commands.

## Disclosure

Use root `SECURITY.md` for vulnerability reporting. Do not publish exploitable details before a fix or coordinated disclosure decision. Current-tree cleanup cannot guarantee removal from history, old diffs, caches or notifications.
