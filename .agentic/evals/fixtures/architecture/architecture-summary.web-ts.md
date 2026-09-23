# Architecture Summary — fixture.web-ts

- Graph state: `observed`
- Nodes: 8
- Edges: 8

## Capabilities

- `capability.catalog` — Catalog — `packages/catalog`
  - Depends on: none
  - Contracts: `contract.catalog`
  - Surfaces: `surface.catalog-ui`
- `capability.search` — Search — `packages/search`
  - Depends on: `capability.catalog`
  - Contracts: none
  - Surfaces: `surface.search-ui`

## Constraints

- `boundary.web-no-catalog-adapter` — forbidden-dependency — declared — `app.web` → `adapter.catalog-api`

## Coverage

- Declared nodes: 8
- Declared edges: 8
- Checked paths: 0
- Complete: false

## Not checked

- Repository paths are declared fixture data and were not inspected against a checkout.
