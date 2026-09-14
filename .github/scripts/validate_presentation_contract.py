#!/usr/bin/env python3
"""Check vocabulary/schema/example coherence without executing application code.

This is not JSON Schema evaluation or asset-byte verification; run the separate
schema conformance cases and the consumer's semantic/file/runtime checks as well.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def validate_contract(root: Path = ROOT) -> None:
    def read(relative: str):
        path = root / relative
        if path.is_symlink() or path.stat().st_size > 262144:
            raise ValueError("Invalid presentation contract input")
        return json.loads(path.read_text(encoding="utf-8"))
    pack = "catalog/packs/project-presentation/"
    vocabulary = read(pack + "layouts.json")
    schema = read("catalog/schema/project-visuals.schema.json")
    example = read(pack + "examples/visuals.json")
    manifest = read("catalog/packs/manifest.json")
    if manifest["modules"]["project-presentation"]["version"] != "0.1.0":
        raise ValueError("Unexpected presentation pack version")
    props = schema["$defs"]["section"]["properties"]
    pairs = [("layouts", "layout"), ("purposes", "purpose"), ("surfaces", "surface"),
             ("frames", "frame"), ("corners", "corners"), ("spacing", "spacing")]
    for source, target in pairs:
        if set(vocabulary[source]) != set(props[target]["enum"]):
            raise ValueError("Presentation vocabulary/schema drift")
    if set(vocabulary["ratios"]) != set(schema["$defs"]["item"]["properties"]["ratio"]["enum"]):
        raise ValueError("Presentation ratio/schema drift")
    branches = {rule["if"]["properties"]["layout"]["const"]: rule["then"]["properties"]["items"]
                for rule in schema["$defs"]["section"]["allOf"]}
    if set(branches) != set(vocabulary["layouts"]):
        raise ValueError("Incomplete layout cardinality branches")
    for name, layout in vocabulary["layouts"].items():
        if len(layout["spans"]) != layout["items"] or any(type(n) is not int or not 1 <= n <= 12 for n in layout["spans"]):
            raise ValueError("Invalid grid spans")
        if branches[name] != {"minItems": layout["items"], "maxItems": layout["items"]}:
            raise ValueError("Layout cardinality drift")
    if vocabulary["responsive"] != {"columns": 12, "collapseBelowRem": 48, "smallScreenColumns": 1, "order": "source"}:
        raise ValueError("Unreviewed responsive contract")
    for key, collection in [("surface", "surfaces"), ("frame", "frames"), ("corners", "corners"), ("spacing", "spacing"), ("ratio", "ratios")]:
        if vocabulary["defaults"][key] not in vocabulary[collection]:
            raise ValueError("Invalid presentation default")
    if vocabulary["defaults"]["fit"] != "contain":
        raise ValueError("Unsafe default image fit")
    used = set()
    for section in example["sections"]:
        if len(section["items"]) != vocabulary["layouts"][section["layout"]]["items"]:
            raise ValueError("Invalid synthetic scene size")
        for item in section["items"]:
            if item["asset"] not in example["assets"]:
                raise ValueError("Unresolved synthetic asset")
            used.add(item["asset"])
    if used != set(example["assets"]):
        raise ValueError("Unused synthetic asset")
    for file in ["PACK.md", "CONTENT.md", "LAYOUT.md", "EXPORT.md", "templates/PRESENTATION.md"]:
        if not (root / pack / file).is_file():
            raise ValueError("Missing presentation pack file")
    print("Presentation vocabulary, schema and example coherence passed; not runtime or asset approval.")

if __name__ == "__main__":
    validate_contract()
