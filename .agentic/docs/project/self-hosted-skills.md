# Self-hosted skills

All eight skills declared in this repository's own manifest have local
entrypoints. Seven Harness procedures come from reviewed agents revision
`9d029d60bec1ca827a278d0ab18a6ad3e4fc13dc`; `typesafe-ai` retains independent
provenance and its existing bytes. The initial complete delivery was #123 after
the two priority imports in #121. This does not install the full authoring collection.

## Conditional discovery

Root `AGENTS.md` keeps the direct decision/efficiency routes and links to the
local `.agents/skills/README.md` index for lifecycle, review, documentation and
explicitly authorised release work. Load one owning procedure and expand its
references only as needed. Installing the release skill does not authorise a
release. Uninstalled specialist handoffs remain unavailable rather than silently
triggering installations, extra agents or providers.

## Exact source and local dependencies

The lock retains version `0.5.0-beta.1`, seven selected names and SHA-256 checksums
for all 27 imported files. The exact commit, not the unchanged version label,
identifies the reviewed content. No target manifest/schema, vendor bytes,
downstream source pins or runtime code changes are part of this synchronization.

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

## Scope-preserving update from agents PR #38

Only agentic-improvement's SKILL.md and conditional efficiency guide change from
the previous agents pin `3bbafa3ee1c106edae94893e28b2760f5e3bc663`. The reviewed
source blobs are `85e7e54d8bd40b8286cedbbba2039b4780da24f2` and
`e7f7d28bbeb8c3109008f4fe2ccfb87e0df0c724`, respectively. All other imported
payloads, vendor content, manifest permissions and the 27-file inventory remain unchanged.

The procedure now makes applicability part of rule identity: equal text in
separate directories does not authorise deleting or globally hoisting a rule.
Diagnostic summaries retain check/test, location, phase and attempt. An unrelated
pass or a passing retry cannot hide failure evidence. Policy changes invalidate
policy-dependent findings even when source code and HEAD are unchanged.

UTF-8 source bytes, before/after at the two reviewed pins:

| File | Before | After |
| --- | ---: | ---: |
| SKILL.md | 3613 | 3731 |
| Conditional efficiency guide | 4798 | 4113 |
| Both files | 8411 | 7844 |

The always-loaded procedure grows by 118 bytes to state the safeguard; the optional
guide shrinks by 685 bytes. Their combined source is 567 bytes smaller (about 6.7%).
This is not a per-session token or billing result: a routine task may not load the
guide at all. Do not market the combined number as universally reduced context.

Four author-exposed walkthroughs and six synthetic grader tests live upstream in
agents PR #38. The prose records the implementation assistant's qualitative review;
it is not an isolated task trial, authenticated host trace or independent assessment.

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

The staged imports are hashed against retrieved upstream Git blobs; full checkout
validation runs in the existing CI workflow. A trusted quiescent checkout is
assumed. Hashes detect drift, not trusted authorship. No credentials, paid providers,
other project installs or downstream implementation are involved. Automatic host
activation, real Jev inference and comparative behavioural/usage gates remain
under agents #26/#32/#36.
