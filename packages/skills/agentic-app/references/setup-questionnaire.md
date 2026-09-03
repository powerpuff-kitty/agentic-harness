# Guided Setup Questionnaire

The agent must inspect the repository before asking questions. Never ask for facts that can be read from manifests, source code, CI, infrastructure files, or existing documentation.

## Interaction model

1. Inspect and summarize what was detected.
2. Classify each setup fact as detected, inferred-with-confidence, or unresolved.
3. Ask only unresolved high-impact questions.
4. Recommend packs and permissions.
5. Show a proposed configuration before writing files.
6. Continue only after user approval when the setup changes repository policy or permissions.

## Minimum questions

Ask these only when unresolved:

- Project purpose/type: web app, SaaS, backend/API, mobile, AI, realtime, data, SDK/library, other.
- Maturity: prototype, startup, production, critical.
- Priorities: speed, design fidelity, security, reliability, agent autonomy, compliance.
- Agent autonomy: conservative, balanced, autonomous.
- Which actions require approval: dependencies, DB schema, auth, infrastructure, production config.
- Authoritative external sources: Figma, product specs, API specs, screenshots, architecture docs, issue tracker.

## Prompt format

Prefer one compact questionnaire rather than serial questioning. Present detected facts first, then only missing decisions.

## Non-interactive mode

When explicitly requested, infer low-risk defaults, never infer high-impact permissions, and return unresolved questions at the end. Do not block read-only AUDIT mode on setup questions.
