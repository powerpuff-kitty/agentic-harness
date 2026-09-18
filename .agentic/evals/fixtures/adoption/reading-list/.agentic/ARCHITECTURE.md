# Architecture

Vue 3 and TypeScript implement a single memory-only reading list, built with Vite. No router, state-management package or backend is needed. `src/main.ts` is the composition root.

| Boundary | Responsibility | Dependencies |
| --- | --- | --- |
| `src/domain/` | Entry types, input validation, immutable read transitions | Standard JavaScript including the URL API; no Vue or outer layers |
| `src/application/services/` | Session API: list, add, toggle and ID allocation | Domain only |
| `src/presentation/views/` | Form, filter, focus recovery and rendering | Application service, domain types, shared controls |
| `src/presentation/components/` | Reusable named controls with props/events | Vue and semantic CSS tokens; no service state |
| `src/presentation/styles/tokens.css` | Semantic tokens and shared layout | No application dependencies |

The runnable fixture refines the context-only example's proposed paths into explicit `application` and `presentation` layers because these are supported by the current deterministic analyzer. This is a scenario choice, not a required layout for Vue projects. `.agentic/architecture.json` explicitly selects layered dependency direction and dependency hygiene.

The service validates before mutation; invalid input preserves both form values and service state. Each service instance owns its entries. Snapshots are copied so external consumers cannot mutate its state. Views keep filter state locally. The domain counts title length in JavaScript UTF-16 code units and validates HTTP(S) links without fetching them.

## Enforcement boundaries

The CLI checks supported local imports, runtime cycles and named-layer direction. The seeded domain-to-presentation import must produce `layered.domain-independent` with source/target evidence. Computed imports must report incomplete coverage; the compatible CLI fix is identified in `../VERIFICATION.md`.

The selected layered profile cannot independently enforce the narrower component-to-service restriction, domain imports of external Vue, or semantic business-logic placement. Those remain code-review obligations. Design checks are static evidence, not behavioral/accessibility proof. Exceptions are applied only in disposable negative-test copies; baseline configuration has none.

Node/TypeScript unit tests validate the session API; browser tests exercise the built application. No remote API exists. Unexpected browser/runtime failure has no recovery mechanism beyond reload, which clears state. Deployment and performance budgets remain unresolved.
