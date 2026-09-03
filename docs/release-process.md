# Release Process

Before a public release:

1. CI, unit tests, repository validation, template audit, and security baseline must pass.
2. Update `CHANGELOG.md` and module manifests.
3. Run the CLI against a clean temporary project and at least one existing-project UPGRADE fixture.
4. Review schema/template compatibility and document migrations.
5. Tag using semantic versioning.
6. Do not publish a release with known high/critical audit findings unless explicitly documented as accepted risk.

A production-quality release should also have branch protection requiring the CI/security checks and review before merge.
