# Self-hosted skills

All eight skills declared in this repository's own manifest have local entrypoints. Seven Harness procedures are pinned to agents revision `5cad9ec18b3eff329feab0423b4447c9d9967ec3`; typesafe-ai retains independent provenance and unchanged content. This installs the selected procedures, not every skill in the 31-skill authoring collection.

## Conditional discovery and lifecycle context

Root AGENTS.md routes to the local skill index and the priority decision/efficiency procedures. Select one owner and expand only the references needed for the task. A broad lifecycle audit need not load composition details. Init, upgrade and migration consult agentic-app/references/composition.md. Completion-artifact work consults agentic-app/references/completion.md. The default entrypoint retains source authority, approval, preservation and verification limits.

Guidance does not require a Harness executable or TypeSafe account. Manual steps still need accepted canonical sources, edit authority and applicable validation. Missing tools or evidence remain unresolved; no fabricated verdict or schema replaces them. Actual Jev requires explicit provider/data permission. Installing the release skill does not authorise publishing a release.

## Optional lossless log helper

The agentic-improvement skill includes `scripts/compact_log.py`, introduced only in its conditional efficiency guide. The default SKILL.md and all triggers remain unchanged. For an explicitly selected, reviewed log and permitted local helper execution, run from the repository root:

```sh
python3 .agents/skills/agentic-improvement/scripts/compact_log.py /reviewed/path/check.log --budget-bytes 65536
```

The Python 3.10+ standard-library helper preserves supplied UTF-8 bytes, line endings, ordering and repetition counts; only adjacent identical lines are grouped. It retains a source hash/reference and checks reconstruction. It never executes log content, redacts secrets, infers a passed check, calls a provider or writes files. Review/redact input before use. Keep manual handling when the helper is unavailable or not permitted.

The 1 MiB input cap is enforced. The output budget is advisory: overflow returns the complete record and exit 1, not truncated evidence. Exit 0 means helper success; original producer completeness and process exit stay unknown. The envelope can be larger for nonrepetitive logs, so inspect actual byte accounting instead of assuming savings. This is a display helper, not a canonical execution receipt or permission grant.

The version-2 bundle declaration explicitly names optional Python scripts, manual fallbacks and no-auto-run boundaries. Upstream v1 bundles remain documentation-only; a v1-only packager cannot consume v2 and must not silently omit helpers. No generic installer or host execution hook is added here.

## Optional selected-evidence freshness

The same skill now includes `scripts/evidence_snapshot.py` and a conditional `references/evidence-reuse.md` guide. Capture and compare require a fresh explicit file selection and task/criteria scope; record paths cannot expand read authority. Hashes detect actual selected-byte changes, including same-size edits with restored timestamps and changed policy with unchanged code. Root/scope changes, missing files and removed selections require refresh. No file bodies, task text or absolute root paths are returned.

From this repository, for an approved source selection:

```sh
python3 .agents/skills/agentic-improvement/scripts/evidence_snapshot.py capture \
  --root . --scope 'review selected Harness guidance; criteria v1' \
  --file AGENTS.md --file .agentic/manifest.yaml
```

The helper writes only stdout; persist it only to a reviewed new location when needed. Compare that snapshot with the same explicit selection and current scope using `compare /reviewed/snapshot.json` instead of `capture`. Exit 0 means matching selected bytes or successful capture, not a passed check. Exit 1 means refresh required; exit 2 means invalid input. Paths and hashes are not anonymisation, and files must already be reviewed non-secret text.

Up to 128 explicit files, 1 MiB each, with an 8 MiB read allowance and 128 KiB snapshot input. Rejected text reads also consume the allowance. No Git access, discovery, network/provider calls or source writes. Unselected/new dependencies and applicable policies still require scope discovery. Matching hashes neither prove completeness nor authenticate an earlier finding or restore forgotten context. Do not treat them as an automatic Jev-result cache. Hashing adds local I/O and report overhead; no measured token saving is asserted.

## Source provenance and preservation

This sync updates only the efficiency guide and bundle declaration among existing payloads and adds the freshness helper and its local guide. The inventory increases from 30 to 32 imports. The other 28 imported files, including all SKILL.md entrypoints, the existing log helper, older lifecycle guides and TypeSafe content remain unchanged. No source files or customised content are removed.

The own-project lock records version metadata, the exact agents commit and SHA-256 checksums. The read-only verifier separately records reviewed Git blob identities. Version 0.5.0-beta.1 remains upstream metadata, not a newly published release. Skill inventory and own-manifest permissions are unchanged.

Source paths are skills/<skill>/<file> at the pinned agents revision, except MIT notices match the root LICENSE. The retained older lifecycle references map to upstream references/repository-discovery.md and references/context-engineering.md. Composition/completion guides originate inside upstream skills/agentic-app/references/. Authoring ownership remains the agents repository.

## Read-only verification

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

The verifier binds manifest selection, actual directories, index/router links, selected lock names, reviewed source bytes and local references. It never imports or executes helpers. Its 29 regression methods cover each missing imported file, changed bytes, wrong pins/checksums, missing or duplicate declarations, unknown directories, links, lifecycle routes and optional-script boundaries. Explicit tests execute copied reviewed helpers on synthetic inputs separately from integrity checking, including snapshot capture, unchanged comparison and a same-size change. Failures do not repair or overwrite content. The original missing-manifest-declaration regression remains intact.

The checker uses this own-repository manifest authoring subset: unquoted top-level keys and two-space plain-name skills block lists. It is not a general YAML parser; unsupported forms fail rather than bypass binding. Vendor verification establishes a present nonempty entrypoint, not vendor byte provenance. A trusted quiescent checkout is assumed; hashes are not signatures of trusted authorship or a script-safety certification.

## Evidence limits

Agents #45 tracks the freshness helper under P0 #36/#26. Thirty-two helper/budget tests passed locally on the staged relevant-file snapshot; complete upstream CI additionally passed three standalone/collection/prepared-trial tests. Candidate and merged-main source identities are recorded on agents PR #46. These tests validate file handling and byte comparison, not independent model behaviour.

Upstream agents #43 retains actual log-compactor subprocess measurements for synthetic repetitive and distinct logs, including the negative case where envelope overhead grows output. Source/output bytes are not provider tokens, billing savings or end-to-end model outcomes. Canonical import and actual-helper validation run in this repository's existing CI. Source review is by the implementation assistant, not an independent evaluator.

No CLI/application implementation or downstream pin, workflow YAML, credentials, live Jev call, release or device-global installation changes. Automatic host loading, representative model outcomes and complete token usage remain open under agents #26/#32/#36. Earlier lifecycle/import evidence remains in agents #41/#43 and canonical #121/#123 and PRs #122 through #127.
