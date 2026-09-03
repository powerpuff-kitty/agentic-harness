# Evals

Use this directory for repeatable checks of agent behavior and generated artifacts.

## What belongs here

- Regression prompts for previously observed agent failures.
- Golden/accepted outputs when exact or structural comparison is useful.
- Rubrics for qualities that cannot be captured by unit tests alone.
- Scripts that convert subjective rules into deterministic checks where possible.

## Rule of thumb

If a correction has been made repeatedly, do not rely on repeatedly telling the agent. Prefer, in order:

1. deterministic enforcement in code/test/lint/schema;
2. a clear source-of-truth rule;
3. a reusable skill procedure;
4. an accepted exemplar;
5. an eval that catches the regression.

Document each eval's purpose, input, expected behavior, and failure interpretation.
