# Testing Strategy

Agents should infer the project's existing test stack and preserve it.

Map changes to validation:
- pure logic -> unit tests
- DB/repository/API integration -> integration tests
- public API contracts/events -> contract/schema tests
- critical user journeys -> end-to-end tests
- UI accessibility -> automated accessibility plus manual checks where needed
- design fidelity -> visual regression or accepted exemplars
- migrations -> forward/backward or rollback validation when supported
- security-sensitive changes -> negative/adversarial cases

Do not add every test type to every project. Add the minimum layers that cover meaningful failure modes.
