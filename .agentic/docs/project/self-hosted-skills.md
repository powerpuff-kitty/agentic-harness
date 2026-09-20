# Self-hosted skills

All eight skills declared in this repository's own manifest now have local
entrypoints. Seven Harness procedures come from reviewed agents revision
`3bbafa3ee1c106edae94893e28b2760f5e3bc663`; `typesafe-ai` retains independent
provenance and its existing bytes. This completes #123 after the two priority
imports in #121. It does not install all 31 skills from the authoring collection.

## Conditional discovery

Root `AGENTS.md` keeps the direct decision/efficiency routes and links to the
local `.agents/skills/README.md` index for lifecycle, review, documentation and
explicitly authorised release work. Load one owning procedure and expand its
references only as needed. Installing the release skill does not authorise a
release. Uninstalled specialist handoffs remain unavailable rather than silently
triggering installations, extra agents or providers.

## Exact source and local dependencies

The lock retains the same agents revision and version `0.5.0-beta.1`, now with
seven selected names and SHA-256 checksums for all 27 imported files. No target
manifest/schema, vendor bytes, downstream source pins or runtime code changes.
The 19 additional files complete agentic-app, codebase-audit, security-review,
documentation and release, including necessary guides and exact MIT notices.

Source paths are `skills/<skill>/<file>` at the pinned agents revision, except
LICENSE files come from its root LICENSE. Lifecycle's two guides are exact copies
of upstream `references/repository-discovery.md` and
`references/context-engineering.md`, placed under its local `references/` folder.
Their source mapping is explicit in the verifier. The other review/priority guides
already originate inside their skill directories. Authoring remains upstream;
these are reviewed copies, not competing project truth.

Bundle declarations are retained where supplied upstream. Lifecycle, documentation
and release are ordinary local skill directories, not newly sealed archives.
No new distribution version, release or device-global update is claimed.

## Read-only verification

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

Verification binds the own-project manifest selection, actual skill directories,
conditional router/index links, exact selected lock names, reviewed Git blob
identities, SHA-256 checksums and necessary local references. Vendor checking is
limited to a present nonempty entrypoint; it does not certify vendor provenance.
Missing/duplicate/unknown declarations, missing guides, source drift, wrong pins,
extra imported files/directories and linked inputs fail without repair or overwrite.

The manifest-membership check deliberately supports this repository's simple
unquoted top-level keys and two-space plain-name skills block list, with comments.
Quoted/flow/anchor/merge/multi-document forms fail explicitly. This is a checked
authoring subset, not a general YAML parser or replacement for catalog validation.
Meaningful format or source changes require review of the verifier and tests.

## Reproduced defect and evidence limits

At regression commit `1ae321dacdb85d33057e17dadbca1cc7d5286c7b`, existing CI run
35478916477 failed exactly `test_removed_selected_manifest_declaration_is_rejected`:
removing decision-intelligence from the manifest did not raise InvalidImport.
The fix reads and binds the declarations rather than treating directory presence
as sufficient. The unchanged failing assertion remains in the regression suite.
Candidate and merged-main results are recorded in PR #124 and issue #123.

The local staged imports were hashed against their retrieved upstream Git blobs;
full checkout validation runs in the existing CI workflow. A trusted quiescent
checkout is assumed. Hashes detect drift, not trusted authorship. This is an
assisted engineering change with prior exposure, not an independent model trial,
automatic host activation, actual Jev inference or empirical token-saving result.
No credentials, paid providers, other project installs or downstream implementation
are involved. Broader behavioural/usage gates remain under agents #26/#32/#36.
