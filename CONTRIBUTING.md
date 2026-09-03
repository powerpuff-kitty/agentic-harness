# Contributing

Preserve the repository boundaries: Rust crates are deterministic engine code; `packages/` contains official distributable templates, packs, skills, policies, profiles, and presets; `schema/` contains public machine contracts.

Before opening a PR run:

```bash
cargo check --workspace --all-targets
cargo test --workspace --all-targets
cargo run --quiet -- validate .
cargo run --quiet -- harness-audit packages/templates/base
cargo run --quiet -- audit .
```

New skills require `packages/skills/<name>/SKILL.md`; new packs require `packages/packs/<name>/PACK.md` and a manifest entry. Runtime behavior belongs in Rust crates. Keep package content framework-neutral unless the package explicitly declares a narrower scope. New third-party crates should be justified by capability, maintenance, security, and binary-size tradeoffs.
