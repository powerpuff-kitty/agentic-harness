# Task Lifecycle

Use persistent execution state for work that spans multiple meaningful steps.

Statuses: proposed -> planned -> active -> blocked -> review -> done; cancelled is terminal.

A task/plan should record:
- goal and non-goals
- assumptions and unresolved questions
- impacted areas
- implementation steps
- validation plan
- dependencies/blockers
- decisions created or changed
- completion evidence

Do not use durable architecture docs as a task tracker. Archive or summarize completed execution plans instead of letting `current.md` grow forever.
