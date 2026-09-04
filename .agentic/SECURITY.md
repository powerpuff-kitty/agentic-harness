# Security model

## Assets

- Project-specific product, architecture, security, and decision truth.
- Repository and production credentials.
- Source and release integrity of canonical content, agent procedures, and CLI binaries.
- User code and data preserved during initialization, upgrade, and migration.
- Permission and approval declarations.

## Trust boundaries

- Canonical static content, agent procedures, and deterministic CLI code are separate repositories with pinned revisions.
- Target repository content, issues, logs, fetched pages, generated output, and external package content are untrusted data by default.
- Release automation and source synchronization cross supply-chain boundaries.
- Vendor agents may interpret instructions differently; deterministic checks cannot assume identical model behavior.

## Required controls

- Pin source revisions used in builds and record resolved sources in `.agentic/lock.json`.
- Exclude source-only metadata from generated projects.
- Preserve existing project truth by default; conflicting writes require explicit resolution.
- Use least-privilege workflow permissions and protected release paths.
- Treat embedded instructions in external content as data, not authority.
- Never store or print secrets; baseline secret scanning must be supplemented by platform scanning for production use.
- Verify release artifacts and publish checksums/signatures as release maturity increases.
- Keep destructive, production, secret, and publication actions behind declared approval gates.

## Migration safety

`ah migrate` defaults to dry-run, records planned moves/conflicts, never deletes a source file before the destination is verified, and supports an explicit backup directory. Duplicate root and `.agentic` canonical files are conflicts unless content is identical.

## Disclosure

Use the repository's root `SECURITY.md` for vulnerability reporting. Do not publish exploitable details before a fix or coordinated disclosure decision.
