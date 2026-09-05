# Harness Observatory data contract

The Observatory is a generated view over the Git-backed model registry and Agentic Readiness standard. It must not become a second source of truth.

## Views

- model index: profile id, vendor/model, profile version, effective date, status;
- model detail: recommendations grouped by context, skills, autonomy, completion, testing/tooling, and instruction sensitivity;
- model diff: recommendation additions/removals/changes between any two profiles;
- history: Git-backed change timeline with evidence/provenance;
- readiness reference: scoring dimensions and rule identifiers;
- machine feed: generated JSON suitable for CLI/CI consumers.

## Evidence display

Every model-specific recommendation must expose its confidence class and evidence records. UI must visually distinguish vendor-documented, benchmarked, community-observed, and inferred guidance.

## Generation

The website should be statically generated from `registry/` plus the scoring standard. Generated artifacts are disposable and must never be edited as canonical data.

## Extensibility

Adding a vendor or model requires only a valid profile under `registry/models/<vendor>/`; no navigation or schema redesign should be required.
