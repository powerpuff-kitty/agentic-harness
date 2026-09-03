# Dependency Upgrade

Inventory the dependency and its transitive/runtime impact. Read release notes and migration guidance. Separate security-critical upgrades from routine churn. Upgrade the smallest coherent set, regenerate lockfiles, run build/tests/lint/security checks, inspect API behavior changes, and record material decisions. Never disable security checks merely to make an upgrade pass.
