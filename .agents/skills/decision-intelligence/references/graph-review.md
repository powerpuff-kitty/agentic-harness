# Review declared decision dependencies

Use this only for a task involving an existing, explicitly reviewed DecisionGraph. Ordinary classifications need no graph, Python helper, extra agent or provider. The canonical Decision Kernel owns graph/spec/request/receipt contracts; this is a local inspection aid, not another wire contract or workflow runtime.

## Optional read-only check

From this skill's root, when local helper execution is permitted:

```sh
python3 scripts/review_graph.py /reviewed/path/graph.json --group-size 4
```

The [helper](scripts/review_graph.py) uses Python 3.10+ standard library. It reads only the named non-secret UTF-8 JSON file and emits a source hash plus declared dependency layers. It neither reads spec references nor invokes providers, reducers, commands or writes. Without it, inspect node identities, dependencies and reducer inputs manually; do not install a runtime automatically.

A group is a bounded display of nodes in one topological layer, NOT an authorized provider batch. Later layers require successful, policy-acceptable predecessor results at runtime. Reducer's `declared_inputs_after_layer` describes structural order only; it does not mean results exist or were accepted. Cycles and invalid references suppress all groups, including otherwise independent prefixes.

Exit 0 means the supported graph structure is reviewable; 1 means declared dependency defects block grouping; 2 means malformed, unsupported or unavailable input. Duplicate node/edge declarations are rejected as malformed. No exit means project tests passed, the decisions are correct or an action is permitted.

## Before any real grouped judgment

Prefer native tools for mechanically answerable questions. For the remaining semantic questions, verify exact specs and criteria, independently sufficient current evidence including contradictions, compatible immutable state, provider capability, disclosure permission and the full call/retry budget. Graph edges alone cannot prove semantic independence or identical state. Do not widen state disclosure merely to combine questions.

Repeated spec ID/revision references are highlighted, never removed: different nodes may have different inputs or scopes. Even matching file hashes do not authenticate earlier judgments or restore lost context. Recheck required rules and changed dependencies. Missing inputs, abstention and provider failures block dependent judgments; they must not be coerced into false, zero or a successful result. Reducers remain deterministic, separately implemented and reviewed.

Actual Jev integration still requires the independently installed official TypeSafe skill and current vendor documentation, with explicit permission. This helper makes no inference, cost, latency or token-saving claim. Fewer proposed groups are not fewer measured provider calls.

## Supported subset and bounds

Input is the existing `decision-graph` v1 shape: graph ID/revision/nodes and optional reducers; node ID/spec ID/spec revision/depends_on; deterministic reducer ID/inputs and optional output. Unrecognized fields are `unsupported-fields`, not silently ignored or evidence that the full canonical schema rejects them. The helper is deliberately not a JSON Schema validator, spec resolver, state verifier, scheduler or execution-policy engine.

Limits: 64 KiB input, 128 nodes, 32 reducers, 4096 node-dependency edges, 256 characters per identifier, revisions 1 through 2147483647, and display group size 1 through 32. Observed symlinks, traversal and nonregular inputs are refused. A trusted quiescent filesystem is required; no atomic snapshot or sandbox is claimed. Output includes supplied graph/spec identifiers: use non-secret inputs and review output before sharing.

Canonical basis: [DecisionGraph v1](https://github.com/powerpuff-kitty/agentic-harness/blob/main/catalog/schema/decision-graph.v1.schema.json), reviewed source blob `75cae2884600eb56da4787631e3223902fd2d852`, and its declared-node/reducer dependency semantics. Reconcile future contract changes before widening this subset.
