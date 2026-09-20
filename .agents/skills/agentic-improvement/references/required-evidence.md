# Preserve declared evidence while narrowing excerpts

Use this only when a task already has reviewed required source spans. The optional
[extractor](scripts/extract_context.py) can check that a proposed `--span` selection
covers a separately declared `--require-span` set. It does not discover requirements
or decide which rules, qualifiers, contrary evidence, callers or tests matter.

From this skill's root, with the actual reviewed full-file `sha256:` identity:

```sh
python3 scripts/extract_context.py --root /reviewed/project \
  --span src/service.py 20 55 "$SOURCE_SHA256" \
  --require-span src/service.py 20 40 "$SOURCE_SHA256" \
  --budget-bytes 65536
```

Declare required policy and counterevidence spans too when applicable. Keep those
requirements fixed while trimming optional context. Do not remove the flag, change
a pin or weaken a required range merely to obtain success. Resolve genuine scope or
source changes against accepted task criteria before replacing the declaration.
A required path is a constraint on selection, never permission to read an extra file.

The helper compares exact path/hash identities and interval unions before reading
target source. Selecting lines 20-25 and 27-40 cannot satisfy a requirement for 20-40;
the missing line remains a gap. Adjacent ranges may jointly cover a requirement.
Different paths never substitute even when their bytes match. Up to 128 selected
and 128 required requests are supported; an explicitly empty required list is invalid.

Missing coverage or conflicting pins return exit 2 with `required-spans-not-covered`
and no source output. Other malformed/stale inputs keep their existing failure path.
Only after actual source hashes and ranges validate can a successful record contain
`required_evidence`: the normalized declaration digest, file/range/line counts and
`emitted: true`. This digest identifies supplied requirements, not their authenticity,
task scope or completeness. Evidence sufficiency and test success remain unverified.

The whole output budget includes this extra metadata. Exit 1 still defers every
excerpt when over budget; `required_evidence.emitted` is false even when the proposed
selection covered the declaration. Preserve required spans and remove optional
context or explicitly raise the budget. A tiny control response can exceed a tiny
budget. No flag means the previous interface and output bytes are unchanged.

Snapshot freshness, required coverage and source retrieval answer different questions.
An unchanged snapshot does not prove a new selection includes the required evidence.
A structural coverage match cannot bypass stale source pins. Neither result restores
lost model context, approves a Jev batch or verifies a project check. Native checks
and source/criteria review remain separate. No additional provider, discovery or
source write is introduced; use the manual coverage review when execution is unavailable.
