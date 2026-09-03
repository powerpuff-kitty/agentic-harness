# Contributing

Changes should preserve the repository boundaries: templates are generated project shape, packs are knowledge, skills are procedures, schemas are machine contracts, and the Rust CLI is deterministic enforcement.

Before opening a PR run:

```bash
cargo check --all-targets
cargo test --all-targets
cargo run --quiet -- validate .
cargo run --quiet -- harness-audit templates/base
cargo run --quiet -- audit .
```

New skills require `skills/<name>/SKILL.md`; new packs require `packs/<name>/PACK.md` and a manifest entry. Runtime behavior belongs in Rust. New third-party crates should be justified by capability, maintenance, security, and binary-size tradeoffs.
