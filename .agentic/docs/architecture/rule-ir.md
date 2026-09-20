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
