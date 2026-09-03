# Analytics Pack

Use for products that measure user behavior, funnels, retention, activation, conversion, and product outcomes.

## Constraints
- Define events from product questions, not from available UI clicks.
- Maintain an event dictionary with owner, trigger, properties, and privacy classification.
- Avoid collecting secrets, raw credentials, or unnecessary personal data.
- Separate product analytics from operational telemetry.
- Require consent and retention rules where applicable.

## Expected artifacts
`docs/analytics/events.md`, KPI definitions, funnel definitions, experiment conventions, and analytics validation tests when analytics is enabled.
