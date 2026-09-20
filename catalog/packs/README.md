# Agentic Packs

Packs are composable domain/technical knowledge modules. They complement the core harness rather than replacing it.

A pack may define required knowledge, suggested docs, skills, evals, examples, and approval gates. Declare selected packs under `modules.packs` in `.agentic/manifest.yaml`; use the compatible CLI to compose their files and provenance. A manifest edit alone does not install content.

The [manifest](manifest.json) lists all available pack IDs and versions. Select packs relevant to the project and load them when the task touches that domain, following project policies and accepted truth.

The web-app, security-critical and library-sdk packs include decision tables, synthetic examples, anti-patterns and evidence checklists. Other packs remain starter guidance: selection does not certify comparable depth, implementation, enforcement or verification. Expand a starter only when a project needs its domain; do not create empty supporting documents to imply completeness.
