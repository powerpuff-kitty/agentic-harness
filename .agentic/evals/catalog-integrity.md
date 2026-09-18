# Catalog integrity evaluation

A passing catalog has valid schemas and JSON, complete materialized variant cores, valid pack/policy/profile/preset references, consistent format versions, no deprecated public source roots, no source metadata leakage into target files, and an understandable README map.

The same target-core structural checks apply to the [filled synthetic context fixture](fixtures/context/reading-list/README.md). Its null source identities deliberately mean installation provenance is unresolved. A valid fixture is not evidence of CLI composition, working application behavior or native host delivery.

Run `python3 .github/scripts/measure_context.py` to measure authored variant/fixture file count, UTF-8 bytes, whitespace words and startup router/map/manifest size. Selected modules and task-specific reads add context; words are not model tokens. Minimal/full installed output and content preservation must be tested by the CLI before claiming reduced generated ceremony.
