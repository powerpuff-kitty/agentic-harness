#!/usr/bin/env python3
"""Preserve structural checks and gate the current public documentation surface."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

from validate_public_surface import validate_public_surface

ROOT = Path(__file__).resolve().parents[2]
errors = validate_public_surface(ROOT)
if errors:
    print("Public surface validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

# The original structural validator is retained byte-for-byte in this module.
runpy.run_path(str(Path(__file__).with_name("_validate_catalog_structure.py")), run_name="__main__")
