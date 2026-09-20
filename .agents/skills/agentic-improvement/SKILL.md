---
name: agentic-improvement
description: "Improve an existing repository's agent instructions, context routing and skill design. Use when the user asks to reduce token use, repeated reads, duplicated guidance or verbose handoffs while preserving evidence and completion checks. Do not use for the initial readiness audit, ordinary code refactoring, typed semantic judgments or model-fit comparisons."
---
# Agentic Improvement

## Objective

Make scoped agent workflows clearer and more efficient without weakening accepted project rules, required evidence or verification.

## Inputs

Required: target repository and requested improvement. Optional: existing readiness findings, representative task transcripts or usage observations that the user has authorised, target profile and edit permission. A CLI report is useful when available, never a prerequisite.

## Context

Read the compact project router, applicable mandatory rules and files implicated by the task/findings. Expand only for a concrete unresolved question. Use [the efficiency guide](references/efficiency.md) for a substantial context-optimisation task. It remains available when this skill is copied alone; no collection-wide reference or executable is required.

## Procedure

1. Establish a baseline from existing evidence. Without a measured readiness/usage report, describe observed instruction and routing problems qualitatively; keep scores, costs and token savings unknown.
2. Map required evidence separately from optional background. Preserve relevant policy, source qualifiers, contradictions and acceptance checks. Record missing required sources as blockers for the affected claim, not as token savings.
3. Correct stale routes and narrow triggers before adding skills. Deduplicate presentation only after matching authority, applicability and exceptions; identical text in different folders can have different scope. Preserve canonical sources and provenance. Reconcile conflicts explicitly; deleting or relocating a rule is a separate reviewed change.
4. Replace blanket reads with task-to-source routes. Reuse unchanged evidence by source/configuration/scope identity, but refresh changed working-tree content and retrieve references the host cannot resolve. Keep code interfaces, callers and affected tests when needed for correctness.
5. Prefer native checks to model reasoning for exact questions. Summarise tool results with scope, exit status, relevant failures and actual retrievable evidence; preserve truncation and unavailable checks. Use compact resumable handoffs rather than full transcripts.
6. Preview affected files, scope and expected benefit without inventing a score delta. Apply authorised reversible edits; leave unclear semantic merges and policy changes for review. Model-specific guidance belongs in thin adapters, not project truth.
7. Repeat the same representative task/checks where feasible. Separate source-size estimates, observed submitted tokens, provider billing, auxiliary calls/retries and actual outcomes. Keep omitted measurements unknown. Do not introduce Jev calls or multi-agent work solely to claim optimisation.

## Output

Return the observed baseline, prioritised changes, files edited, preserved evidence/checks, verification results and remaining gaps. Include before/after metrics only when measured with the same scope and identified method. Keep the report compact; persist it only where useful and permitted.

## Completion

Requested changes are delivered within scope; relevant validators/checks ran or are explicitly unexecuted; required evidence and project authority remain intact. Unknown quality, savings, host behaviour and runtime enforcement are not reported as verified improvements.
