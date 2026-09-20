# Self-hosted skills

All eight skills declared in this repository's own manifest have local entrypoints. Seven Harness procedures are pinned to agents revision `6dfb44af12d96b1a2b4681ab3fdecc17baf9ea07`; typesafe-ai retains independent provenance and unchanged content. This installs the selected procedures, not every skill in the 31-skill authoring collection.

## Conditional discovery and lifecycle context

Root AGENTS.md routes to the local skill index and the priority decision/efficiency procedures. Select one owner and expand only the references needed for the task. Broad lifecycle audit need not load composition details. Init, upgrade and migration consult agentic-app/references/composition.md; completion-artifact work consults its completion.md. The default entrypoint retains source authority, approval, preservation and verification limits.

Guidance requires neither a Harness executable nor a TypeSafe account. Missing tools or evidence stay unresolved. Actual Jev needs explicit provider/data permission and its independently maintained official skill/live docs. Installing a release skill does not authorize publication. None of the optional helpers runs merely because its skill was loaded.

## Optional local helpers

All three helpers use Python 3.10+ standard library and must be explicitly invoked only when permitted. Review inputs for secrets before use. They neither redact sensitive data nor authorize actions, execute input text, call a provider or write source files. Manual review remains available without Python.

### Lossless log display

```sh
python3 .agents/skills/agentic-improvement/scripts/compact_log.py /reviewed/path/check.log --budget-bytes 65536
```

Adjacent identical lines are grouped with exact repetition counts, line endings, order and source identity. Reconstruction is verified. The 1 MiB input cap and advisory output budget are distinct: overflow returns the complete record and exit 1, not truncation. Exit 0 means helper success, not project-check success. Producer completeness and command exit remain unknown. Nonrepetitive logs can grow because of metadata; inspect the complete byte accounting.

### Selected-evidence freshness

```sh
python3 .agents/skills/agentic-improvement/scripts/evidence_snapshot.py capture \
  --root . --scope 'review selected Harness guidance; criteria v1' \
  --file AGENTS.md --file .agentic/manifest.yaml
```

Capture emits a snapshot to stdout. Persist only to a reviewed new location when useful; compare with `compare /reviewed/snapshot.json` and a fresh explicit root/scope/file selection. Record paths cannot expand read authority. Same-size edits, changed policy, missing files and root/scope/selection changes require refresh. Output contains no source bodies, task text or absolute root paths. Limits are 128 files, 1 MiB each, an 8 MiB read allowance including rejected text, and a 128 KiB snapshot.

Matching hashes are selected-byte evidence, not complete scope, authenticated previous judgments, retained model context, passing checks or a Jev-result cache. Unselected dependencies and newly applicable rules still need discovery. Hashes are not anonymisation; source inputs must be reviewed non-secret text.

### Declared decision dependencies

```sh
python3 .agents/skills/decision-intelligence/scripts/review_graph.py /reviewed/path/graph.json --group-size 4
```

The optional graph reviewer consumes a bounded subset of existing DecisionGraph v1. It displays topological layers and bounded review groups, flags repeated spec references without deleting nodes, and identifies deterministic reducer prerequisites without executing them. Missing dependencies, self-links, cycles and invalid reducer inputs suppress all groups. Duplicate node/edge declarations are malformed. Unrecognized extension fields are unsupported, not silently ignored or declared invalid under the full canonical schema.

Exit 0 means a reviewable declared structure, 1 means dependency defects, and 2 means unsupported/invalid/unavailable input. A same-layer group is not a provider batch authorization: compatible state, current sufficient evidence, actual spec semantics, provider support and permissions remain unchecked. Later judgments require accepted predecessor results; reducers must not convert missing results into success. Limits are 64 KiB input, 128 nodes, 32 reducers, 4096 dependency edges and a display width of 1 through 32. Source references in the graph are never followed.

## Provenance and distribution

This sync updates only decision-intelligence's guide and bundle declaration among existing imports, adds its graph-review guide and helper, and advances the own-project source pin. The inventory is 34 files. The other 30 existing imported files, all SKILL.md entrypoints, efficiency helpers, older lifecycle references, TypeSafe content and permission definitions are unchanged. No source files or customizations are deleted.

The lock retains the exact agents commit, upstream version metadata and SHA-256 checksums; the read-only verifier separately pins Git blob identities. Version 0.5.0-beta.1 is not a new release. Source paths are skills/<skill>/<file>, except MIT notices match root LICENSE and retained lifecycle shared guides map to upstream references/. Authoring remains in agentic-harness-agents.

Both guidance skills now use explicit v2 optional-script declarations with manual fallbacks. The three enrolled review bundles remain documentation-only v1. Older v1-only consumers must reject v2 rather than drop helpers. Packaging hashes opaque script bytes without executing or certifying them. Source installation is not host activation.

## Verification and limits

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

Integrity checking binds manifest membership, installed directories, conditional routes, source pins, checksums and local references without executing helpers or repairing files. The 30-method regression suite additionally invokes copied reviewed helpers on synthetic inputs. The decision test uses the canonical schema before checking graph order, cycle refusal and explicitly unsupported additive fields. Test execution uses the existing catalog-test jsonschema dependency; the helpers themselves use only standard library.

The manifest reader supports the own-repository plain block-list subset, not all YAML. Vendor verification establishes a nonempty entrypoint, not vendor provenance. File checks assume a trusted quiescent filesystem, not a sandbox or atomic snapshot. Hashes detect drift, not trusted authorship.

Agents #47 tracks the graph review under #32/#36; #45 and #43 retain freshness/log measurements and regressions. Upstream graph tests include 34 local algorithm/file/subprocess checks and four distribution checks in complete CI. Native checks and author-exposed examples are not independent model trials. Actual host activation, representative outcomes and complete token usage remain open under #26/#32/#36. Fewer displayed groups are not measured provider calls or token savings.

No CLI/application implementation, downstream source pin, workflow YAML, credential access, live inference, new release or device-global installation changes. Prior delivery and failure evidence remain in canonical #121/#123 and PRs #122 through #128; candidate and merged-main checks for this sync are recorded on its PR.
