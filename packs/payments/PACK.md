# Payments Pack

Use for billing, checkout, subscriptions, payouts, or money movement.

Minimize payment-data scope; prefer hosted/tokenized provider flows. Require idempotency for money-changing operations, immutable transaction references, webhook verification, explicit currency/minor-unit handling, reconciliation, failure/retry states, refunds/disputes modeling, and auditability. Never store card security codes or log sensitive payment payloads.
