# Boilerplates

Boilerplates are human-readable recipes that combine canonical templates with common packs, profiles, policies, and agent skills.

Current machine-readable compositions in `../presets/` include:

- `vue-saas` — SaaS-oriented Vue composition.
- `api-postgres` — backend API with PostgreSQL knowledge.
- `secure-saas` — SaaS composition with stronger security posture.

A boilerplate should document:

1. intended product shape;
2. base template;
3. recommended packs and policies;
4. recommended agent skills from `agentic-harness-agents`;
5. expected deployment/data assumptions;
6. what is intentionally not included.

Do not duplicate full template files here. Keep template truth in `templates/` and use boilerplates as understandable compositions.
