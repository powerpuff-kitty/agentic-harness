# Product

## Purpose and scope

A single reader records titles and optional links during one browser session, marks entries read and filters all/unread entries. The list is memory-only; reloading clears it. Explain that limitation beside the list before the user adds an entry.

Accounts, shared lists, synchronization, analytics, recommendations, imports and persistent storage are out of scope. This synthetic scenario has a runnable local application; it is not a deployed product.

## Journeys and acceptance

- Add a trimmed title of 1–120 characters and an optional absolute HTTP(S) URL. Reject other schemes, malformed URLs and empty/overlong titles without losing input. Duplicates are allowed; each entry has a separate session-local ID.
- Successful add clears the form, leaves focus at the title input and exposes the new entry in the all filter. A new unread entry is also visible under the unread filter.
- Toggle read status without changing other entries. When an entry disappears from the unread filter, move focus to the next remaining entry's toggle, or to the filter control when none remains.
- Distinguish a new empty list from a filter with no results. Both explain the relevant next action.

## Targets and open decisions

Critical journeys must be usable by keyboard and at 320 CSS pixels without horizontal page scrolling. WCAG 2.2 AA is the intended accessibility target, not a verified compliance claim.

The measured browser version is recorded in `../VERIFICATION.md`; this is test coverage, not a multi-browser support promise. Numerical performance budgets and broader browser support remain unresolved. Persistence requires a new product/security decision rather than silently adding local storage.
