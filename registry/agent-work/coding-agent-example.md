# Integrated coding-agent example

This synthetic example demonstrates the Agent Work Protocol as one coherent coding run. It is a deterministic conformance fixture, not a recorded model session, benchmark, provider trace, or claim that a host loaded instructions.

## Scenario

A coding agent receives one scoped feature objective. The feature is represented by a parent Task with child Tasks for inspection, implementation, and verification.

1. The initial plan contains the feature, inspection, and implementation Tasks.
2. Inspection completes.
3. Implementation completes and produces a content-addressed patch artifact.
4. The agent replans by appending revision 2, adding an explicit verification Task while retaining all historical Tasks and revision 1.
5. The verification Task executes a focused synthetic test.
6. The `test.passed` WorkEvent references verified test evidence.
7. An independent deterministic evaluator records an evidence-backed validation metric.
8. The Run and WorkUnit complete with a separate output revision.

No field stores private chain-of-thought. The opaque session reference is correlation metadata only.

## Fixtures

| Concern | Fixture |
| --- | --- |
| WorkUnit v2, nested Task tree, attempts, plan revisions, result | `fixtures/coding-agent-example-work-unit.v2.json` |
| Observable lifecycle, replan, test and evaluation events | `fixtures/coding-agent-example-events.v1.json` |
| Verified focused-test result | `fixtures/coding-agent-example-evidence.v1.json` |
| Produced patch lineage | `fixtures/coding-agent-example-artifacts.v1.json` |
| Evidence-backed validation metric | `fixtures/coding-agent-example-metrics.v1.json` |
| Independent normalized evaluation | `fixtures/coding-agent-example-evaluations.v2.json` |

## Conformance

`.github/scripts/validate_agent_work_protocol.py` validates each fixture against its canonical schema and then validates the relationships across the scenario.

The cross-fixture checks require:

- at least one parent/child Task relationship;
- an append-only replan that changes the active Task set;
- completed WorkUnit and Run with a result revision;
- explicit `plan.created`, `plan.revised`, `test.started`, `test.passed`, `artifact.created`, and `evaluation.completed` events;
- verified test evidence attached to `test.passed`;
- artifact producer Run/Task/Attempt references that resolve;
- artifact retention on the producing Task graph;
- Evaluation → Metric → Evidence references that resolve and target the same WorkUnit/Run;
- absence of private-reasoning field names.

Negative mutations prove that a test pass without evidence and an Evaluation with a dangling Metric reference fail conformance.
