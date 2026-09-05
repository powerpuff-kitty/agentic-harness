# Model best-practices registry

This registry tracks model-specific agentic guidance without duplicating project truth.

## Rules

- Canonical project architecture, product rules, security policy, and accepted decisions remain model-independent.
- Model profiles contain only adaptation guidance: context density, skill selection, autonomy/completion behavior, testing/tool use, and known instruction sensitivities.
- Every recommendation requires provenance and a confidence class.
- `vendor-documented` and reproducible `benchmarked` evidence should outrank community observations.
- Changes are versioned in Git. Prefer a new profile version or an explicit supersession when guidance materially changes.
- Do not add speculative model claims without evidence.

## Layout

- `model-profile.schema.json` — canonical machine-readable schema.
- `models/<vendor>/<model>.json` — current profile for a model.
- `history/` — optional snapshots/migrations when retaining prior material outside Git history is useful.

The CLI may embed or sync this registry, but must not hardcode duplicate model opinions.
