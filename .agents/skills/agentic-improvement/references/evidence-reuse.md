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
