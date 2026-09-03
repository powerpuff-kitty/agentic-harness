# Compatibility Policy

Compatibility is tracked across the framework release, base template, skills, packs, and manifest/schema version.

`templates/base/template.json`, `skills/manifest.json`, and `packs/manifest.json` are the canonical module-version indexes.

An UPGRADE must preserve existing source-of-truth content and report incompatible changes before applying them. Vendor adapters should remain thin and may evolve independently as agent products change. Deprecated modules should remain available for at least one minor release when practical, with a replacement and migration note.
