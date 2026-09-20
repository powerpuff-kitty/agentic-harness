# Self-hosted skills

All eight skills declared in this repository's own manifest have local entrypoints. Seven Harness procedures are pinned to agents revision `90d0c95a3ffc6b2676cf62b6f8f5a21be501069b`; typesafe-ai retains independent provenance and unchanged content. This installs the selected procedures, not every skill in the 31-skill authoring collection.

## Conditional discovery and lifecycle context

Root AGENTS.md routes to the local skill index and the priority decision/efficiency procedures. Select one owner and expand only the references needed for the task. A broad lifecycle audit need not load composition details. Init, upgrade and migration consult agentic-app/references/composition.md. Completion-artifact work consults agentic-app/references/completion.md. The default entrypoint retains source authority, approval, preservation and verification limits.

Guidance does not require a Harness executable or TypeSafe account. Manual steps still need accepted canonical sources, edit authority and applicable validation. Missing tools or evidence remain unresolved; no fabricated verdict or schema replaces them. Actual Jev requires explicit provider/data permission. Installing the release skill does not authorise publishing a release.

## Source provenance and preservation

The current sync changes only agentic-app/SKILL.md among existing payloads and adds its two mode-specific guides, bringing reviewed imports from 27 to 29 files. All other 26 imported files, including the two older lifecycle shared guides, remain byte-identical. Those older references remain for preservation and are not default reads in the new procedure. No source files or customised content are removed.

The own-project lock records version metadata, the exact agents commit and SHA-256 checksums. The read-only verifier separately records reviewed Git blob identities. Version 0.5.0-beta.1 remains upstream metadata, not a newly published release. Skill inventory, own-manifest permissions and TypeSafe bytes are unchanged.

Source paths are skills/<skill>/<file> at the pinned agents revision, except MIT notices match the root LICENSE. The retained older lifecycle references map to upstream references/repository-discovery.md and references/context-engineering.md. New composition/completion guides originate inside upstream skills/agentic-app/references/. Authoring ownership remains the agents repository.

Lifecycle is now a self-contained source directory upstream, including its own MIT notice. It is not a newly enrolled sealed documentation archive. Canonical Harness preserves the two earlier shared copies in addition to the new upstream directory contents.

## Read-only verification

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

The verifier binds manifest selection, actual directories, index/router links, selected lock names, reviewed source bytes and local references. Its 25 regression methods include each missing imported file, changed bytes, wrong pins/checksums, missing or duplicate declarations, unknown directories, links and both new lifecycle routes. Failures do not repair or overwrite content. The earlier missing-manifest-declaration regression from #123 remains intact.

The checker uses this own-repository manifest authoring subset: unquoted top-level keys and two-space plain-name skills block lists. It is not a general YAML parser; unsupported forms fail rather than bypass binding. Full catalog validation remains separate. Vendor verification establishes a present nonempty entrypoint, not vendor byte provenance. A trusted quiescent checkout is assumed, and hashes are not signatures of trusted authorship.

## Source footprint and evidence limits

The lifecycle entrypoint decreases from 4,113 to 3,388 UTF-8 bytes (725 fewer, about 17.6%). New composition and completion guides are 3,509 and 2,615 bytes. Loading all three totals 9,512 bytes before licence, retained references, host context or target evidence; only default entrypoint size is reduced by the cited percentage. Extra detail is not free context or observed token savings.

Agents #41 tracks this change under #36/#25 and canonical #105/#114. Eleven upstream source/portability tests include the actual collection ZIP; ten were executed locally on a relevant-file snapshot and the complete suite passed candidate CI. Canonical import validation runs in its existing CI. The implementation assistant reviewed the source; this is not an independent behavioural evaluation.

No CLI/application implementation or downstream pin, workflow YAML, credentials, provider call or device-global installation changes. Automatic host loading, representative model outcomes and complete token usage remain unverified under agents #26/#32/#36. Prior delivery history and reproduced regression evidence remain in canonical #121/#123 and PRs #122/#124/#125.
