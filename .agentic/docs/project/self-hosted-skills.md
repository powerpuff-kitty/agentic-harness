# Self-hosted skills

All eight skills selected by this repository's manifest have local entrypoints.
Seven Harness procedures come from the exact agents revision in `.agentic/lock.json`;
`typesafe-ai` retains independent provenance and unchanged content. Resolve current
versions, source pins and file identities from that lock and the read-only verifier,
not from historical examples. This installs the selected procedures, not the whole
31-skill authoring collection.

## Conditional discovery

Root `AGENTS.md` routes to the installed skill index and the decision/efficiency
procedures. Select the owning skill; expand only references needed for the task.
Ordinary tasks need no extra optimisation wrapper. Lifecycle audits do not preload
composition instructions. Setup/upgrade/migration use the local composition guide;
completion-artifact work uses the local completion guide. Core source authority,
custom/null routes, local edits, approvals and verification remain protected.

Guidance requires neither a Harness executable nor a TypeSafe account. Actual Jev
requires explicit provider/data permission and current independently managed vendor
guidance. Missing tools, facts or permissions remain unresolved. Installing a release
skill does not authorise a release; installing a helper does not authorise execution.

## Optional deterministic helpers

The efficiency skill now carries three explicitly invoked helpers:

| Helper | Scope | Conditional local guide |
| --- | --- | --- |
| `compact_log.py` | Lossless adjacent-line compaction of a named reviewed log | `agentic-improvement/references/efficiency.md` |
| `evidence_snapshot.py` | Capture/compare explicitly selected source hashes and scope | `agentic-improvement/references/evidence-reuse.md` |
| `extract_context.py` | Retrieve explicit source line ranges against expected file hashes | `agentic-improvement/references/evidence-reuse.md` |

Decision Intelligence separately carries `review_graph.py`; its local graph-review
guide defines the supported DecisionGraph subset. Layers are structural review,
not an executing scheduler or permission for a Jev batch. Repeated nodes remain
visible, and missing dependencies/cycles prevent grouping.

For source retrieval, set `SOURCE_SHA256` to the actual full-file `sha256:` identity
from a reviewed snapshot or native hash result, then run from this repository:

```sh
python3 .agents/skills/agentic-improvement/scripts/extract_context.py \
  --root /reviewed/project --span src/service.py 20 40 "$SOURCE_SHA256" \
  --span src/service.py 35 55 "$SOURCE_SHA256" --budget-bytes 65536
```

This merges the overlap, reads that file once and emits exact text for lines 20-55
with source/excerpt hashes and omitted-line counts. Numbering is inclusive and based
on LF; CRLF bytes are retained. A stale pin, bad range or later-file failure emits no
partial source payload. Exceeding the complete-envelope byte budget returns exit 1
and no excerpts, not silently truncated evidence. Exit 0 is retrieval success, not
verified project compliance; exit 2 rejects invalid, stale or unavailable input.
A tiny control record can exceed an extremely small budget.

The extractor reuses the reviewed sibling `evidence_snapshot.py`. Copy the complete
skill directory; no unrelated PYTHONPATH fallback is accepted. Its bounds are 128
span requests, 1 MiB per file and 8 MiB total reads, with a default 65,536-byte output
budget. Existing helpers keep their existing distinct bounds and exit semantics.

Helpers use Python 3.10+ standard library, require permitted execution and reviewed
non-secret inputs, and make no provider calls or source writes. They do not redact
secrets. Excerpt output contains source text and requires sharing review; hashes and
paths are not anonymisation. Mandatory rules, qualifiers, contradictions, callers
and tests cannot be discarded to fit a budget. Unselected dependencies still need
discovery. Matching bytes cannot authenticate an old judgment, restore lost context,
prove adequate evidence or certify a check. Trusted quiescent source/helper directories
are assumed; no atomic snapshot or hostile-filesystem sandbox is claimed.

## Provenance, packaging and verification

Authoring remains in `agentic-harness-agents`. Imported paths normally map to
`skills/<skill>/<file>` at the locked revision; notices match its root MIT LICENSE.
The two preserved older lifecycle guides map to upstream shared `references/`
paths explicitly recorded in the verifier. They remain installed for preservation,
not mandatory initial reads. No existing source or customised content is deleted.

This delivery adds the extractor and updates its bundle and reuse guide. All default
SKILL.md files, triggers, existing helpers, vendor content and permission definitions
are unchanged. The source lock and reviewed blob/SHA-256 identities cover 35 imports.
Upstream version metadata remains 0.5.0-beta.1; updating a source pin is not publishing
a release or replacing a global installation.

Both guidance bundles use explicit v2 optional-script declarations with manual
fallbacks; three enrolled review bundles remain documentation-only v1. Older v1-only
packagers must reject v2 rather than omit scripts. Packaging and integrity validation
retain scripts as opaque bytes, never execute them or certify script safety.

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

The verifier binds manifest membership, local directories, conditional routes,
selected lock names, exact reviewed bytes and references. The 31-test import suite
retains prior regressions and explicitly exercises copied helpers separately from
integrity-only verification. The new excerpt test checks overlap, budget deferral
and stale-pin refusal. Missing/changed files and undeclared helpers fail without
repair or overwrite. Manifest parsing remains the documented own-repository block-list
subset, not full YAML; vendor validation checks presence, not vendor authenticity.
Hashes detect drift but are not trusted-author signatures.

Upstream PR #50 records 26 local retrieval tests and four complete-CI distribution
checks. Reproducible synthetic outputs include both a large partial-source reduction
and growth for tiny input. They are byte measurements, not a representative model
benchmark. Source review is by the implementation assistant; independent host/task
and complete-token evidence remains open under agents #26/#32/#36. No live Jev
inference, runtime application/CLI change, downstream pin, workflow YAML, credential
access, new release or device-global update is part of this delivery.

Earlier delivery history and reproduced defects remain in canonical PRs #122-#129
and agents #41/#43/#45/#47. Usage detail stays in the owning skill-local guides
rather than being copied into this status document on every synchronization.
