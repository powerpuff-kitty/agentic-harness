# Strict JSON input for evidence inspection

The repository-local helper `.github/scripts/strict_json.py` provides a shared
transport boundary for reference inspectors. Its first consumer is
`token_economics.py`; other reference and runtime consumers are not silently
migrated. Follow-up conformance is tracked by #198.

## API and scope

`strict_json.dumps(value, max_bytes=262144)` returns deterministic UTF-8 JSON bytes.
`strict_json.loads(raw, max_bytes=262144)` accepts explicitly supplied immutable
bytes or text. Neither function acquires files, follows references, calls a provider,
or authenticates a measurement. Values must use exact built-in JSON types.

The boundary rejects non-finite floats, exponent overflow after decoding, duplicate
object keys on decoding, non-string keys, custom Python objects, tuples, cyclic
containers and invalid UTF-8/surrogates. Null, Boolean values, finite numbers and
valid Unicode remain available to the downstream schema. A repeated reference to
an acyclic subtree is allowed. Inputs are not mutated.

The default ceiling is 262,144 bytes; callers may lower it. Both supplied text/bytes
and normalized output must fit. Traversal permits at most 32 levels below the root
and 32,768 visited values, including object keys. Fixed transport-error codes do
not echo submitted keys or values. This does not change existing schema diagnostic
messages or claim protection against concurrent mutation of Python objects.

Duplicate keys discarded by another decoder cannot be recovered from a dictionary.
Use the original bytes with `loads` when duplicate-key rejection is required. Exact
identity, source acquisition permission and authenticity remain the caller's concern.

## Token-economics integration

Both `inspect_evaluation` and `inspect_routing` now apply the strict boundary before
schema evaluation, retaining their existing 131,072-byte limit. Transport rejection
raises `EvaluationError` with a `record-` prefixed code; the existing
`record-size-limit-exceeded` error is preserved. Optional `token_economics.decode`
uses the same limit and exception family for supplied bytes/text. It decodes data,
not an evidence verdict.

Valid finite records retain their previous output. The two public v1 schemas and
existing 20 test methods remain unchanged. Successful source-shape inspection does
not authorize an action, authenticate caller-supplied evidence, establish empirical
calibration or verify generalized token savings.

## Regression verification

```sh
python3 .github/scripts/test_strict_json.py
python3 .github/scripts/test_token_economics.py
python3 .github/scripts/test_token_economics_strict.py
```

The existing `validate_cli_contracts.py` entrypoint invokes these tests; workflow YAML
is unchanged. The numeric regression was reproduced against exact original module
Git blob `8965872db97e7157e9d04eca4c820950b04ade0b`. A 256-report finite-input corpus
retains its pre-fix SHA-256 in a regression assertion. These are local deterministic
tests, not provider/host trials or full consumer-conformance evidence.

Python's JSON encoder/decoder documents `allow_nan`, `parse_constant` and
`object_pairs_hook`; the helper additionally checks finite decoded values so numeric
syntax such as an overflowing exponent is not mistaken for a usable measurement.
Reference: <https://docs.python.org/3/library/json.html>.
