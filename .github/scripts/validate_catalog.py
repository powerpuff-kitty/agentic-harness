#!/usr/bin/env python3
"""Preserve structural checks and gate the current public documentation surface."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

from validate_public_surface import validate_public_surface
from validate_context_profiles import validate as validate_context_profiles
import json

ROOT = Path(__file__).resolve().parents[2]
errors = validate_public_surface(ROOT)
errors.extend(validate_context_profiles(ROOT, json.loads((ROOT / "catalog/context/profiles.v1.json").read_text())))
if errors:
    print("Public surface validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

# Structural checks include materialized variants and synthetic context examples.
runpy.run_path(str(Path(__file__).with_name("_validate_catalog_structure.py")), run_name="__main__")
