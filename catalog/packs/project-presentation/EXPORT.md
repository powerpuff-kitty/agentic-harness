# Export and replication contract

## Ownership and installation

Catalog: reusable requirements, layout vocabulary and schemas.
Project: accepted presentation requirements, canonical facts/tokens/assets and
publication decisions. Agent procedures: agentic-harness-agents. Deterministic
installation/import/diff checking: agentic-harness-cli. Renderer: the consuming
portfolio/docs application. Do not move every responsibility into the catalog.

Install this opt-in pack at a reviewed source revision. Preserve the project's
current `.agentic/DESIGN.md` and metadata. Create a project-owned
`.agentic/PRESENTATION.md` from the template only after review; a later catalog
update must not overwrite it. Resolve installed files and checksums in the normal
manifest/lock lifecycle. The new pack is not silently installed across repositories
and this proposal does not modify CLI source pins or guarantee CLI support.

## Data and artifacts

A source project can maintain:

```text
.agentic/PRESENTATION.md        # owner-reviewed requirements, not public content
presentation/visuals.json       # portable visual extension, schemaVersion 1
presentation/media/             # reviewed raster exports for this subset
presentation/content.json      # host-mapped narrative, or a generated snapshot
presentation/tokens.json        # optional generated token export, never forked truth
```

Names are a recommended convention, not a requirement to duplicate existing
canonical files. The source project's normal metadata remains authoritative. A
consumer maps `projectId` to its canonical catalogue, references assets, and pins
the source revision, schema/layout versions and hashes in an import record.
Product source revision and catalog-contract revision are different values.

The visual extension requires: projectId, a bounded asset registry and ordered
visual sections. Each asset has a project-relative path, kind, intrinsic pixel
dimensions, SHA-256 of exact exported bytes, alternative text, credit and an
approved rights record. Rights are a review declaration, not a legal determination
made by the validator. An approved display use does not transfer ownership or
permit arbitrary resale. Font names never authorize sharing font files.

V1 raster support is PNG/JPEG/WebP. SVG, video, 3D and executable examples require
separate capability/security contracts; do not weaken file validation to accept
them. The example hashes/paths are deliberately synthetic and must fail real-file
verification until replaced by approved files. Reference moodboards are not product
assets and must not be copied into a public export merely for convenience.

## Validation stages

1. Structural JSON Schema: allowed types, enums, bounded strings, dimensions and
   item cardinality. Unknown fields fail. No arbitrary HTML/JS/CSS/remote URLs.
2. Semantic checks: unique section/heading IDs, valid asset references, matching
   project identity, no duplicate asset paths, no unused/unreviewed assets, bounded
   total pixel/file budget. Do not crop screenshots/logos.
3. Filesystem/byte checks: project-root confinement, no symlinks, extension and
   signature/dimensions agree, exact SHA-256, bounded size, approved export files
   only. Files in a public directory are public even when a UI hides them.
4. Human review: rights, personal/client information, hidden image metadata,
   factual claims, the intended brand, actual rendering, keyboard/zoom and alt text.

A signature/header check is not a complete image decoder, sanitizer or metadata
scanner. A hash provides byte identity, not proof of licensing or truth. Store no
access tokens, source credentials, personal enquiries or private source links in
public JSON. Export only the approved subset; dry-run and diff before applying.

## Optional execution

Publishing a design system does not require web components. Prefer token data,
static assets and actual native component documentation. A reusable custom element
is justified by external consumers, not by a portfolio screenshot requirement.
A showcase widget is not the same product as a reusable UI component library.

An interactive example must declare its capabilities/network behavior, use synthetic
fixtures, activate explicitly, provide a static fallback and have verified teardown.
Shadow DOM is not a JavaScript permission boundary. Independent-origin sandboxing
and messaging need their own reviewed contract. No runtime repository query, CMS
or database is needed for a file-based presentation.

Primary references: https://www.designtokens.org/TR/2025.10/format/
https://www.w3.org/WAI/tutorials/images/
https://vuejs.org/guide/extras/web-components.html
