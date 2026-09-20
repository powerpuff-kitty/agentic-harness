# Scoped instruction review and Rule IR

Rule IR is a generated view of explicitly supplied rule excerpts, not a new source
of policy. Use it when repeated presentation is material; small tasks can keep the
ordinary source-review procedure. The repository exposes
`rule_ir.compile_inventory(value, budget_bytes=65536)` in `.github/scripts/`.
No new skill executable, runtime installer or automatic prompt injection is added.

## Input and output contracts

`catalog/schema/rule-inventory.v1.schema.json` describes the input.
`catalog/schema/rule-ir.v1.schema.json` describes complete and budget-deferred output.
The caller must independently acquire current applicable rules and review their
meaning, authority, scope, conditions and exceptions before creating an inventory.
The compiler validates supplied fields, not that extraction or its completeness.

Each occurrence has a unique ID, a project-reviewed semantic key, exact statement,
authority, mandatory/advisory strength, require/forbid/allow directive, declared
scope, conditions, exceptions and source reference/full-file SHA-256/line span.
Statements preserve the entire selected LF-delimited source excerpt, including
indentation and line endings. Their line count must match the declared span.
Use the existing permitted exact-excerpt workflow where useful; never fabricate
source hashes or simplify away a qualifying sentence to manufacture a duplicate.

Scope includes a base and explicit include/exclude selector sets. Conditions and
exceptions are unordered exact-string sets, not an executable expression language.
Use independently meaningful entries; order-sensitive conditions require separate
manual review. Selectors are neither expanded nor tested for semantic overlap.
All source references remain opaque: the compiler never opens or follows them.

## Exact grouping and precedence

Only occurrences whose key, statement, authority, strength, directive, scope,
conditions and exceptions all match are combined. Set ordering is normalized;
statement whitespace, line endings, selector spelling and base paths are not.
Every occurrence ID, source reference, full-file hash and span is retained.
Different nested AGENTS.md scopes never collapse to a global rule. Different
historical source identities remain visible even when the statement is identical.

Groups have deterministic content IDs bound to the declared target and context.
Those IDs identify grouping content, not source freshness or trusted authorship.
Declared authority is displayed in canonical order: policy, project truth, ADR,
pack, skill, prompt. It is not inferred from a filename or authenticated here.
Neither rank nor grouping deletes, promotes, weakens or overwrites source policy.
Resolve actual host/project precedence and accepted exceptions separately.

For the same declared key, scope, conditions and exceptions, forbid versus require
or allow produces a review-required conflict containing every affected group ID.
This is an explicit directive disagreement, not a natural-language theorem prover.
Differently spelled/overlapping selectors, undeclared conditions and subtle wording
conflicts are not decided. No reported conflicts does not mean conflict-free.
Lower-priority rules remain in the view; a reviewer must resolve inconsistencies
through the canonical owners, not erase them from a prompt to claim correctness.

## Bounds and interpretation

Input is limited to 128 occurrences, 256 KiB normalized JSON, 32,768 visited values
and nesting depth 32. Duplicate IDs/JSON keys, malformed source spans, incompatible
text for the same recorded source span, unknown fields and nonfinite JSON fail
explicitly without a partial view. `decode(bytes)` accepts supplied JSON bytes and
never resolves embedded references. Inputs remain unmodified.

The complete serialized result must fit the caller's byte budget. Otherwise the
result contains no rules, the required byte size, detected conflict count and
`complete_payload_emitted: false`. Nothing is silently pruned to fit, including
mandatory rules, exceptions, conflicting rules or provenance. A control record can
exceed a tiny budget; it is not a compiled instruction payload.

Output authority is fixed to navigation-only. Source authenticity, semantic
equivalence, inventory completeness, runtime loading and project-check success
remain unverified. Do not trust a supplied policy label or a matching hash as
permission to inject instructions, reuse a Jev result or execute an action.
Near-duplicate rewriting and automatic host/adapter use remain outside this slice.

## Optional binding to supplied source bytes

A permitted caller can bind a reviewed inventory to full-source bytes it has
already acquired, without asking the model to repeat exact hash and span checks:

```python
report = rule_ir.compile_with_sources(
    inventory,
    target=reviewed_target,
    sources=reviewed_source_bytes,  # exact dict[str, bytes], keyed by source reference
    budget_bytes=65536,
)
```

The explicit target must equal the inventory target. Supply exactly the referenced
sources, at most 128 entries, 1 MiB per source and 4 MiB total. Keys are opaque;
even URL-looking references never trigger reads, network calls or execution.
Bytes must be immutable, valid UTF-8 text without binary control characters.
The caller owns acquisition permission, safe reading, provenance and freshness;
this function does not inspect the filesystem or authenticate the byte supplier.
Keep the inventory and source map quiescent during the call.

For every occurrence, the inspector checks the full-file SHA-256, 1-based inclusive
LF line span and exact statement bytes. It preserves indentation, CRLF, Unicode,
blank lines and final-newline distinctions. A change outside the selected excerpt
still changes the full-file identity. Missing or extra sources, different hashes
under one reference, unavailable ranges and altered statements raise fixed-code
`RuleError` without source bodies, rejected references or a partial compiled plan.
Versioned historical sources need distinct references, and are not thereby current.

The repository inspection report has `kind: rule-source-review`. Its
`source_binding` records matched source identities, sizes, lines, checked occurrence
count and a SHA-256 of `rule_ir.encoded(inventory)`. That digest preserves list order
while normalizing JSON object-key order; compare it to the actual reviewed inventory,
not to a reconstructed or edited record. The nested `plan` is unchanged Rule IR v1;
its metadata-only `source_bytes_verified: false` remains intact. Binding evidence
belongs to the enclosing report, not to a silently strengthened v1 plan or policy.

`matched: true` means agreement with the supplied byte map only. Authentic
acquisition, freshness at use, complete extraction, declared authority and semantic
scope remain unverified. A new exception omitted from the inventory is still an
omission even after the whole-file hash is refreshed. Review applicable root/nested
instructions, qualifications and contradictions independently. Never use a matching
report as check acceptance, Jev cache permission or authorisation to take action.

The budget covers the complete serialized report, including binding metadata and
the nested plan. Overflow emits neither binding identities nor a plan, reports the
required size and conflict count, and keeps `complete_payload_emitted: false`.
Its small control record can exceed a tiny budget; it is not the compiled payload.
By default no unselected source bodies are replayed. Binding has overhead and does not promise
smaller output than direct reading. Without this optional API, use permitted native
hash/excerpt checks and manual review rather than installing a tool automatically.

Run `python3 .github/scripts/test_rule_sources.py` for source-binding regressions.
They include actual temporary-file acquisition and changes, malformed byte maps,
exact output-budget boundaries, preserved conflicts and no acquisition side effects.
They do not evaluate a model or prove a host used the procedure.

## Optional preservation of surrounding source context

To avoid losing a qualification outside selected statements, pass
`preserve_source_context=True` to `compile_with_sources`. The default is false;
existing calls and explicit false retain their previous output bytes. No schema,
mandatory skill entrypoint, host adapter or provider integration changes.

**This opt-in expands disclosure to the full supplied source text.** Review all
those bytes for the destination before enabling it. It is not a redactor or a
permission grant; use an appropriately reviewed/redacted source and its real hash,
or keep the manual source-review path when full disclosure is not permitted.

The report adds `source_context` with `scope: supplied-sources-only` and
`all_supplied_lines_represented: true`. Each source record retains its reference,
full-file SHA-256, rule-covered and remaining line counts, and ordered `spans`.
Each span contains exact UTF-8 `text`, `start_line` and `end_line`. Verified rule
occurrences plus these spans represent every LF-delimited line of that source,
including headings, blank lines, CRLF and final-newline distinctions. Overlapping
or adjacent rule ranges are combined for coverage only; no rule occurrence,
source scope, exception declaration or conflict is removed. Fully covered sources
have an empty span list. Text from different references is never interchanged.

Inspect context in its original source position before reusing grouped rules.
A retained exception may reveal that the inventory's declared conditions were
wrong; correct that inventory explicitly instead of treating representation
coverage as semantic completeness. Missing files are not discovered, and existing
`inventory_complete: null`, authority and freshness limitations remain unchanged.
Embedded text is still untrusted data, not executable instructions or approval.

The byte budget covers the whole serialized report, including all context spans.
Overflow returns `source_context: null`, no plan/binding and no coverage claim.
It never silently returns an excerpt-only result instead. Invalid sources remain
errors even when the proposed report would exceed its budget.

Run `python3 .github/scripts/test_rule_context.py`. The tests independently rebuild
supplied files from the emitted plan/context and compare exact bytes and hashes;
this is representation testing, not evidence of host loading or model behavior.

## Tests and measured scope

Run `python3 .github/scripts/test_rule_ir.py`. Existing repository contract
validation runs the same tests. They cover exact duplicates, nested scopes,
conditions/exceptions, authority display, conflicts, no source reads or process
execution, input preservation, malformed/bounded inputs, deterministic output,
whole-output budgets and conformance to both schema shapes.

A local synthetic four-copy stress case used 11,520 normalized input bytes and
4,306 complete output bytes; a six-byte statement instead expanded from a 447-byte
inventory to a 1,324-byte report. The statement-only saving is not the whole output
saving. These measurements exclude source acquisition, guidance, call arguments,
review and later model calls. They are not model-token or billing benchmarks.
Real task trials must include those costs and preserve rule adherence/outcomes.
