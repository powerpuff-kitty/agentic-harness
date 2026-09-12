# Public-surface policy

Public repository source and collaboration metadata must describe only approved public products, capabilities and dependencies. Do not name or link internal repositories, identify internal consumers in diagrams, or announce unpublished products through examples, issue/PR text, comments, release notes or generated artifacts.

The public ecosystem comprises `agentic-harness`, `agentic-harness-agents` and `agentic-harness-cli`. Generic interoperability requirements belong in public contracts; consumer-specific details do not.

## Review and validation

Run `python3 .github/scripts/validate_public_surface.py` or the catalog validation entrypoint. The regression validator allows the three public repository names and rejects other literal identifiers in this naming family, including case variants and one level of URL percent encoding. It checks current text and path names, including hidden docs and generated text outside excluded dependency/cache directories. It reports file/line and a generic reason, never the matched text. Identifiers in diagnostic paths are redacted.

The checker also compares the marked README onboarding example with `catalog/quick-start.json`. It does not execute shell text. The CLI's separate installed-binary tests must establish command behavior for the exact source pins.

Do not add actual internal names to a denylist or regression fixture: that would republish them. Tests use synthetic names. Review allowlist changes explicitly rather than extending it merely to make validation pass.

## Scope and limits

This is a narrow text regression check, not a complete privacy scanner. It does not understand arbitrary prose, obfuscation, renamed internal projects or binary/image content. Git internals, virtual environments, dependency directories and Python caches are excluded. NUL-containing binary payloads are outside scope; oversized/undecodable text, unreadable files and symlinks are reported rather than silently approved.

The validator cannot inspect GitHub issue bodies, comments, PR descriptions, repository settings, old commits or external caches. Review editable metadata separately. Removing a reference from current source does not erase Git history, historical diffs, notifications, forks or caches. History rewriting, publication and visibility changes require a separate explicit decision; do not force-push as part of a documentation fix.

## Capability claims

Mark supported, experimental and planned capabilities accurately. A context template is not application scaffolding. A policy declaration is not a runtime restriction. A valid artifact is not evidence that the project's tests ran. A rubric is not a successful model evaluation.
