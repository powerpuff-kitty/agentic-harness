# Pack Resolution

Packs are composable knowledge modules. A pack says what an agent needs to know for a project category. Skills say how to perform repeatable tasks.

## Resolution rules

- Always include core repository guidance.
- Recommend packs from detected stack and user-selected product type.
- Prefer the smallest sufficient pack set.
- Packs may add documentation requirements, skills, examples, evals, and approval gates.
- A project may use multiple packs.
- Never let a pack overwrite project-specific truth.

## Common mapping

- browser UI -> `web-app`
- strong visual/product-design requirement -> `design-system`
- HTTP/RPC backend -> `backend-api`
- multi-tenant billing product -> `saas`
- native/hybrid client -> `mobile`
- model/RAG/agent behavior -> `ai-app`
- analytics/pipelines/warehouse -> `data-platform`
- websockets/WebRTC/presence -> `realtime`
- high-assurance/security-sensitive -> `security-critical`
- package/SDK/public library -> `library-sdk`
- PostgreSQL -> `postgres`

The resolved set belongs in `agentic.yaml`.
