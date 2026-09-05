# Agentic Readiness scoring standard

Agentic Readiness evaluates how effectively a repository exposes context, procedures, verification, and safety boundaries to coding agents. It is separate from ordinary code-quality scoring.

## Two scores

1. **Universal Agentic Structure Score** — model-independent repository quality.
2. **Model Compatibility Score** — fit between the current repository structure and one evidence-backed model profile.

A new model release may change compatibility without changing the universal score.

## Universal dimensions

| Dimension | Weight |
| --- | ---: |
| Context architecture | 14 |
| `AGENTS.md` quality | 10 |
| Skill architecture | 10 |
| Documentation routing | 9 |
| Completion semantics | 9 |
| Decision boundaries | 8 |
| Verification/tooling | 10 |
| Architecture discoverability | 7 |
| Decision history | 5 |
| Model portability | 6 |
| Instruction health | 7 |
| Agent security posture | 5 |

Weights total 100.

## Finding severities

- **critical**: unsafe or destructive agent behavior is plausibly enabled; subtract 25 from the affected dimension and cap overall score at 59 until resolved.
- **high**: likely to materially reduce correctness, context efficiency, or safety; subtract 15.
- **medium**: recurring friction or avoidable ambiguity; subtract 7.
- **low**: quality improvement with limited immediate impact; subtract 3.

Dimension scores start at 100 and are clamped to 0..100. Multiple findings may accumulate. Positive capability bonuses are not used in v1; absence of a finding is the reward, which keeps scores explainable.

## Required finding shape

Every automated finding should provide:

```json
{
  "rule": "AH-CONTEXT-001",
  "severity": "high",
  "dimension": "context_architecture",
  "message": "Five documents are required for every task.",
  "evidence": ["AGENTS.md:4"],
  "remediation": "Replace unconditional reads with task-scoped routes.",
  "confidence": "deterministic"
}
```

## Baseline rules

### Context architecture
- `AH-CONTEXT-001` high — mandatory broad/full-repository reading.
- `AH-CONTEXT-002` medium — oversized always-loaded instruction surface.
- `AH-CONTEXT-003` medium — no conditional context router/index where substantial project truth exists.

### AGENTS.md quality
- `AH-AGENTS-001` medium — duplicated project truth that belongs in canonical `.agentic/` documents.
- `AH-AGENTS-002` medium — no precedence or routing guidance.

### Skills
- `AH-SKILL-001` high — strongly overlapping trigger descriptions.
- `AH-SKILL-002` medium — broad domain-level trigger likely to activate for unrelated tasks.
- `AH-SKILL-003` low — large skill lacks progressive disclosure to supporting material.

### Completion and autonomy
- `AH-DONE-001` medium — no completion/verification semantics.
- `AH-AUTONOMY-001` high — destructive/release/secret actions lack approval boundaries.
- `AH-AUTONOMY-002` medium — overly restrictive instructions prevent safe local verification or fixes.

### Portability/instruction health
- `AH-PORT-001` medium — vendor adapter redefines canonical project truth.
- `AH-INSTR-001` high — contradictory instructions across always-loaded files.
- `AH-INSTR-002` medium — materially duplicated instructions across agent/vendor/skill files.

### Security
- `AH-SEC-001` critical — instructions permit exposing secrets or executing destructive production operations without approval.
- `AH-SEC-002` high — no explicit boundary for secrets/production/destructive actions in a repository that documents those capabilities.

## Model compatibility

Compatibility starts from the universal structure score and applies only evidence-backed profile rules. Model recommendations must not be invented from generic reputation. Each adjustment must identify the model-profile recommendation and its evidence/confidence class.

## Confidence

Automated findings use one of:

- `deterministic` — direct structural/textual rule;
- `heuristic` — pattern-based and potentially noisy;
- `profile-backed` — model-specific rule with registry evidence.

Reports must expose confidence alongside scores so users can distinguish measured structure from interpretation.
