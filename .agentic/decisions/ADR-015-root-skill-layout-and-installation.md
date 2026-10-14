# ADR-015: Expose independent skills at the source root

- Status: accepted
- Date: 2026-10-14
- Deciders: project owner
- Supersedes: none

## Context

The owner requested removal of the `skills/` container, five focused development
procedures and repository-playbook-informed improvements. The owner separately
accepted root `README.md` and `INSTALL.md` entrypoints in the skills source as
explicit exceptions to its folder-only layout.

## Decision

Place each skill in `<name>/` at the repository root. Retain each skill's entrypoint,
license and necessary local resources. Use document-relative Markdown links. Add
systematic-debugging, test-engineering, change-review, ci-triage and
repository-maintenance with narrow triggers and standalone guidance.

Keep `README.md` and `INSTALL.md` beside those folders. The README introduces
the catalog; INSTALL provides a copyable installation prompt, placement, provenance,
conflict guidance and honest loading checks. Native OpenCode skill loading uses the portable SKILL.md format; agent-profile adapters
are a separate concern. Source validation is not proof of a host's actual loading
or model adherence. New acceptance scenarios remain specifications until executed.

The CLI consumes exact source pins and stages only skill payloads in generated
build output before embedding them. Repository Git metadata and collection guidance
must never enter distributed skill payloads. Existing installation paths, skill
identifiers, historical release assets and project pins are preserved until an
explicitly reviewed update.

## Alternatives and consequences

Keep the nested collection directory, or add a general repository scaffold. The
owner chose direct skill discovery, an overview and one installation entrypoint.
The layout detail of ADR-014 is amended; its separation of reusable skills from collection
machinery remains intact.

Repository-playbook's local Markdown-link findings are repaired. Generic root
AGENTS.md, editor settings, PR template, collection CI and root-license
presence checks do not describe this explicitly reduced source contract. They are
recorded layout exceptions, not silently counted as passing checks. Licensing
remains explicit per skill. Unknown remote settings and manual/behavioral checks
remain unknown; no aggregate readiness score or automatic release is implied.
