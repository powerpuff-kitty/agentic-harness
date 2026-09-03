# Boilerplate Catalog Model

`agentic-harness` is the catalog itself: boilerplates are first-class root directories rather than children of another wrapper folder.

```text
base/
web-app/
backend-api/
saas/
monorepo/
library-sdk/
```

Each entry contains `boilerplate.json` metadata and the canonical project shape for that starting point. Shared reusable layers live under `modules/`; presets select a root boilerplate plus modules and skills.

This layout is intentionally optimized for GitHub browsing and agent retrieval: a visitor can see the available project starting points without first learning internal package structure.

Complete reference applications, showcases, generated examples, runtime code, and agent prompts are outside the scope of this repository.
