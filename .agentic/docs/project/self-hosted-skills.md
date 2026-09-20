# Self-hosted priority skills

This repository carries reviewed copies of `decision-intelligence` and `agentic-improvement` under `.agents/skills/`. Their authoring source remains `powerpuff-kitty/agentic-harness-agents`, pinned at `3bbafa3ee1c106edae94893e28b2760f5e3bc663`. This is repository-local delivery for #121 under the P0 #105/#114 workstreams, not a release or device-global update.

## Routing

The root `AGENTS.md` routes bounded evidence-support judgments and typed task classification to `decision-intelligence`; context/instruction optimisation routes to `agentic-improvement`. Routine code or documentation work does not have to load either as an additional wrapper. Both use conditional local guides.

Actual TypeSafe integration still routes to the separately maintained `typesafe-ai` skill. The vendor directory is unchanged by this import. Current-agent guidance never implies real Jev inference, provider credentials, free inference or permission to send repository context elsewhere. Existing project approval boundaries remain unchanged.

## Provenance and scope

`.agentic/lock.json` records the reviewed agents revision, the two imported skill versions and SHA-256 identities of all eight imported files, including their MIT notices. Version `0.5.0-beta.1` is retained from the source manifest; the commit and hashes identify these exact bytes. It is not a newly published distribution version.

The lock's `agents_source` now identifies these installed Harness imports. Other pre-existing names in the project's `skills` list are preserved declarations, not proof that their directories are installed. In particular, this change does not materialise agentic-app, codebase-audit, security-review, documentation or release. The TypeSafe directory has independent upstream provenance and is outside the agents import pin. No downstream CLI source pin changes here.

## Verify, do not overwrite

```sh
python3 .github/scripts/validate_self_hosted_skills.py
python3 .github/scripts/test_self_hosted_skills.py
```

The first command checks the actual files against reviewed Git blob identities and lock SHA-256 checksums, complete local bundle contents, licence bytes and root routes. It does not fetch sources, install files, execute a skill, open credentials or launch a model. The second verifies the real checkout before running mutation tests on temporary copies. The existing canonical contract-validation entrypoint also runs these regressions; no workflow YAML change is needed.

Missing guides, changed bytes, wrong pins/checksums, duplicate JSON keys, extra payload files, linked files/directories and absent routes fail. A failure never repairs or overwrites customised content. For a future update, review the source revision, compare all selected files, preserve local changes and update the lock and reviewed validator identities together. Do not change checksums merely to suppress a mismatch.

The validator assumes a trusted, quiescent checkout. Its Git hashes and SHA-256 inventory detect drift against reviewed values; they do not authenticate authorship. It checks only the two selected imports, not every declaration or the vendor payload. The bundle declarations are retained documentation metadata; these directories are not newly generated sealed ZIP archives.

## Evidence limits

The local regression run validates installation integrity, not a controlled skill trial. This continuation was assisted by the implementation agent with prior knowledge of the procedures and expected results; there is no independent or blinded baseline. Host automatic discovery/loading, observed model-token usage, actual Jev inference and empirical outcome improvement remain unverified under agents #26/#32/#36. Structural delivery is a prerequisite, not a substitute, for those measurements.
