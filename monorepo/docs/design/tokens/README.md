# Tokens

Prefer three layers:

1. Primitive: raw scales (`neutral.900`, `space.4`, `radius.2`).
2. Semantic: purpose (`color.text.primary`, `color.surface`, `space.section`).
3. Component: scoped aliases (`button.primary.background`).

Components and layouts should consume semantic/component tokens rather than introducing raw values without a reason.
