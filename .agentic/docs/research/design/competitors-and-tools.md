# Competitors and design-context tools

Reviewed 2026-09-08. Re-verify current pricing, feature flags, terms, and API/MCP behavior before implementing integrations.

## UI Rules

Source: https://uirules.com/

Category: design-system-as-context for AI tools.

Observed strengths:
- structured styles/tokens, rules, component vocabulary, and project overrides;
- rule importance/severity concepts and task-relevant context retrieval;
- MCP/tool delivery and design-system history/versioning;
- imports from existing sources such as CSS/Figma-style data where supported.

Relevance to Harness:
- validates task-scoped design context as a useful product category;
- Harness should remain repository-native, provider-neutral, and able to compile deterministic context without a cloud account;
- Harness should go earlier (analyze/generate identity) and later (verify drift/compliance) than design-context delivery alone.

## DESIGN.md ecosystem

Reviewed sources include:
- https://designmd.me/
- https://designmd.supply/
- https://design-md.hyperbrowser.ai/
- https://getdesign.md/
- https://www.typeui.sh/
- https://open-design.ai/
- https://www.aura.build/
- https://neuform.ai/
- https://styles.refero.design/

Category: website/design extraction, reusable design descriptions, design-system authoring, references, and AI delivery.

Relevance to Harness:
- support import/interchange rather than treating one DESIGN.md dialect as project truth;
- preserve source/provenance and conflict-review before adoption;
- distinguish imported evidence, approved identity, and implementation bindings;
- use external design documents as optional inputs to a canonical Design Genome.

## Appllama

Source: https://appllama.io/
MCP: https://appllama.io/mcp
Terms: https://appllama.io/terms

Category: current mobile product-design reference library with screen/flow research and optional MCP access.

Relevance to Harness:
- flow-level research is more valuable than isolated screenshot inspiration;
- commercial provider access should use the user's authorization and remain optional;
- do not bulk mirror, cache, train on, or benchmark against provider data when terms prohibit it;
- retain project-specific derived decisions, not a copy of a provider's proprietary corpus.

## Section/pattern galleries

Reviewed examples:
- https://www.navbar.gallery/
- https://supahero.io/
- https://404s.design/
- https://www.footer.design/
- https://www.cta.gallery/
- https://www.unsection.com/
- https://60fps.design/
- https://designspells.com/
- https://bentogrids.com/

Category: section, interaction, and visual-pattern inspiration.

Relevance to Harness:
- classify references by purpose and transferable principle rather than copying layouts;
- research evidence should record what is useful, when it applies, and what must not be copied;
- product requirements must not be inferred merely because a reference contains a feature.

## Competitive conclusion

The opportunity is not another theme generator or screenshot gallery. The differentiated loop is:

`analyze -> preserve -> compile -> implement -> verify`, with later `research -> create` capabilities feeding the same canonical identity contract.
