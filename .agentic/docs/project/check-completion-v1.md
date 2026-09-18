# Caller-approved scoped completion v1

The experimental `check-completion.v1.schema.json` defines an evidence manifest and a separate scoped completion verdict. It consumes existing execution/governance v1 records without changing their meanings. ADR-010 records the owner's initial trust choice: caller-approved exact report digests; signed producers later.

## Review boundary

A `check-evidence-manifest` contains one run `{path,digest}`, up to 64 governance `{path,digest,producer:{id,version}}` entries and up to 64 reference `{name,path,digest}` entries. Paths are confined to the target, portable/normalized and link-free. References are opaque names resolved only through this approved manifest; no URL fetching. Repeated paths, names, reports or claims fail. All referenced bytes must match their digests.

The caller reviews the reports, provenance, required project controls and reference bindings, then independently supplies the SHA-256 of the exact manifest bytes through `--approve-evidence`. This approves the included report and reference digests, not arbitrary future reports from that producer. No persisted approval, auto-accept option or report-controlled trust. Never automatically pipe a calculated digest into approval for an arbitrary project. Synthetic tests may approve only their authored fixed fixtures.

## Evaluation

`ah checks complete [TARGET] --evidence PATH --approve-evidence sha256:REVIEWED_MANIFEST` accepts optional explicit `--config` and `--settings`. It never runs commands. Read/validate the manifest (262144 bytes maximum) and compare approval before following any reference. Limit run bytes to 2000000, governance reports to 1 MiB each / 8 MiB total, and references to 2000000 each / 8 MiB total. Reuse bounded, deadline-aware current review and source snapshots. Recheck report/reference/manifest bytes, then final project/policy/settings/tool/executor identities. No inherited approval from `checks run`.

The imported run's complete review must equal the freshly generated review, including exact executor, host, tools, target and selected configuration. Recompute RunLedger from plan-owned flags/order, exact argv/cwd and validated outcomes. Reject absent/extra/duplicate results, integrity failures, halted runs, stale/future/contradictory timestamps or noncurrent inputs. Ordinary optional failures remain visible and follow existing ledger semantics. Conservatively require run start within `max_age_ms`, and bounded passing durations. The same binary and target are required; cross-host or upgraded-executor reports require a fresh run.

Governance assertions must match current source/policy/scope and exact required capability, fall within maximum age, match approved producer/version and bytes, and resolve every evidence reference. Reject malformed, duplicate/conflicting, missing, unsupported, unverified or failed required claims. Do not substitute declared for enforced.

Success emits `check-completion` with `completion_verified:true` only for `scope:declared-checks-and-required-controls` under `trust:caller-approved-exact-evidence`; `producer_authenticated:false` is mandatory. Record manifest/run/policy/source digests and evaluation time. Rejection exits 2 with an omitted-content diagnostic and no completion artifact. Existing audit/gate and check-run artifacts are unchanged; check-run completion remains false.

## Limits and compatibility

This is acceptance under explicit caller trust, not independent proof of execution or enforcement, cryptographic producer authentication, a sandbox or whole-project readiness. The caller's evidence assessment, local clock and approved policy remain trust inputs. Reference integrity does not prove semantic truth. No protection against an unrestricted agent supplying approval flags, hostile concurrent races, reverted mutations, undeclared inputs or changes after evaluation. No implicit files are written. Keep evidence outside declared input roots to avoid self-referential digests.

The consuming CLI must pin this schema, test actual outputs against it, and provide command-level negative tests. Agent procedures must require explicit caller review and preserve scoped claims. Existing projects need no migration; older clients lack this command and must not interpret the new verdict as an old audit artifact.
