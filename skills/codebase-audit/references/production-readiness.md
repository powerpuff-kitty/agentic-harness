# Production Readiness

Assess four maturity targets independently.

## Prototype

Requires understandable setup, basic correctness checks, no obvious secret/security hazards, and enough documentation to continue development.

## Startup

Adds reliable CI, meaningful tests, migrations/data safety, dependency hygiene, basic security review, deployment documentation, and minimal observability.

## Production

Adds repeatable deployment and rollback, environment separation, stronger authorization/security controls, automated supply-chain/security checks, operational runbooks, monitoring/alerts, backups/recovery where stateful, compatibility/migration discipline, performance/accessibility requirements as applicable, and maintained source-of-truth documentation.

## Critical

Adds explicit threat models, stricter review/approval gates, auditable access, tested disaster recovery, stronger tenant/data isolation, security regression testing, dependency provenance/SBOM expectations, incident exercises, high-availability/failure-mode analysis, and tighter agent/tool permissions.

## Blockers

A production-readiness score above 80 should not be assigned when any applicable blocker remains unresolved, such as:

- no reliable build/test path
- known critical security issue
- no authorization model for privileged operations
- unsafe secret handling
- destructive migrations without rollback/recovery
- stateful production system with no backup/recovery plan
- deployment with no rollback/recovery path
- unbounded autonomous agent writes to production or privileged tools
- critical external dependencies with no failure strategy

Always distinguish `not present` from `not applicable` and `not checked`.