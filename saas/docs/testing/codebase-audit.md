# Codebase Quality Audit

Use the reusable `codebase-audit` skill when installed to measure repository quality across code quality, maintainability, architecture, testing, security, performance, dependency health, documentation, agent-doc compliance, and operations.

Treat scores as evidence-backed decision support, not absolute truth. Persist machine-readable results only when they are useful for trend comparison or CI gating.

Recommended audit moments:
- before production launch
- after large architectural migrations
- before/after major agent-driven refactors
- periodically for production/critical projects
- as a no-regression CI gate for security/testing where justified
