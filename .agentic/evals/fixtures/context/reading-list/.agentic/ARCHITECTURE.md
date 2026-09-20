# Architecture

## Implementation target

Vue and TypeScript are selected for this synthetic scenario. No application source or dependencies exist in this fixture; paths below define intended ownership for the future implementation.

| Boundary | Responsibility | Allowed dependencies |
| --- | --- | --- |
| `src/domain/` | Entry types, title/URL validation, immutable read-status transitions | No Vue, browser APIs, services or views |
| `src/services/` | Session-local list state and ID allocation | Domain |
| `src/views/` | Form input, filter state, focus recovery and rendering | Services, domain types, shared controls |
| `src/components/` | Reusable controls with explicit props/events | Design tokens; no service state |
| `src/styles/tokens.css` | Canonical visual values once implemented | No application dependencies |

Input flows from the view to domain validation, then through the service to session state and back to rendering. Validation failure leaves service state unchanged. The filter is view-local because shareable filtered links are out of scope. No router or shared state library is required for this one-screen scenario.

## Invariants and evidence gaps

These boundaries are project choices, not universal Vue conventions. Domain-to-view imports and component-to-service imports violate this scenario. There are no source paths to analyze yet; boundary tests and deterministic architecture configuration must be added with source.

No network requests, persistence or server execution are intended. Adding any requires revisiting PRODUCT.md and SECURITY.md. Dependency/runtime pins, build configuration, unexpected-runtime-failure recovery and deployment remain unconfigured. No passing build, architecture or runtime evidence is claimed.
