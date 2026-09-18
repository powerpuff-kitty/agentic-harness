# Minimal context and useful packs — issue #84

Status: catalog content and context-selection v1 contract implemented; companion CLI implementation and verification in progress. Publication is not authorized by this plan.

## Outcome and current slice

Reduce unnecessary generated context while retaining inspectable materialized variants and preserving authored truth. The web-app, security-critical and library-sdk packs now include decisions, examples, anti-patterns and evidence checklists. The filled synthetic reading-list fixture demonstrates context with explicit unknowns; it is not a runnable #86 integration project.

## Selection contract

ADR-009 and [context selection v1](../../docs/project/context-selection-v1.md) define the accepted additive contract. Full remains the default; organization profiles (`startup`, `enterprise`, etc.) retain their existing meanings. Compatible CLI versions expose `--context-profile`; verify installed support before use.

The minimal baseline has a budget of **12 materialized files before selected modules, skills, host adapters and project-specific additions**:

- Root README.md and AGENTS.md.
- `.agentic/README.md`, manifest.yaml, lock.json, PRODUCT.md, ARCHITECTURE.md, SECURITY.md and THIRD_PARTY_NOTICES.md.
- `.agentic/decisions/README.md`, index.yaml and ADR-000-template.md.

Retain core paths, licensing notices and decision lifecycle. For visual projects, add DESIGN.md. Add installed pack/policy/skill files and their necessary routers according to explicit selection. Add host adapters according to host selection. Create reference, supporting docs, plan, task and evaluation files when useful content or a selected module requires them; set omitted optional manifest paths to null and generate an accurate context map. Full materialized source variants remain directly inspectable.

The baseline budget is a design target, not an installed-project maximum or a current CLI guarantee. Never remove a project-authored file to meet it. On upgrade, preserve existing optional files even when minimal mode would omit them for a fresh project. Conflicting customizations must be reported, not silently overwritten. A changed profile does not authorize pruning.

## Independent evidence states

Keep structure installed, project configured, checks configured and behavior verified separate. Placeholder truth remains unresolved. The example has authored scenario context, unresolved source pins, no configured checks and no verified behavior. Its deliberate unknowns are useful input, not failed attempts to invent project decisions.

## Remaining implementation sequence

1. Completed: record ADR-009, the canonical selection schema/data, manifest extension, current architecture and companion procedure guidance. Continue CLI work under the existing #38/#39 preservation semantics.
2. Implement explicit minimal/full composition in the CLI while retaining existing defaults. Update exact catalog/agents pins only to reviewed commits containing the required content; local uncommitted content cannot be a source pin.
3. Run installed-binary tests for minimal/full selection, module-triggered additions, repeated composition, transition between modes, custom optional files, modified pack conflicts and preservation on failure. Include current-layout upgrade and legacy-layout refusal/manual migration behavior.
4. Compare materialized-source metrics with actual generated results. Count selected module/skill/adapter files separately. Measure task routing on the filled fixture: form change reads PRODUCT/DESIGN/web-app guidance; boundary change reads ARCHITECTURE; link-input change reads SECURITY plus relevant validation requirements. Report bytes/words, not invented model token counts or improved outcomes.
5. Build #86's runnable synthetic Vue/TypeScript project and seed supported architecture/design violations. Approved check execution and fresh evidence depend on #85 and CLI #55; native host delivery/outcome evidence depends on agents #24–26.

## Validation and rollback

Catalog validation checks the existing variants and the new context fixture. `python3 .github/scripts/measure_context.py` prints deterministic source file/byte/word counts and startup-route size. These measurements exclude CLI-added modules and are not CLI execution tests or model evaluations.

Content-only changes are reversible with a normal reviewed revert. No installed user project is edited. Future composition changes must be previewable and preserve authored files; do not use deletion as rollback.

Completion of #84 still requires downstream selection, pin, preservation and migration evidence. #86 additionally needs runnable application and host/check evidence. Neither issue is complete from this catalog slice.

## Catalog slice evidence — 2026-09-18

Catalog validation, architecture registry validation, CLI evidence/compatibility fixtures, public-surface/archive-name regression tests and `git diff --check` passed locally. CLI contract validation used an isolated temporary Python environment with the repository CI's pinned `jsonschema==4.26.0`; no project dependency was added.

Measured source trees: base 27 files / 13,989 UTF-8 bytes; web-app 34 / 16,700; filled reading-list context 13 / 13,577. Router/map/manifest bytes: base 5,410; web-app 5,626; example 3,067. The trees differ in content and installed-module scope; these figures establish a reproducible baseline, not a controlled model-quality comparison or proof of generated-output reduction.

No downstream binary, migration, host/model or runtime application tests ran. No source pins, project installations or public metadata were changed.
