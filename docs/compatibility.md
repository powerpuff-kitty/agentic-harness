# Compatibility Policy

Compatibility is tracked across the Agentic Harness canonical content revision, base boilerplate, packs, policies, profiles, presets, schemas, agent skills, and CLI release.

`boilerplates/base/template.json`, `packs/manifest.json`, and the schemas in `schema/` are canonical indexes/contracts in this repository. Agent skill versions are maintained in `agentic-harness-agents`.

An upgrade must preserve existing source-of-truth content and report incompatible changes before applying them. Agent adapters should remain thin and may evolve independently as agent products change. Deprecated modules should remain available for at least one minor release when practical, with a replacement and migration note.
