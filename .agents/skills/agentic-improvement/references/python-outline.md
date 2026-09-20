# Locate Python definitions before reading bodies

Use only when relevant Python source is already identified but its line ranges are
not. Prefer a native targeted read when its location is known or the file is small.
This optional mode extends the existing [excerpt helper](scripts/extract_context.py);
copy its reviewed sibling reader too. It requires permitted local execution and
reviewed non-secret inputs, not a Harness runtime, new skill or provider account.
Without a compatible interpreter/helper, inspect the selected source manually.

## Outline, then retrieve

Set `SOURCE_SHA256` to the actual full-file `sha256:` identity from a reviewed
snapshot or native hash result. From this skill's root:

```sh
python3 scripts/extract_context.py --root /reviewed/project \
  --outline src/service.py "$SOURCE_SHA256" --budget-bytes 65536
```

Repeat `--outline PATH SHA256` for other explicitly selected `.py` files. Each
unique path is read once; a conflicting pin or stale source rejects the whole
operation. The result locates named functions, async functions and classes, including
nested and conditionally defined ones. It returns Python-normalized names, lexical
parents, local line/column identities and inclusive decorator-to-end line ranges.
Repeated names retain distinct identities. It omits bodies, defaults and docstrings.
Metadata names can still be sensitive; this is not redaction or anonymisation.

Use a returned `start_line` and `end_line` with the same source pin in a separate
`--span` invocation. Include any independently required policy, counterevidence,
callers and tests using the [required-evidence guard](references/required-evidence.md).
An outline never satisfies source requirements: combining `--outline` with `--span`
or `--require-span` is rejected. A source change between outline and retrieval must
fail the old pin; review the change before adopting a fresh one.

## Interpret the map narrowly

This is a syntactic definition map, not a public API, dependency index, scope resolver
or summary of behaviour. It does not resolve imports or dynamic definitions, evaluate
conditions, call decorators, compile executable target code or run checks. Module-level
statements, imports, lambda assignments, comments preceding decorators, class bases and
other relevant context are not separate map entries. Line-based retrieval can include
other text on the same line. A parsed module with no named definitions legitimately
has an empty map; that does not mean its contents are irrelevant or safe.

Parsing uses the reported Python interpreter grammar (3.10+), not every Python version.
Unsupported syntax/languages fail explicitly. UTF-8 BOM and CRLF are supported; bare
CR is refused to keep numbering consistent with the extractor's LF boundaries.
Parser warnings are suppressed rather than echoing source lines. Definitions are
ordered deterministically for the same bytes and interpreter. Hashes and position IDs
bind navigation to source bytes; they do not authenticate authorship or findings.

## Bounds and budgets

At most 128 explicit selections, 256 KiB per Python source, 8 MiB total reads,
50,000 visited AST nodes per file and 2,048 definitions across the operation. Node
limits apply after native parsing; this is not process isolation or a hard parser
memory limit. The existing trusted/quiescent filesystem assumption still applies.
Unsupported, malformed, unavailable or over-complex inputs return exit 2 without a
partial map. Exit 0 means navigation metadata was produced, not that evidence was
emitted or project checks passed. Exit 1 defers the complete map when its whole JSON
envelope exceeds the byte budget; a tiny control record can exceed a tiny budget.

Snapshot, outline and excerpt each add local I/O, tool calls and metadata. Measure
all of them, plus subsequent context and model calls, against a direct read. An
outline can cost more than a small file; source-byte reductions are not token/billing
savings. No automatic index/cache, source writes, provider calls or host hooks exist.

Parser basis: [Python AST documentation](https://docs.python.org/3.10/library/ast.html),
reviewed 2026-09-20. Parser locations are navigation, not compilation or execution evidence.
