# Audit Scoring

Scores are 0–100 and evidence-weighted.

## Bands

- 90–100: exemplary; strong controls and little material debt
- 80–89: strong; production-capable with limited gaps
- 70–79: good; meaningful gaps remain
- 60–69: fair; usable but several material risks
- 40–59: weak; substantial remediation needed
- 0–39: poor/unsafe for the target maturity

## Method

Start each applicable dimension at 70, then adjust using evidence. This avoids rewarding repositories merely for having files while allowing excellent implementations to reach 90+.

Positive evidence commonly adds 3–10 points: deterministic CI checks, clear boundaries, tested failure paths, automated security controls, maintained runbooks, healthy dependency discipline, measurable budgets, or high-quality agent routing.

Negative evidence commonly subtracts 3–15 points: missing tests, unsafe defaults, large coupled modules, undocumented architecture, no rollback, unpinned supply-chain execution, missing authorization boundaries, duplicated instructions, stale docs, or unverifiable claims.

A critical security or data-integrity flaw may cap the relevant dimension below 40 regardless of other strengths.

## Overall weighting

Default weights:

- code_quality: 12
- maintainability: 12
- architecture: 12
- testing: 12
- security: 16
- performance: 6
- dependency_health: 8
- documentation: 8
- agent_docs: 7
- operations: 7

Normalize after removing N/A dimensions.

Do not hide weak security behind a strong overall average. Always report security and production blockers independently.