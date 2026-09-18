# Reading-list context

Start with this map and `manifest.yaml`, then load only the relevant truth.

| Task | Read | Purpose |
| --- | --- | --- |
| Change behavior or resolve product scope | PRODUCT.md | Journeys, rejection/recovery and explicit open decisions |
| Change dependencies or data flow | ARCHITECTURE.md | Intended implementation boundaries and invariants |
| Change controls or visual states | DESIGN.md | Scenario intent and missing implementation evidence |
| Touch input, links, storage or permissions | SECURITY.md | Threats, controls and verification expectations |
| Reconsider a durable choice | decisions/ | Decision lifecycle and index; no historical decisions recorded |
| Reproduce installation | lock.json | Unresolved sources; this fixture is not an installed project |

All paths above are relative to this directory. No optional docs, plans, tasks, packs, policies or skills have been installed. Create supporting context only when useful content exists.

Precedence: installed mandatory policies, current project truth, accepted ADRs, packs, skills, task prompts. Record unresolved decisions explicitly; absent tests and missing implementation never count as successful verification.
