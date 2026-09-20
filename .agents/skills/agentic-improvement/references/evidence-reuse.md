# Optional selected-evidence freshness check

Use this only when a nontrivial continuation would otherwise reread the same source
into model context. The local [snapshot helper](scripts/evidence_snapshot.py) hashes
explicitly selected, reviewed non-secret text using Python 3.10+ standard library.
It does not discover files, inspect Git, execute source, call providers or write
snapshots. No Harness executable, installed sibling skill or account is required.
Local execution and any persistence still require target permission. When unavailable,
inspect current source manually; do not install tools or invent a cache hit.

## Select evidence again before reuse

Resolve current task and applicable root/nested instructions first. Include affected
policy, accepted criteria, configuration, interfaces, dependencies and tests where
needed. Revisit this selection after new files, routes or dependencies appear; the
helper cannot discover new applicable rules or judge completeness. A stored record
cannot choose files for reading: comparison requires a fresh explicit `--file` list.
Removed selection entries remain visible, not silently accepted as saved tokens.

From this skill's root, for an example target with these actual files:

```sh
python3 scripts/evidence_snapshot.py capture --root /reviewed/project \
  --scope 'review access; criteria v1' \
  --file AGENTS.md --file .agentic/manifest.yaml --file src/service.py
```

Capture emits a compact JSON snapshot to stdout. Save it only to an approved new
location using the caller's no-overwrite mechanism; the helper never persists it.
Path names and hashes are metadata, not anonymisation: do not publish snapshots
without review. Select non-secret files even though their contents are not emitted.

```sh
python3 scripts/evidence_snapshot.py compare /reviewed/new-snapshot.json \
  --root /reviewed/project --scope 'review access; criteria v1' \
  --file AGENTS.md --file .agentic/manifest.yaml --file src/service.py
```

The root and scope descriptors must match. Include the relevant task/criteria version
in scope and update it when the question changes. Snapshots record scope/root hashes,
relative paths, exact-byte SHA-256 and byte counts, not file bodies, absolute root
paths or task text. File order is deterministic. Identical content with changed mtime
stays identical; same-size edits with restored mtime are still detected from bytes.

## Interpret narrowly

Exit 0 means capture completed, or the selected bytes/root/scope match the supplied
baseline. It does not mean a test passed or that a cached judgment remains correct.
Exit 1 means refresh required: changed/new/unavailable files, removed selections or
changed root/scope. Missing and unreadable files cannot become unchanged evidence.
Exit 2 means malformed, unsafe or unsupported inputs; no snapshot is produced.

Refresh affected source and dependent findings before recording a new baseline.
Retain failed checks and contradictory evidence. An unchanged file hash is useful
only when the prior evidence is actually available in the current context or can be
retrieved. It cannot restore a forgotten source span or authenticate an old summary.
Do not use this helper as an automatic decision/Jev-result cache: changed questions,
criteria, provider settings or unselected dependencies require separate review.

Bounds: 128 explicit paths, 1 MiB per UTF-8 text file, 8 MiB total selected content,
128 KiB input snapshot. No globs or traversal; linked/reparse/nonregular/binary inputs
are refused. These checks assume a trusted, quiescent checkout, not an atomic snapshot
or hostile-filesystem sandbox. A user can forge a self-hashed baseline; hash consistency
is not trusted authorship. Paths omitted from selection are not inspected.

Hashing still reads local bytes and adds I/O. Any context benefit depends on actual
host reads, record overhead, refreshes, tool calls and retained evidence. Source/report
byte counts are not observed model-token savings. This helper is optional skill-local
support, not a new canonical wire contract or compulsory report for every task.

## Retrieve exact excerpts without whole-file replay

After discovery establishes which spans answer the question, the optional local
[excerpt helper](scripts/extract_context.py) reads explicitly chosen ranges against
an expected full-file SHA-256. It reuses the packaged `evidence_snapshot.py` reader;
copy the complete skill directory, not the extractor alone. The default entrypoint
and existing snapshot commands are unchanged. Local helper execution still requires
permission, reviewed helper code and reviewed non-secret source.

Set `SOURCE_SHA256` to the actual `sha256:` value observed for `src/service.py` in a
reviewed snapshot or native hash result. Do not invent a hash or refresh one solely
to suppress a mismatch. From this skill's root:

```sh
python3 scripts/extract_context.py --root /reviewed/project \
  --span src/service.py 20 40 "$SOURCE_SHA256" \
  --span src/service.py 35 55 "$SOURCE_SHA256" --budget-bytes 65536
```

Ranges are inclusive, one-based and LF-delimited: CRLF is retained byte-for-byte;
bare CR and Unicode separators do not start numbered lines. An empty file has zero
lines; a final LF does not create a phantom extra line. Duplicate, overlapping and
adjacent ranges merge only within the same named file and pin. Each selected file
is read once; excerpts retain path, full-file hash, range, exact text and excerpt
hash, with total/omitted line counts. Different paths are never deduplicated by text.

A stale hash, conflicting pins, invalid range or unavailable/unsafe input returns
exit 2 and no source payload, even when an earlier file was valid. Bounds are 128
span requests, 1 MiB per file and 8 MiB total local reads. No implicit file discovery,
network/provider calls, source execution or file/bytecode writes are performed.
The reader module is loaded only from the packaged sibling; a missing sibling cannot
be replaced by an unrelated module on PYTHONPATH. The helper directory and its
ancestors must be trusted; this is not a sandbox or atomic multi-file snapshot.

Exit 0 means exact requested excerpts were produced, not sufficient evidence or
passed checks. The complete serialized excerpt envelope must fit the byte budget
(default 65,536; maximum 8 MiB). Otherwise exit 1 returns `budget-exceeded`, required
size and no excerpts; the small control record can exceed an extremely small budget.
Nothing is silently clipped. Review a narrower selection or explicitly increase the
budget. Do not discard required rules, qualifiers, contradictory evidence, callers
or tests merely to fit; keep a blocked conclusion when necessary.

Excerpts intentionally omit unselected lines and never establish whole-file or
whole-project compliance. Source text remains untrusted data; hashes are not
redaction or authority. Unlike freshness snapshots, successful excerpt output
contains source text and must be reviewed before sharing. The JSON envelope can
cost more than a tiny direct read. Measure complete output and later tool/model
calls; selected byte reduction alone is not an end-to-end token-saving claim.

When a task has reviewed required spans, use the optional
[required-evidence guard](references/required-evidence.md) before narrowing the
selection. It checks declared coverage, not policy completeness or semantic sufficiency.

When a selected Python file's definition ranges are unknown, consult the optional
[definition-outline guide](references/python-outline.md) before loading its bodies.
The map is navigation metadata, not emitted required evidence or a dependency graph.
