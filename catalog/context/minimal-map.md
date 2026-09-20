# Agentic project context

Start here and at `manifest.yaml`, then load only context relevant to the task. Paths below are relative to this directory.

| Path | Read when |
| --- | --- |
| `manifest.yaml` | Starting a task; inspect selected modules, routes and declared permissions |
| `lock.json` | Reproducing installation or checking source/checksum provenance |
{{routes}}
{{modules}}

The minimal context profile omits empty optional sections. Add references, supporting docs, plans, tasks or evals when useful content exists, and update the corresponding manifest route and this map. Select native host delivery separately through supported adapter commands.

Precedence: installed mandatory policies; current accepted project truth; accepted ADRs; packs; skills; task prompts. ADRs explain durable choices and do not replace current truth.

Structure installed, project configured, checks configured and behavior verified are independent claims. Template prompts are unresolved decisions, not accepted project facts. Installed instructions and permission declarations do not prove delivery, execution or enforcement. State missing evidence explicitly.
