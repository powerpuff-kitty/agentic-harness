# Document and Decision Lifecycle

Durable knowledge should declare status when useful: draft, active, deprecated, superseded.

Recommended frontmatter:

```yaml
---
status: active
owner: architecture
last-reviewed: 2026-09-03
review-after: 90d
related:
  - ADR-014
---
```

## Rules
- Temporary execution state belongs in plans/tasks, not architecture truth.
- Proposed architecture choices are not accepted ADRs until explicitly decided.
- Superseded ADRs remain in history and link to the replacement.
- An implementation that contradicts docs should trigger investigation, not silent doc rewriting.
- Audits should flag stale, orphaned, contradictory, or duplicated instructions.
