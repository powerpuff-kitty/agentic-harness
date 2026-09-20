# P0: Harness and skills first

Owner direction accepted 2026-09-20: focus on canonical `agentic-harness` and `agentic-harness-agents`. Defer downstream runtime implementation. This plan changes delivery order, not permission boundaries or supported-runtime claims.

## Active work

1. Canonical context-engineering standard and reusable AI pack: source-preserving task context, exact-tool preference, typed semantic decisions, safe handoffs and honest usage accounting. Track under #105 and #114.
2. `agentic-harness-agents` #32: narrow decision-intelligence procedure with a current-agent guidance path and independently optional TypeSafe integration.
3. `agentic-harness-agents` #36: extend agentic-improvement and shared authoring guidance rather than create overlapping optimisation skills. The two guidance skills now have standalone documentation-bundle declarations in the review candidate.
4. `agentic-harness-agents` #26: routing/exclusion cases, grader regressions and paired supplied-record comparisons. Representative independently reviewed host observations remain a distinct unfinished gate. Keep this P0 alongside the procedures.

## Delivery gates

Follow [skills-first acceptance](../docs/testing/skills-first-acceptance.md): usable guidance; portable bytes and preservation; comparable observations; measured outcomes. Publish focused review candidates and run existing catalog/agents validators plus fixture checks. Record exact candidate identities rather than carrying a previous head's green result forward.

Agents PR #37 now includes 27 additional paired-comparison regression methods and a portable-guidance bundle regression. Comparison arithmetic requires matching specification/source/policy/check/host/model/settings identities, preserved required evidence, recorded check references and complete usage. It does not authenticate traces or establish model performance. Canonical guidance remains in PR #120.

Do not claim installed-device updates, automatic host loading, actual Jev inference, measured provider savings or empirical model quality from documentation or fixture validation. Existing compiled-context schema and runtime candidates remain separate work unless explicitly reviewed/delivered. No downstream source pin or implementation change is required for this skills-first slice. Public content must not identify internal consumers.
