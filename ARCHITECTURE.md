# Architecture

This file is the architecture index. Keep it concise and point to deeper documents.

## System overview

Describe the system in one paragraph:

- What the application does.
- Where it runs.
- Its major runtime components.
- Its primary data stores.
- Its important external integrations.

## Architecture principles

1. Prefer explicit boundaries over implicit coupling.
2. Keep domain logic independent from delivery mechanisms where practical.
3. Make side effects observable and testable.
4. Document irreversible or high-cost decisions as ADRs.
5. Prefer boring, well-understood infrastructure unless complexity creates measurable value.
6. Encode architectural constraints in tests/lints where possible.

## Component map

Fill this in for the project:

```text
Client(s)
   ↓
Application/API
   ↓
Domain/services
   ↓
Persistence + external systems
```

## Detailed architecture

- `docs/architecture/frontend.md`
- `docs/architecture/backend.md`
- `docs/architecture/data.md`
- `docs/architecture/integrations.md`
- `docs/architecture/observability.md`

## Decisions

See `docs/decisions/index.md` for architecture decision records.
