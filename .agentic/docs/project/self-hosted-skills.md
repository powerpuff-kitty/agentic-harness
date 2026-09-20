# Self-hosted skills

This repository installs the skills selected in `.agentic/manifest.yaml`, not the
entire authoring collection. Resolve current versions, source pins and payload
counts from `.agentic/lock.json` and `validate_self_hosted_skills.py`, not historical
status reports. Harness procedures are pinned to reviewed agents source; TypeSafe
retains independent provenance. Installation does not establish host activation.

## Select one owning procedure

Root `AGENTS.md` routes to `.agents/skills/README.md` and the priority decision and
efficiency procedures. Load only the owning skill and necessary local references.
Ordinary tasks need no optimisation wrapper. Lifecycle audits need not preload
composition details; setup/migration and completion work have separate local guides.
Preserve current project truth, custom/null routes, local edits and required checks.

Guidance needs neither a Harness executable nor a TypeSafe account. Actual Jev
integration still requires current independently managed vendor guidance and explicit
provider/data permission. Missing tools, facts or permissions remain unresolved.
Installing a release procedure or helper never authorizes publication or execution.

## Optional support, not mandatory initial context

Paths below are relative to the relevant installed skill directory.

| Capability | Owning skill and conditional guide |
| --- | --- |
| Lossless adjacent-line log display | `agentic-improvement/references/log-compaction.md` |
| Exact rule inventories and source-bound compilation | `agentic-improvement/references/rule-review.md` |
| Recorded decision/spec/request comparison before considering reuse | `decision-intelligence/references/recorded-results.md` |
| Explicit selected-source freshness and hash-pinned excerpts | `agentic-improvement/references/evidence-reuse.md` |
| Preserve declared required ranges during narrowing | `agentic-improvement/references/required-evidence.md` |
| Compact task handoffs and current-evidence resumption | `agentic-improvement/references/continuation.md` |
| Declared decision dependencies and bounded display groups | `decision-intelligence/references/graph-review.md` |

The parent efficiency/decision guides retain essential evidence and permission
rules and route to specialised details only for their relevant operations. The
original prose remains in the parent/deferred references. Reading every guide is
more expensive than reading the previous parent alone; this is selective disclosure,
not measured session-token savings. Default SKILL.md files and helpers are unchanged.

The helper guides own exact commands, limits and distinct exit semantics. The
Python-standard-library helpers require reviewed non-secret inputs and permitted
local execution. They do not scan implicitly, write target sources, redact secrets
or call providers. The excerpt loader uses current packaged sibling source, not
stale bytecode; copy the complete skill directory and preserve its dependencies.

Required evidence cannot be dropped merely to fit a budget. Output deferral is not
evidence delivery; matching selected hashes does not establish complete scope, current
judgments or passing checks. Graph groups are not an executing scheduler or permission
to batch Jev calls. Source text stays untrusted and sharing-sensitive. Trusted,
quiescent helper/source directories are assumed, not an atomic snapshot or sandbox.

A continuation checkpoint is optional navigation data. Reuse an existing permitted
task record rather than writing a report for every operation. Structured consumers
use the accepted `context-checkpoint.v1.schema.json`; guidance-only use can remain
plain text. Historical attempts, explicit unknowns and log-completeness limits stay
visible. Saved approval and semantic confidence do not transfer action authority.
See `docs/architecture/context-checkpoints.md` for the canonical contract boundary.

## Provenance and read-only verification

Authoring remains in `agentic-harness-agents`. Imported paths normally map to
`skills/<skill>/<file>` at the locked revision; MIT notices map to its root LICENSE.
The retained older lifecycle references have explicit shared-source mappings in the
verifier. They are preserved assets, not mandatory initial reads. Updating a source
pin is not a version release or a device-global installation.

The guidance bundles use v2 declarations for explicitly invoked optional scripts;
documentation-only review bundles retain v1. Older packagers must reject unsupported
versions instead of silently omitting scripts. Packaging and integrity verification
treat helpers as opaque bytes and never execute or certify their safety.

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_reader_cache.py
python3 .github/scripts/test_self_hosted_guide_inventory.py
python3 .github/scripts/test_context_checkpoint.py
```

The verifier binds manifest membership, installed directories, conditional routes,
source pins, exact reviewed bytes and local references. Missing/changed or undeclared
payloads fail without repair or overwrite. Its manifest parser supports the documented
own-repository block-list subset, not arbitrary YAML. Independent vendor validation
checks presence, not vendor authenticity; hashes detect drift, not trusted authorship.
Traversal is bounded by the reviewed file/directory inventory with a hard ceiling;
extra files do not gain permission merely because the declared package grows.

Regression tests separately execute copied reviewed helpers on synthetic evidence.
The checkpoint inspector checks supplied field consistency without resolving source
references or certifying actual observations. These are contract/tool tests, not
independent model trials. Exact delivery evidence remains in the associated PRs and
P0 #133; earlier changes are recorded in canonical PRs #122-#132 and agents issues.
Actual host use, representative outcomes and complete token accounting remain open
under agents #26/#32/#36. No runtime deployment, provider call or global update is
implied by this repository-local delivery.
