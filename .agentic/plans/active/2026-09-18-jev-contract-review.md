# Jev contract alignment review

Reviewed 2026-09-18 against issue #106 and PR #108 head `10a4d0cd416ee723e1d60a9116ac035afc671999`. This is a local review, not an accepted contract change or approval to publish.

## Recommendation

Complete the existing #108 contract before implementing its CLI consumer. Do not start a second competing contract. The broader adoption roadmap still needs #86's runnable Vue/TypeScript fixture and CLI #55's check executor; the TypeSafe skill installation does not resolve those dependencies.

## Findings

1. **High: successful results lack semantic validation.** The PR validator accepts an empty `answers` object on success, a selected Choice absent from its distribution, four probabilities of 0.9, and a Score of 9 for a three-level rubric. Reproduced by copying the validator's positive result and mutating each condition independently. Add at least one answer on success and a request/result semantic validator enforcing exact question IDs/types, candidate/level correspondence, normalized distributions with a documented tolerance, and score bounds/weighted-value consistency. JSON Schema alone cannot enforce all cross-record relationships. Provider adapters must apply the same invariants before consuming results.

2. **High: current issue scope exceeds the PR's evidence model.** Issue #106 now explicitly requires distinguishing coding-agent advice, runtime provider judgments and deterministic verification; abstention, insufficient and contradictory evidence; source references; and optional confidence with provenance/calibration status. The PR has only success and operational failure statuses, always requires numeric Choice/Score confidence, and has no producer/evidence-source distinction. Add explicit representations and positive/negative examples without treating agent self-confidence as calibrated provider output.

3. **Medium: policy thresholds and configuration provenance are absent.** `decision-policy` supports allowed classes, a failure mode and resource limits, but no reviewable thresholds. Requests/results carry state/question digests but no project-policy/configuration revision. Add the policy linkage and define how uncertainty selects fallback/escalation so a result can be assessed against the policy used at evaluation time. A question digest does not identify the policy that consumed its answer.

4. **Medium: supported TypeSafe input subset is undocumented.** The current HTTP API permits structured instructions; the PR restricts all question instructions to single-line text. Either support structured inputs or document the deliberate v1 subset and reject unsupported inputs explicitly. This is a compatibility restriction, not proof of a broken wire mapping.

## Aligned portions

The documented endpoint, bearer authentication, `jev-latest` alias, batched question map and three primitive mappings align with the live API reference. The explicit advisory boundary and `authorization_granted: false` are appropriate. These declarations still require enforcement in consuming code.

## Evidence and limits

- Read the installed TypeSafe skill and live documentation index/API reference; no credentials accessed and no inference request made.
- Executed the PR's existing validator from extracted added files using the existing isolated Python environment with jsonschema 4.26.0: passed.
- All four malformed-result probes above were accepted by that validator. They establish validation gaps, not observed production incidents.
- Local catalog validation and `git diff --check` passed after skill installation.
- No PR branch edits, remote comments, issue changes, publication or integration tests performed for this review.

Sources: [issue #106](https://github.com/powerpuff-kitty/agentic-harness/issues/106), [PR #108](https://github.com/powerpuff-kitty/agentic-harness/pull/108), [TypeSafe HTTP API](https://docs.typesafe.ai/api.md), [adoption issue #86](https://github.com/powerpuff-kitty/agentic-harness/issues/86), [CLI executor #55](https://github.com/powerpuff-kitty/agentic-harness-cli/issues/55).
