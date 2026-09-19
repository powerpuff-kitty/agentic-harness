# ai-app

Use for products containing LLMs, RAG, agents, classifiers, embeddings, or model-driven workflows. This pack is design guidance; selecting it does not configure a model, enable hosted inference or enforce a runtime policy.

## Project decisions

Document model responsibilities, prompt/instruction boundaries, retrieval sources, tool permissions, structured outputs, eval datasets, failure modes, grounding/citations, privacy, cost/latency budgets, fallbacks, and human approval points. Keep those decisions in the project's existing accepted truth/configuration, not in provider prompts alone.

Choose separately: what code can determine exactly; what needs a bounded semantic judgment; what needs open-ended generation; and which actions require independent authorisation. A model output must never grant itself permissions or turn uncertain evidence into a passed check.

## Context and token efficiency

Supply the smallest sufficient task-specific evidence set. Preserve required rules, acceptance checks and contradictory evidence. Reuse source-grounded observations only while their source/configuration/scope identities remain current. Prefer focused source spans, existing interfaces and native diagnostic summaries to whole-repository or transcript dumps. References are useful only when the consuming host can retrieve them.

Measure input, output, tool results, retries and auxiliary provider calls separately. Unknown usage is unknown; an estimator is not billing data. A smaller prompt is not proof of improved outcomes. Do not claim a fixed saving percentage, infer semantic equivalence from similar instructions, or assume JSON is always more compact.

## Typed decision design

A provider-neutral decision procedure can run as guidance with the current coding agent. Jev is an optional hosted implementation for finite semantic judgments, not an automatic replacement for every LLM call. Keep its official integration skill independently updatable. Use [the decision and efficiency guide](references/efficient-decisions.md) only when designing such decisions.

Do not treat model behaviour as deterministic. Evaluate representative and adversarial cases, preserve abstention and failures, and distinguish instruction/fixture validation from actual host/model observations. Installing a skill does not demonstrate host discovery or compliance.
