# Shared evidence conformance fixtures

Canonical owner: this repository. Delivery tracking: #198 under #87.

`evidence-v1.json` is an exact-byte corpus for the Python reference decoder/schema
and the existing Rust CLI decoder/artifact validator. It contains 48 synthetic
cases: 19 transport cases and 29 Codebase Audit v2 shape cases. Each input has a
SHA-256 and explicit expected acceptance/rejection stage. Hex represents the one
invalid UTF-8 input; it is data, never executable content.

## Run the reference

```sh
python3 .github/scripts/evidence_conformance.py
python3 .github/scripts/test_evidence_conformance.py
```

The first command reads the fixed local corpus and independently pinned schema,
emits a result with exact corpus/schema identities, and exits 0 for a matching
corpus, 1 for a mismatch or 2 for malformed local input. A trusted quiescent checkout
is assumed. It never follows evidence references or executes fixture text. The 18
mutation tests verify identity drift, malformed metadata, unsupported scopes,
arbitrary-schema substitution, local-read restrictions and deliberately wrong
expectations. The existing machine-contract entrypoint runs this test suite.

## Consumer synchronization

Consumers copy the exact corpus bytes and retain this repository's commit/path,
corpus SHA-256 and scope in test-only provenance metadata. Review changes on both
sides; do not regenerate expectations to match a failing implementation. The Rust
consumer must exercise its existing `strict_json::decode` and `artifact::validate`
functions, not a reimplementation written just to pass these fixtures. Check its
pinned audit schema against the corpus schema digest before claiming compatibility.
No wholesale catalog or procedure pin promotion is required for test-only copying.

A changed expectation must fail the result comparison. A changed input must fail
its digest check. Consumer outcomes need actual test execution at an exact source
revision; fixture availability and this README do not establish that execution.
The corpus remains independently reviewable when a consumer has an older catalog.

## Limits

This corpus checks transport and audit shape only. A report with unknown scores or
incomplete scan evidence is structurally valid, not a verified completion or passed
policy gate. The reference output fixes completion/release verification to false.

The first slice does not establish installed command dispatch, numeric spelling
normalization (such as 2 versus 2.0), large-integer precision, cross-language
fingerprints, full size/depth/node-limit parity, evidence authenticity, freshness,
thresholds, other evidence families, host loading, Jev outcomes or release readiness.
Each corpus input is at most 4096 bytes. These limitations are retained in the
machine-readable corpus and result rather than dropped from passing reports.

#198 stays open for those broader consumer paths. #197 remains open for complete
command-documentation synchronization and tested released combinations.
