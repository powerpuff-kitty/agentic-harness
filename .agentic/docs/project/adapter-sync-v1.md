# Context adapter installation report v1

Experimental, additive artifact for CLI #65 and agents #24. Schema: `catalog/schema/adapter-sync.v1.schema.json`. No audit, gate, execution-policy or manifest contract changes.

The report describes a create-only preview or application of explicitly selected context assets. Destinations are bounded to the approved Claude/Cursor context files and a retained MIT notice under `.agents/adapters/LICENSE`. Existing product context, custom routes, settings, permissions and hooks are not rewritten.

`entries` retain the preview's create/unchanged/conflict decisions and exact desired/existing content hashes. `source` identifies the pinned agents repository commit; inventory and router hashes bind inputs. The review digest hashes the CLI's stable serialized preview (before adding the digest field) using the domain `ah-adapter-sync-v1` plus NUL and one unsigned 64-bit big-endian byte-length-prefixed field. This is not JSON canonicalization, an authentication credential or independently verified host evidence.

`ready` is preview-only. `conflict` can be reported during preview or application but claims no writes. `applied` means the selected files were verified present with expected bytes when the installer finished; it does not imply they were loaded by a host. `partial` retains successful creates and created directories alongside an error. Multi-file crash atomicity and automatic rollback are not promised. Reinspect a failed or interrupted install before retrying; a fresh preview can continue without rewriting identical files.

`host_delivery_verified` and `enforcement_verified` are always false. Live-host imports, glob selection, instruction adherence and actual restrictions need separate evidence. Schema validity alone cannot establish digest correctness, provenance authenticity, exact state/action correspondence or filesystem safety.

## Public archive-name regression

Upstream source validation found the public plugin archive template was being interpreted as a new repository identifier. The literal public-name check now recognizes only the approved agents ZIP filename family with X.Y.Z, optional alpha/beta/rc.N or the literal `{version}` placeholder, and optional `.sha256`. GitHub repository URL segments are checked before archive normalization; a versioned archive-shaped string is not permitted as an unapproved repository slug. Other repository suffixes remain rejected and diagnostics remain redacted. This is a narrow text regression check, not semantic privacy certification.

The report's actual CLI implementation and fresh installed-binary tests remain tracked in powerpuff-kitty/agentic-harness-cli#65. Structural fixtures and public-name regression tests do not themselves establish that installation works.
