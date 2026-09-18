# Roadmap and delivery reconciliation — 2026-09-18

The owner requested that project #5 tickets reflect their roadmap and repository ownership and that in-progress work continue toward completion.

## Board audit and repair

Before: 83 issues, 82 without labels; 71 Backlog, 6 In progress, 6 Done. Canonical #84 and tracker #87 incorrectly remained Backlog. Nine selected roadmap dependencies were absent. Existing issue state and Done status agreed; no issue needed reopening or premature closure.

After verified readback: 92 issues, all with `roadmap` and exactly the corresponding `repo:agentic-harness`, `repo:agentic-harness-cli` or `repo:agentic-harness-agents` label. Existing labels were preserved. Repository means the issue's source owner; it does not transfer implementation responsibility. The built-in Repository field remains available. Explicit title priorities were copied to the project Priority field: 8 P0, 16 P1 and 1 P2; no priority was invented for the other 67 issues.

| Repository | Backlog | In progress | Done | Total |
| --- | ---: | ---: | ---: | ---: |
| agentic-harness | 66 | 4 | 6 | 76 |
| agentic-harness-cli | 6 | 5 | 1 | 12 |
| agentic-harness-agents | 2 | 2 | 0 | 4 |
| Total | 74 | 11 | 7 | 92 |

Added CLI #26/#38/#39/#50/#56/#57 and agents #24/#25/#26, which are explicit roadmap or #84 dependencies. This is not an import of every unrelated open issue across the ecosystem. All canonical open issues were already represented. Closed CLI #56 is Done.

Active work:

- Canonical #84: minimal context/deeper packs, implemented locally; publication/review/platform CI pending.
- Canonical #85: governance semantics and caller-approved completion, implemented locally; publication/review/platform CI pending.
- Canonical #86: runnable adoption fixture and deterministic verification; native-host acceptance blocked by the observed Claude authentication failure.
- Canonical #87: coordinating roadmap, open until its tracked scope is complete.
- CLI #55/#61/#62/#63: integrated executor, ledger, ownership and bounds corrections, locally tested; fresh candidate review/platform evidence pending.
- CLI #50: candidate release review, still no-go pending final platform/dependency/provenance/rollback evidence.
- Agents #24/#25: native adapters and flagship procedures, partially delivered; remaining host/managed-operation/procedure outcomes are explicit in their issues.

## Reconciliation with current main

Canonical main advanced to `ccc74b1` with Decision Kernel contracts; CLI main advanced to `3787605` with its offline runtime. The local branches required conflict resolution before review.

Canonical merge `6b03603` preserves ADR-008/009/010, both completion and Decision Kernel validators, context selection and catalog documentation. Catalog and combined contract suites pass. CLI reconciliation retains both command families and pins this combined catalog with agents `7e7d44e`. An upstream CLI test hard-coded the previous catalog revision; it now compares the reported source identity with the exact lock entry. Its 35-test CLI suite passes after correction.

Final combined CLI candidate `02bf336` passes all 197 Rust tests, formatting, Clippy and actual-output contract validation, including 20 adapter, 16 skill-delivery, 17 context-selection and 25 completion probes. CLI review: `docs/reviews/2026-09-18-roadmap-integration.md`. The branches are ready for source publication/review, subject to approval and fresh remote CI. Earlier optimized candidate evidence remains historical; it is not relabeled as evidence for new source or pins.

## Finish order and publication boundary

1. Finish local combined-candidate validation and prepare review descriptions.
2. Publish the canonical and agents branches for review, then publish the CLI branch with reachable exact pins. Source publication requires the approval specified by `.agentic/manifest.yaml`; the owner's explicit instruction to update GitHub tickets authorizes the board/issue updates already performed.
3. Observe fresh platform CI and review the delivered acceptance criteria before closing #84/#85 and CLI #55/#61–#63. Preserve the original CLI #60 review history when superseding its candidate.
4. Repair configured Claude authentication and retry only within the authorized single-file, requested $1, 300-second trial limits. Record real outcomes for #86. One run cannot satisfy all agents #24 host variants or #26 comparative/repeated evaluation acceptance.
5. Complete remaining agent procedure/evaluation scope and candidate-specific release gates. No release/tag is part of the branch-publication proposal.

No source push, main merge, release or successful model task is claimed by this reconciliation. No issue was closed merely because local tests pass.
