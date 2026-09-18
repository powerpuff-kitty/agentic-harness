# Minimal context and useful packs — issue #84

Status: catalog, companion CLI and agent guidance implemented and locally verified. Cross-platform CI and publication remain pending; this plan does not authorize publication.

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

## Implementation sequence and remaining integration

1. Completed: record ADR-009, the canonical selection schema/data, manifest extension, current architecture and companion procedure guidance. Continue CLI work under the existing #38/#39 preservation semantics.
2. Completed locally: explicit minimal/full CLI composition, compatible full default, persisted selection and installed-variant inheritance. Pins reference committed catalog and agents content; source checkouts matched those identities.
3. Completed on macOS x86_64: minimal/full selection, module-triggered additions, repeated composition, both transitions, custom/null routes, custom optional files, modified pack conflicts, injected write failures and legacy-layout refusal. Linux/Windows/macOS arm64 CI remains pending; automatic legacy migration remains unsupported.
4. Actual generated-output measurements are recorded below. Compare materialized-source metrics with actual generated results. Count selected module/skill/adapter files separately. Measure task routing on the filled fixture: form change reads PRODUCT/DESIGN/web-app guidance; boundary change reads ARCHITECTURE; link-input change reads SECURITY plus relevant validation requirements. Report bytes/words, not invented model token counts or improved outcomes.
5. Build #86's runnable synthetic Vue/TypeScript project and seed supported architecture/design violations. Approved check execution and fresh evidence depend on #85 and CLI #55; native host delivery/outcome evidence depends on agents #24–26.

## Validation and rollback

Catalog validation checks the existing variants and the new context fixture. `python3 .github/scripts/measure_context.py` prints deterministic source file/byte/word counts and startup-route size. These measurements exclude CLI-added modules and are not CLI execution tests or model evaluations.

Content-only changes are reversible with a normal reviewed revert. No installed user project is edited. Future composition changes must be previewable and preserve authored files; do not use deletion as rollback.

#84 now has local downstream selection, pin, preservation and legacy-refusal evidence. Cross-platform review and publication remain pending; the GitHub issue is unchanged. #86 still needs runnable application and host/check evidence.

## Catalog slice evidence — 2026-09-18

Catalog validation, architecture registry validation, CLI evidence/compatibility fixtures, public-surface/archive-name regression tests and `git diff --check` passed locally. CLI contract validation used an isolated temporary Python environment with the repository CI's pinned `jsonschema==4.26.0`; no project dependency was added.

Measured source trees: base 27 files / 13,989 UTF-8 bytes; web-app 34 / 16,700; filled reading-list context 13 / 13,577. Router/map/manifest bytes: base 5,410; web-app 5,626; example 3,067. The trees differ in content and installed-module scope; these figures establish a reproducible baseline, not a controlled model-quality comparison or proof of generated-output reduction.

No downstream binary, migration, host/model or runtime application tests ran. No source pins, project installations or public metadata were changed.

## Companion implementation evidence — 2026-09-18

Local branches in all three public repositories are named `feat/minimal-context-selection`:

- Catalog contract/content commit: `dc8902e3fcbaf521ec9ada022bf60f7da094e385`.
- Agent procedure commit: `5fceb09a50222a29ef0c9a52338ba9be9a82e995`.
- CLI implementation/evidence commit: `23fa63e` (see its `docs/context-selection-verification.md`).

The CLI embeds the exact catalog and agent commits above. 144 Rust tests, formatting and Clippy passed. Actual-output validation passed, including 17 context-selection probes. A copied binary outside the checkout and a temporary custom-prefix installation both passed. Twelve generated manifest/lock pairs (all six variants in both modes) passed pinned schemas and exact checksum checks. Agents validation passed with 30 installable skills and 57 adapter/bundle regression tests; this is not executed model routing evidence.

Measured generated base output with default modules/skills: minimal 26 files / 46,606 bytes versus full 39 / 52,869. Web-app: minimal 40 / 78,047 versus full 58 / 86,037. Startup-route bytes: base 3,509 versus 5,516; web-app 3,769 versus 5,653. Selected module contents are complete in both modes. These supersede source-only measurements as evidence of actual composition behavior, without implying improved model outcomes.

No remote publication or issue update occurred. The pinned source commits are local: publish catalog and agents before the dependent CLI branch can build through a fresh remote-only sync. Local testing used clean exact-commit source checkouts fetched from the local repositories. Linux/Windows/macOS arm64 CI, release-artifact validation and native host/model outcomes remain unverified. The independent CLI #55 executor blockers remain open.
