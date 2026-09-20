# Optional JavaScript / TypeScript navigation

Use this when selected JS/TS files are large and relevant definition locations are
unknown. Prefer an available native language-server symbol query or a direct read
for known locations. This is an optional alternative, not an extra required step.

The [helper](scripts/outline_typescript.py) requires Python 3.10+, its reviewed
[sibling reader](scripts/evidence_snapshot.py), an explicitly selected absolute Node
executable and an already-installed TypeScript CommonJS compiler entry. Review the
runtime/parser and permission to execute them first. It never installs packages,
invokes npm/npx, builds a project or starts a provider. Missing tools mean manual
source inspection, not an automatic installation or a false empty map.

## Pin the source and the parser

Set the variables below to actual reviewed paths and observed `sha256:` identities,
not guessed hashes. Parser and helper directories must be trusted and quiescent.
Pass the physical parser entry path; linked parser paths are refused. From this
skill's root:

```sh
python3 scripts/outline_typescript.py --root /reviewed/project \
  --file src/service.ts "$SOURCE_SHA256" \
  --node "$NODE_EXECUTABLE" \
  --typescript "$TYPESCRIPT_ENTRY" "$PARSER_SHA256" --budget-bytes 65536
```

Repeat `--file PATH SHA256` for other explicitly selected files. Supported extensions:
`.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`. Vue `.vue` files are
explicitly unsupported: do not pretend script-only parsing inspected an SFC. They
need a verified SFC parser or native host navigation. No regex-based substitute is used.

The helper passes hash-verified UTF-8 source on stdin to a fixed Node adapter using
`createSourceFile`, not a compiler Program. It does not read tsconfig, follow imports,
resolve dependencies, run decorators or evaluate target modules. The parser itself
IS executed as trusted local code, with ordinary process privileges. Its entry hash
is not authorship authentication or verification of its whole installation. Ambient
Node preload options, module paths and provider credentials are not forwarded; this
is not a filesystem/network sandbox. Node and Python startup still need a trusted host.

## Navigate, then read evidence

Returned definitions include named functions/classes, interfaces/types/enums,
identifier namespaces, methods/accessors/constructors and identifier bindings whose
initializers are functions/classes. Overloads and repeated names retain distinct
file-local UTF-16 offset IDs. Enclosing named declaration IDs are syntactic navigation,
not resolved language scopes. Anonymous enclosing scopes are marked in qualified
names and have no fabricated named parent. Names may be sensitive; this is not redaction.

Bodies, default values, docstrings and parser diagnostic snippets are omitted.
Computed/string-named declarations, ordinary data bindings, dynamic exports,
imports and module-level behavior still require separate inspection. An empty map
is not an empty or safe module. Parser success is not type checking or valid runtime code.

Inclusive `start_line` / `end_line` use LF boundaries compatible with the existing
[excerpt helper](scripts/extract_context.py), including CRLF, BOM and JavaScript's
Unicode line separators. Same-line statements can share a returned range. Single
callable-variable statements include their const/export prefix. Request these ranges
with the same source hash in a separate `--span` operation, and preserve independent
requirements using the [required-evidence guide](references/required-evidence.md).
An outline never counts as emitted required evidence. Source drift requires review,
not merely replacing a pin to silence a mismatch.

## Limits and interpretation

At most 32 requests, 256 KiB per source, 2 MiB total source, 16 MiB parser entry,
50,000 visited AST nodes per file and 2,048 returned definitions overall. Node has
a 15-second timeout and a 128 MiB V8 old-heap limit, not a total-process sandbox.
The fixed adapter bounds returned metadata to 2 MiB; subprocess output is also
checked after capture, not securely bounded against a malicious executable. The
whole final JSON envelope must fit the requested budget (default 64 KiB, max 2 MiB).
Exit 1 defers the entire map, never clips it; a small control record can exceed an
extremely small budget. Exit 2 rejects invalid/stale/unavailable inputs with no partial
map or raw diagnostics. Exit 0 is navigation only, not evidence sufficiency or a pass.

The parser version and entry identity are reported. TypeScript 5/6 compiler-API
shapes are accepted; local integration was exercised with TypeScript 5.8.3 and
Node 22.16.0, not every supported host/version. TypeScript 7's different API is not
supported. Real-parser tests explicitly skip when no reviewed installed parser is
available; parser-independent tests still run. No network install occurs in either path.

The parser is read and loaded in addition to the selected source, and mapping adds
calls and metadata. Measure the entire navigation + retrieval workflow, including
requests, guide loading, retries and downstream model calls. Small files may cost
more than a direct read. Byte counts do not establish model-token or billing savings.

Parser basis: [TypeScript compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API),
reviewed 2026-09-20. This guide delegates language grammar to the selected compiler,
not to a handwritten JavaScript parser.
