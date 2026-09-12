# Optional presentation contract

The catalog now contains the opt-in experimental `project-presentation` pack,
version 0.1.0, and portable `project-visuals` schema version 1. It separates content
meaning, a finite layout vocabulary and product-owned art direction. Public metadata,
identity and token implementations remain project-owned canonical sources.

The pack defines requirements/templates and a visual extension, not an application
renderer, complete narrative schema, installer, exporter or mandatory component
conversion. Default variants and existing installed project context are unchanged.
A consumer can map the extension into its own versioned page document, preserving
project IDs, source revisions, hashes and explicit public-asset approvals.

Canonical source roles remain separate: this repository owns the contract;
agentic-harness-agents owns reusable procedures; agentic-harness-cli owns installation
and deterministic import/diff behavior. Source pins and migration tests in those
repositories require separately reviewed adoption. A copied pack must not be
presented as an already supported CLI command. No downstream pin is changed here.

The project's .agentic/PRESENTATION.md remains internal project truth. Preserve it
when updating templates; only an approved subset becomes public narrative/assets.
Reference boards, fonts and private product details are not catalog fixtures.

Quality evidence: run the focused coherence/schema tests, then the full structural
and public-surface validators on a complete checkout. A schema match does not prove
rights, factual truth, accessible rendering or byte safety. See EXPORT.md for the
four validation stages and the consuming renderer's responsibilities.
