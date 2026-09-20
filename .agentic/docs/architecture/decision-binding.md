# Inspect recorded decision bindings

Use this optional repository contract inspection when reviewing an existing
DecisionSpec, DecisionRequest and DecisionReceipt together. Individual v1 schema
validity is not enough: the receipt can refer to a different state or revision,
or its generic result may not belong to the supplied decision's domain.

`decision_binding.inspect_binding(spec, request, receipt)` in `.github/scripts/`
uses the existing three v1 schemas without modifying them. `decode(raw)` accepts
explicit JSON bytes and rejects duplicate keys, nonfinite constants, malformed
UTF-8/JSON and oversized input. Inspection accepts at most 64 KiB of combined
normalized JSON, 8,192 visited values and nesting depth 32. It is repository tooling,
not a shipped skill executable, installer, provider adapter or runtime policy gate.

## What is compared

The supplied spec ID/revision must be requested uniquely and match the receipt.
Repeated request questions are ambiguous because v1 has no required per-occurrence
receipt binding. Input schema IDs/versions must match across all three documents;
versions are compared without coercing strings, floats or booleans to integers.
The receipt's state fingerprint must equal the request's recorded fingerprint.
Fingerprint strings remain opaque: this inspection does not recompute a payload
hash, authenticate source bytes or establish that the producer kept specs immutable.

Required coverage counts refer to distinct required requirement IDs, not optional
requirements or the number of raw evidence documents. Duplicate requirement IDs,
unknown missing IDs, inconsistent counts and incorrect coverage arithmetic are
reported. `min_count` and `max_age_seconds` require actual source review; this
inspector cannot establish them from evidence-reference strings. The `evidence`
used/missing lists must not overlap. It does not invent a mapping from those source
references to the spec's requirement IDs.

For produced Boolean decisions, `result.value` must be a real Boolean, not 0/1,
null or a string. For produced choices, it must be a case-exact declared option.
A supplied distribution must be nonempty, sum to one within 1e-6 and use only
allowed Boolean/choice labels. Sparse distributions are not forbidden by v1.
Coverage arithmetic uses absolute tolerance 1e-9. Missing distributions and
confidence stay missing; no probabilities are inferred.

### Ordered results

For produced ordinal decisions, the inspector supports the representations already
used by recorded-result evaluation: an exact declared level name, a finite numeric
position in the inclusive interval `0..len(levels)-1`, or a distribution over level
indexes. Fractional positions are allowed; an ordered position is not a probability
or a confidence score. Booleans, null, containers, unknown names and out-of-range
positions are rejected without coercion, rounding, clamping or renormalization.

Distribution keys must be canonical zero-based decimal indexes (`"0"`, `"1"`, ...),
not level names or aliases such as `"01"`, `"+1"`, whitespace or Unicode digits.
This optional inspector is deliberately stricter than permissive runtime readers;
existing schemas/readers remain unchanged. Historical receipts are not rewritten.
A string that looks numeric is a level name only when declared exactly in `levels`.

A distribution-only ordinal result is supported without inventing a point value.
When both fields are present, each is validated: a valid distribution cannot hide
an invalid value. The generic receipt does not specify whether the value is a mean,
mode or another statistic. Their relationship remains explicitly unchecked through
`ordinal-value-distribution-relationship`; no evaluator or policy is selected here.

Other decision primitives retain identity/coverage checks, but their result domain
is not validated here. `result_domain_checked` makes that distinction explicit.
Additive extension semantics and policy dispositions are not interpreted. The
existing schemas and legacy semantic validators remain unchanged.

## Consistency is not success

A well-formed abstention, provider failure or insufficient-evidence receipt can be
consistent with a request. Its recorded status is preserved and a non-produced
review reason remains. Produced partial-evidence results retain missing-evidence
review reasons even at confidence 1.0 or with a supplied `accepted` disposition.
The inspector never chooses a policy disposition or accepts a decision.

Output contains fixed codes and a schema-known status, not questions, result
bodies, source references, hashes or commands. Both input documents and historical
receipts remain unchanged. Current evidence, claim authenticity, provider execution,
calibration, cache eligibility and consequential authorization remain unverified.
All acceptance/authorization flags are false and model tokens are unknown.

Two distinct requests can have identical spec/state identities. Since receipt v1
does not require a request ID, this comparison cannot prove which request occurrence
produced a receipt. A provider hint is advisory, not permission to change providers.
Preserve independently recorded request/provider provenance for any actual reuse.

## Skill use and verification

The existing decision-intelligence guide gives the manual comparison procedure and
an optional route to this API when the target has accepted it. Ordinary judgments
need no extra wrapper, model or provider. A bare current-agent answer must not be
relabeled a DecisionReceipt or assigned invented hashes/confidence.

Run `python3 .github/scripts/test_decision_binding.py` and
`python3 .github/scripts/test_ordinal_binding.py` for the focused regressions.
Existing contract validation invokes the same tests. Fixtures are synthetic and do
not contain real Jev calls. Tests include individually schema-valid mismatches,
ambiguous questions, missing evidence, invalid finite outcomes, malformed input,
no reference reads and no mutation/content replay. They establish deterministic
behavior, not observed model adherence, runtime enforcement or token savings.
