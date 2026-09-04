# Migration safety evaluation

A passing migration proves dry-run is non-writing, identical duplicates are recognized, conflicting canonical files stop apply, backups are created when requested, sources are removed only after verified writes, rerunning migration is idempotent, and the resulting project passes validation.
