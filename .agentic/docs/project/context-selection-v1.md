# Context selection v1

The catalog owns `catalog/context/profiles.v1.json`, validated by `catalog/schema/context-profiles.v1.schema.json`. CLI implementations consume those pinned files; organization profiles, packs and host adapters remain separate concepts.

## Selection and persistence

Compatible implementations expose `init` and `upgrade --context-profile full|minimal`. Optional manifest mapping `composition: {context_profile: minimal}` records the selection. An absent mapping means full for compatibility. An omitted option preserves an existing selection. Unknown values or malformed mappings fail before mutation.

Full selects the complete materialized variant. Minimal selects 12 baseline files, adds DESIGN.md for listed visual variants or selected design-related packs, and adds routers for selected packs, policies and skills. Modules install completely; the baseline excludes modules, skills, native adapters and project-authored additions. The design template falls back to the declared variant when the selected variant has none.

For a fresh minimal target, omitted optional manifest routes are null and the generated context map lists selected routes and module categories. No empty optional trees or vendor adapters are added by minimal selection. Host delivery uses separately supported adapter commands. Template content remains unresolved intent until configured by the project.

## Preservation and mode changes

Changing modes changes which absent files may be added; it never prunes existing files. Preserve authored truth, custom optional documents, module edits, custom routes and explicitly null routes. Preserve the original checksum for a retained file and report conflicting generated content. Existing context maps are project-owned: report differences for reconciliation rather than silently rewriting them. On minimal-to-full expansion, null routes remain null until the project enables them.

An upgrade without a new variant/preset selection uses the installed variant recorded in the lock where available. Older projects without a lock may use their recognized project type. Legacy-layout refusal remains unchanged; this feature does not perform filesystem migration.

Composition metadata uses existing atomic per-file updates and recoverable rollback. Checksums bind the manifest selection without changing lockfile v1. Missing selection-contract build inputs must fail the build.

## Verification and claims

Test fresh minimal/full targets, visual/module additions, repeated composition, inherited selection, both mode transitions, custom/null routes, customized modules, malformed selection, legacy refusal and injected write failure. Exercise a copied executable outside the checkout and validate emitted manifests against the pinned schema.

Report source/build identity and actual file/byte counts. File count, word count, configured checks and executed behavior are separate. No model performance, host delivery, enforcement or application-test success follows from smaller context.

Availability depends on the installed CLI version; inspect help/version rather than assuming an older published binary supports the option.
