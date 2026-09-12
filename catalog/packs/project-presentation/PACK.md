# project-presentation

Version: 0.1.0. Status: opt-in experimental contract, not a renderer or exporter.
Use for approved public case studies, brand presentations and design-system docs.

Read [CONTENT.md](CONTENT.md), [LAYOUT.md](LAYOUT.md) and [EXPORT.md](EXPORT.md).
The approved project identity and its canonical tokens/components remain authoritative.
Use [templates/PRESENTATION.md](templates/PRESENTATION.md) to establish project-owned
requirements without overwriting existing truth. The template is not public content.

`layouts.json` is the versioned composition vocabulary. The corresponding portable
schema is `catalog/schema/project-visuals.schema.json`. Installers must carry both;
normal pack-only copying is not evidence of complete schema/CLI support.
`examples/visuals.json` is a synthetic structure example with no distributable artwork.

Use six finite layouts, readable captions, source order on mobile, approved raster
assets and a static fallback. Reject unsupported executable templates, arbitrary
CSS, private material, invented claims and assumed redistribution rights.
Pricing, testimonials and traction are optional evidence-backed marketing content,
not mandatory portfolio sections. Web components are optional, not a prerequisite.

Validation has structural, semantic, file-byte and human-review stages. See EXPORT.
Test canonical coherence with `python3 .github/scripts/validate_presentation_contract.py`.
Schema conformance tests require the existing development jsonschema tooling and run
with `python3 -m unittest discover -s .github/scripts -p 'test_presentation_contract.py'`.
Do not claim full catalog/CLI/browser verification from those focused checks alone.

No default variant, source pin in downstream repositories, agent procedure, hosted
publication, project metadata or font license is changed by adding this pack.
