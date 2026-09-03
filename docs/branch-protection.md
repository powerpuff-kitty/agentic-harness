# Recommended Branch Protection

For `main` require pull requests, at least one approving review, conversation resolution, and successful `Agentic harness audit` and `Security baseline` checks. Disallow force pushes and branch deletion. Prefer signed commits/tags for releases.

This is a repository-host setting rather than a file-level control; it must be enabled in GitHub repository rules/branch protection. The audit should flag when it is absent.
