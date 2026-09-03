# Audit Dimensions

## Code quality

Look for correctness signals, readable naming, lint/type discipline, complexity, duplication, dead code, error handling, unsafe shortcuts, consistency, and clear interfaces.

## Maintainability

Look for module size, coupling/cohesion, ownership boundaries, change locality, upgrade ease, migration discipline, configuration clarity, duplicated business rules, and sustainable repository organization.

## Architecture

Look for explicit boundaries, dependency direction, domain separation, interfaces/contracts, data ownership, deployment topology, ADRs, resilience/failure design, and whether implementation matches documented architecture.

## Testing

Look for unit/integration/e2e/contract/security/a11y tests as applicable, meaningful failure-path coverage, deterministic CI execution, flaky-test handling, fixtures, and coverage quality rather than coverage percentage alone.

## Security

Look for authentication/authorization, validation, secrets, least privilege, tenant isolation, secure defaults, dependency/supply-chain controls, SAST/secret/dependency scanning, threat models, logging/privacy, unsafe code execution, prompt injection/tool permissions for agents, and incident/recovery considerations.

## Performance

Look for explicit budgets, profiling/benchmarks where justified, N+1/query risks, bundle/runtime constraints, caching correctness, memory/CPU hotspots, backpressure for realtime/data systems, and performance regression checks.

## Dependency health

Look for lockfiles, pinned/reproducible installs, supported runtimes, dependency minimization, update tooling, vulnerability scanning, license/supply-chain considerations, and suspicious scripts/packages.

## Documentation

Look for accurate README/onboarding, product/architecture/data/API documentation, ADRs, runbooks, migration/deployment instructions, ownership, freshness, source provenance, and contradiction/staleness management.

## Agent-doc compliance

Where agent tooling is used, look for a compact router, canonical sources of truth, thin vendor adapters, scoped/nested instructions, skills separated from knowledge, machine-readable permissions, examples/evals, prompt-injection boundaries, approval gates, and deterministic validation of agent docs.

## Operational readiness

Look for CI/CD, environment separation, deployment strategy, rollback, migrations/backups/recovery, observability, alerts, incident/runbooks, health checks, feature flags where useful, SLOs, auditability, and production access controls.