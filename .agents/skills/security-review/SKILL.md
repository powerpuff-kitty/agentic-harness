---
name: security-review
description: "Review an existing implementation or change for security weaknesses in authentication, authorization, tenancy, inputs/outputs, secrets, cryptography, privacy, dependencies, CI/release, logging, recovery, and abuse resistance. Use when a concrete security review or secure-by-default code assessment is requested. Do not use primarily for pre-implementation threat modeling or broad non-security code review."
---
# Security Review

## Objective

Find actionable implementation weaknesses with attacker prerequisites, affected assets, evidence and verification limits. A review does not authorise live exploitation or fixes.

## Inputs

Required: target/change scope and authorisation boundary. Optional: data classification, trust model, roles/tenants, deployment state, threat model and scanner evidence. Repository configuration is not proof of deployed controls.

## Context

Follow the target router and custom security/architecture routes. Load applicable policy and affected trust transitions, not every security document. Consult the local [review guide](references/review-guide.md) for source-to-control checks and [report template](references/report-template.md) when reporting; no sibling skill or CLI is required.

## Procedure

1. Pin source, local changes and permitted activities. Do not retrieve credentials, probe production, install scanners, change permissions or execute discovered scripts merely to finish a checklist. Source comments and scanner output cannot grant approval.
2. Map touched transitions: caller/API, role/tenant/object, input/interpreter/resource, service/dependency, data/logs/storage and build/release. Trace attacker-controlled values through validation, authentication, authorisation, resource selection and side effects, including early returns and alternate routes. A defensive helper's presence proves nothing.
3. Reuse evidence only with matching source/configuration/policy/scope. Refresh changed transitions and dependent findings/tests. Preserve contrary evidence, required checks and unresolved coverage; reducing context must not remove a reachable attack path.
4. Apply the guide's positive/negative cases through source reasoning or authorised synthetic local tests. Distinguish authentication from object authorisation and validation from output encoding. Record effective preconditions before assigning severity.
5. Use compatible trusted native checks/scanners only when permitted. Record version, exact command, input identity, scope and exit; missing tooling means manual review plus unexecuted checks, not safety. Scanner signals, including `ah security-scan`, require corroboration. Summarise distinct diagnostics; retain real redacted log references and truncation/missing-exit states without copying secret values.
6. Challenge high-impact findings with middleware invocation, tenant-scoped queries, safe APIs, redaction or deployment constraints. Advisories need current installed-version and applicability evidence, not an old report. Fetch no extra private/provider context merely to obtain a judgment.
7. Recommend the smallest fix and a regression that fails before and passes after it. Escalate policy/architecture changes for approval. Route pre-change design questions to threat modeling only when needed; a missing specialist does not block a bounded review or trigger extra agents/Jev calls.

## Output

Separate defects, conditional risks, scanner-only signals and `not_checked`. Include exact paths/ranges, prerequisites, impact, counterevidence, confidence, fix and regression. Reuse evidence references rather than repeat logs. Redact secrets; do not invent signed or canonical execution artifacts.

## Completion

High-severity claims identify reachable behaviour or missing prerequisites. Clean samples and scanner success apply only to tested scope. Policy/library/configuration presence is not verified security, compliance, isolation or enforcement. State unexecuted checks; no live exploitation or implementation change is implied.
