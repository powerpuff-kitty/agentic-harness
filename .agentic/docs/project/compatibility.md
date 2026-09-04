# Compatibility

The target filesystem format, manifest, lockfile, variant metadata, policy/pack contracts, audit output, and CLI commands are versioned independently where useful. During beta, additive fields remain preferred; incompatible moves require an explicit migration path and legacy read support for at least one minor release when practical.
