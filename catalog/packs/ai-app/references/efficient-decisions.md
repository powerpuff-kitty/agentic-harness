# Evidence-first typed decisions

This guide describes project-owned decisions, not an SDK implementation. Use existing Decision Kernel contracts from the canonical catalog for machine artifacts; a free-form agent finding is not automatically a validated DecisionReceipt.

## Choose the work, then the mechanism

Exact parsing, lookups, formatting, type checks and executable acceptance criteria belong to code/tools. For a semantic question, identify its finite answer space, needed evidence and abstention behaviour. Open-ended explanations, code generation and broad reviews remain with the appropriate specialist procedure. Review findings may be evidence for a narrower support judgment; that judgment does not replace the original review.

Example: ask whether an architectural statement is supported by the supplied design decision and implementation span. Preserve the two sources separately; record supported, contradicted or insufficient evidence and the missing/contradictory references. Do not interpret unsupported as false or infer global compliance from one example.

## Keep a small decision card

Use an existing project task/configuration record containing the question, criterion, allowed outcomes, source identities, missing evidence, chosen mechanism, fallback and proposed next step. These are review fields, not a second canonical wire schema. A model observation cannot promote itself to accepted policy.

For a current-agent judgment, name that mechanism and leave numerical confidence unknown unless separately measured. Never label a current-agent answer as a Jev response or fabricate probability distributions. Guidance-only means no extra TypeSafe calls; it does not mean local/offline inference or a cost-free coding agent.

## Optional Jev

Before integrating TypeSafe, load its independently installed official `typesafe-ai` skill and read current vendor documentation. Missing skill/docs access is an explicit limitation, not permission to invent endpoints, SDK types, pricing or model availability. Hosted use requires an authorised provider/account, explicit bounded state disclosure and project-approved network/usage limits. Do not fetch credentials as part of guidance, silently enable a provider or switch providers on failure.

As described in TypeSafe's documentation checked on 2026-09-20, a request evaluates one state against independent questions. Keep needed relationships in that state. Choice selects among declared alternatives, Noul addresses a yes/no condition, and Score expresses an ordered dimension. Supply complete criteria and a no-match/insufficient-evidence route where appropriate. Preserve returned uncertainty separately from project calibration and factual correctness.

Grouping useful independent questions may avoid a second request; dependencies that need another answer or new evidence still require another stage. Extra speculative questions consume resources. Do not translate vendor latency examples into a claim of free tokens or guaranteed lower end-to-end cost. A distribution or confidence threshold never authorises deployment, deletion, payments or other consequential actions.

## Evidence and efficiency checks

Compare guidance-only, deterministic and optionally hosted mechanisms on the same versioned tasks and required evidence. Record input/output/tool/auxiliary usage and retries when observed, with unknowns intact. Re-evaluate after source, question, provider or policy changes. Cover missing candidates, contradictory evidence, source drift, unavailable providers, embedded malicious instructions and low-confidence outcomes.

A fixture can validate a rubric; only recorded observations can establish behaviour. Repeated representative runs and preserved task outcomes are needed before recommending automated routing. See the existing Decision Kernel evaluation/calibration contracts rather than inventing universal thresholds.

## Primary references

- [TypeSafe state](https://docs.typesafe.ai/concepts/state): shared state and independent questions.
- [TypeSafe fan-out](https://docs.typesafe.ai/patterns/fan-out): grouping and consuming relevant answers.
- [TypeSafe confidence](https://docs.typesafe.ai/confidence): distributions, uncertainty and domain-specific evaluation.
- [Agent Skills specification](https://agentskills.io/specification): narrow metadata, concise instructions and on-demand references.

References were reviewed on 2026-09-20; availability and API details must be rechecked when implementing an integration. No hosted model was called to author or validate this guide.
