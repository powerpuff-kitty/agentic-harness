# web-app

Use for browser-based applications.

## Decisions to record

Keep accepted choices in the project's canonical context. Mark unresolved choices with their impact and the evidence needed to decide; installing this pack does not decide them.

| Decision | Record in | Concrete questions |
| --- | --- | --- |
| Critical journeys and recovery | PRODUCT.md | What must the user finish? What happens after validation, network or permission failure? |
| Routing and state ownership | ARCHITECTURE.md | Which state belongs in the URL, a view, a shared store or the server? Who invalidates cached data? |
| Data access and mutations | ARCHITECTURE.md | Which service owns requests, cancellation, retries and duplicate-submit protection? |
| Tokens and controls | DESIGN.md | Which token/component sources are canonical? Which states and exceptions are approved? |
| Browser, accessibility and performance targets | PRODUCT.md and relevant supporting docs | Which environments and journeys are supported, and how will they be measured? |
| Sensitive browser data | SECURITY.md | What can reach storage, rendered HTML, logs and third-party scripts? |

## Example and anti-patterns

For a synthetic reading-list application, a view owns an unsaved title input; a service owns list mutations; the domain owns title validation. The filter belongs in the URL only if sharing/bookmarking the filtered list is a product requirement. A failed save preserves input and offers an explicit retry. These are project-selected choices, not universal framework rules.

Avoid duplicating remote records in unrelated stores, scattering fetch/error handling across controls, accepting inaccessible custom controls without justification, or copying raw visual values around an approved token system. Do not add retries to non-idempotent writes without defining duplicate behavior.

## Task-scoped evidence

- For a form change, inspect its journey, validation rules and shared control contract; test invalid input, pending, failure, retry and success.
- For data/state changes, test cancellation, stale responses, cache invalidation and duplicate submission where applicable.
- For a user-facing change, check keyboard operation, focus, accessible names and the supported viewport range. Automated scans alone do not establish complete accessibility.
- Measure the relevant performance target in a named environment; retain unsupported browsers, missing tools and unmeasured paths as gaps.

Completion reports identify the changed journey, checks actually run and their results, remaining unsupported states, and any approved exception. A generated component inventory or a written budget is not runtime verification.
