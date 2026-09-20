# Self-hosted skills

All eight skills declared in this repository's own manifest have local entrypoints. Seven Harness procedures are pinned to agents revision `7a82aafdaf692fc343e107708c67d6d1e67036a2`; typesafe-ai retains independent provenance and unchanged content. This installs the selected procedures, not every skill in the 31-skill authoring collection.

## Conditional discovery and lifecycle context

Root AGENTS.md routes to the local skill index and the priority decision/efficiency procedures. Select one owner and expand only the references needed for the task. A broad lifecycle audit need not load composition details. Init, upgrade and migration consult agentic-app/references/composition.md. Completion-artifact work consults agentic-app/references/completion.md. The default entrypoint retains source authority, approval, preservation and verification limits.

Guidance does not require a Harness executable or TypeSafe account. Manual steps still need accepted canonical sources, edit authority and applicable validation. Missing tools or evidence remain unresolved; no fabricated verdict or schema replaces them. Actual Jev requires explicit provider/data permission. Installing the release skill does not authorise publishing a release.

## Optional lossless log helper

The agentic-improvement skill now includes `scripts/compact_log.py`, introduced only in its conditional efficiency guide. The default SKILL.md and all triggers remain unchanged. For an explicitly selected, reviewed log and permitted local helper execution, run from the repository root:

```sh
python3 .agents/skills/agentic-improvement/scripts/compact_log.py /reviewed/path/check.log --budget-bytes 65536
```

The Python 3.10+ standard-library helper preserves supplied UTF-8 bytes, line endings, ordering and repetition counts; only adjacent identical lines are grouped. It retains a source hash/reference and checks reconstruction. It never executes log content, redacts secrets, infers a passed check, calls a provider or writes files. Review/redact input before use. Keep manual handling when the helper is unavailable or not permitted.

The 1 MiB input cap is enforced. The output budget is advisory: overflow returns the complete record and exit 1, not truncated evidence. Exit 0 means helper success; original producer completeness and process exit stay unknown. The envelope can be larger for nonrepetitive logs, so inspect actual byte accounting instead of assuming savings. This is a display helper, not a canonical execution receipt or permission grant.

Its version-2 bundle declaration explicitly names the optional Python script, manual fallback and no-auto-run boundary. Upstream v1 bundles remain documentation-only; a v1-only packager cannot consume v2 and must not silently omit the helper. No generic installer or host execution hook is added here.

## Source provenance and preservation

The current sync changes only the efficiency guide and its bundle declaration among existing payloads, adds the reviewed helper, and brings the integrity inventory from 29 to 30 imported files. All other 27 imported files, all SKILL.md entrypoints, the older lifecycle guides and TypeSafe content remain unchanged. No source files or customised content are removed.

The own-project lock records version metadata, the exact agents commit and SHA-256 checksums. The read-only verifier separately records reviewed Git blob identities. Version 0.5.0-beta.1 remains upstream metadata, not a newly published release. Skill inventory and own-manifest permissions are unchanged.

Source paths are skills/<skill>/<file> at the pinned agents revision, except MIT notices match the root LICENSE. The retained older lifecycle references map to upstream references/repository-discovery.md and references/context-engineering.md. Composition/completion guides originate inside upstream skills/agentic-app/references/. Authoring ownership remains the agents repository.

## Read-only verification

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

The verifier binds manifest selection, actual directories, index/router links, selected lock names, reviewed source bytes and local references. It now accepts the reviewed optional-script directory and explicit v2 declaration, but never imports or executes the helper. Its 28 regression methods include each missing imported file, changed bytes, wrong pins/checksums, missing or duplicate declarations, unknown directories, links, lifecycle routes, optional-script boundaries and explicit execution of the reviewed helper on one synthetic local log. These test executions are separate from integrity-only verification. Failures do not repair or overwrite content. The earlier missing-manifest-declaration regression remains intact.

The checker uses this own-repository manifest authoring subset: unquoted top-level keys and two-space plain-name skills block lists. It is not a general YAML parser; unsupported forms fail rather than bypass binding. Vendor verification establishes a present nonempty entrypoint, not vendor byte provenance. A trusted quiescent checkout is assumed; hashes are not signatures of trusted authorship or a script-safety certification.

## Evidence limits

Upstream agents #43 retains actual helper subprocess measurements for synthetic repetitive and distinct logs, including a negative case where envelope overhead grows the output. Source/output bytes are not provider tokens, billing savings or end-to-end model outcomes. All 24 helper and 14 packaging/trial tests passed upstream CI; 24 plus 12 staged-input tests ran locally. Canonical import/actual-helper validation runs in this repository's existing CI. Source review was by the implementation assistant, not an independent evaluator.

No CLI/application implementation or downstream pin, workflow YAML, credentials, live Jev call, release or device-global installation changes. Automatic host loading, representative model outcomes and complete token usage remain open under agents #26/#32/#36. Earlier lifecycle and import delivery evidence remains in agents #41 and canonical #121/#123 and PRs #122/#124/#125/#126.
