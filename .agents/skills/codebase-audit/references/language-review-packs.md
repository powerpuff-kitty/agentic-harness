# Language review packs

Use this guide only after loading the target project's accepted architecture and determining the languages actually present. These checks refine a broad codebase audit; they do not override project rules and do not claim deterministic evidence unless the installed analyzer reports the required capability.

## JavaScript / TypeScript
- Inspect package/workspace boundaries, public exports, runtime vs type-only imports, dynamic imports, supported aliases and framework client/server boundaries.
- Keep Vite/build-tool configuration separate from application architecture.
- Treat unresolved aliases/export conditions as coverage gaps when resolver support is partial.
- Prefer official TypeScript, Node.js and selected framework documentation for changing semantics.

## Python
- Inspect package/module roots, relative imports, `pyproject.toml` layout, package ownership and cycles.
- Distinguish import-time side effects from ordinary dependency direction.
- Do not execute imports to discover topology; namespace packages/editable installs/tool-specific source layouts can change resolution.
- Prefer Python import-system and PyPA specifications plus selected framework documentation.

## Rust
- Inspect Cargo workspace/package/crate boundaries, modules, public APIs, feature/target-specific dependencies and unsafe/FFI boundaries when relevant.
- Do not confuse `use` relationships with crate dependency declarations.
- Do not execute proc macros or build scripts during static analysis.
- Prefer the Rust Reference, Cargo reference and project-selected framework documentation.

## Go
- Inspect `go.mod`/`go.work`, package ownership, imports, cycles, `internal` boundaries, build constraints and generated files.
- Do not impose a generic folder architecture such as `cmd/` or `pkg/` unless project policy selects it.
- Prefer the Go specification and official modules/workspaces documentation.

## Evidence requirements
For language-specific findings record: authority scope (universal/language/framework/project), evidence source, analyzer capability/coverage, counterevidence, and not-checked behavior. `partial` analyzer support is partial evidence; `unsupported` is `not_checked`, never a pass.