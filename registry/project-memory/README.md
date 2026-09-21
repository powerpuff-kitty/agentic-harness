# Project Memory

Project Memory is the provider-neutral retained-knowledge layer for Agentic Harness.

It stores compact, validated project knowledge across runs without turning repository instructions, transcripts or model context into an ever-growing history. Memory is local-first and model-independent; local, remote and hybrid providers implement the same contracts.

## Boundaries

Project Memory is separate from:

- project truth: version-controlled rules, architecture and accepted decisions;
- context: a bounded task-specific projection shown to a model;
- reflection: structured post-attempt analysis that may propose a memory candidate;
- execution history: Agent Work events, attempts, evidence and artifacts.

A reflection may propose a candidate memory, but promotion is a separate auditable MemoryOperation. Memory never silently becomes project truth, and raw chat history/private chain-of-thought is not a memory source.

## V1 contracts

- memory.v1.schema.json — memory content, scope, provenance, validity, confidence, sensitivity, usage and lineage.
- memory-query.v1.schema.json — task/scope-aware retrieval request.
- memory-result.v1.schema.json — provider-neutral matches/exclusions with retrieval explanation.
- memory-provider.v1.schema.json — local/remote/hybrid provider capabilities and sensitivity policy.
- memory-operation.v1.schema.json — promotion, reverification, supersession, invalidation, consolidation and expiry.

## Lifecycle

    observation / decision / reflection
      -> candidate memory
      -> validate + deduplicate
      -> promote
      -> retrieve when task-relevant
      -> reverify
      -> supersede / invalidate / consolidate / expire

Memory is intentionally non-monotonic. Superseded, invalidated, stale, expired and consolidated records remain inspectable for auditability but are not silently treated as current truth.

## Sensitivity

A memory carries an explicit sensitivity level and remote persistence/retrieval flags. local_only memories must be filtered before any remote provider handoff. Provider capability/configuration metadata never contains raw authentication secrets; configuration_ref points to external configuration when needed.

## Retrieval

Retrieval is task- and scope-aware. MemoryResult preserves the memory identity, provider identity, relevance method, confidence when available, matched scope and exclusion reasons. Storage size does not imply context size: the Context Gateway decides which retrieved memories, if any, are worth including in model context.

## Consolidation

Consolidation creates a new memory with consolidated_from lineage and preserved source references. Inputs remain inspectable and point to consolidated_into. Consolidation must not erase provenance.

## Validation

Run:

    python3 .github/scripts/validate_project_memory.py

The validator checks schemas and representative fixtures for privacy, stale/superseded/invalidation semantics, bidirectional lineage, conflicts, consolidation provenance and query/result filtering.
