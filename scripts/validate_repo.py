#!/usr/bin/env python3
"""Validate repository manifests, schemas and module shape without third-party dependencies."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
SOURCE=Path(__file__).resolve().parents[1]

def fail(msg,errors): errors.append(msg)
def main():
    errors=[]
    for p in (SOURCE/"schema").glob("*.json"):
        try: json.loads(p.read_text())
        except Exception as e: fail(f"invalid JSON schema {p.name}: {e}",errors)
    for folder,entry in [(SOURCE/"skills","SKILL.md"),(SOURCE/"packs","PACK.md")]:
        if folder.exists():
            for d in folder.iterdir():
                if d.is_dir() and not (d/entry).exists(): fail(f"{d.relative_to(SOURCE)} missing {entry}",errors)
    for mf,base,entry in [(SOURCE/"skills/manifest.json",SOURCE/"skills","SKILL.md"),(SOURCE/"packs/manifest.json",SOURCE/"packs","PACK.md")]:
        if mf.exists():
            try: data=json.loads(mf.read_text())
            except Exception as e: fail(f"invalid {mf.name}: {e}",errors); continue
            for name in data.get("modules",{}):
                if not (base/name/entry).exists(): fail(f"manifest references missing module {name}",errors)
    template=SOURCE/"templates/base"
    for f in ["AGENTS.md","agentic.yaml","PRODUCT.md","ARCHITECTURE.md","DESIGN.md","REFERENCE.md","SECURITY.md"]:
        if not (template/f).exists(): fail(f"base template missing {f}",errors)
    manifest=(ROOT/"agentic.yaml") if (ROOT/"agentic.yaml").exists() else template/"agentic.yaml"
    text=manifest.read_text()
    for token in ["version:","project:","maturity:","packs:","agent:","forbidden:"]:
        if token not in text: fail(f"agentic manifest missing {token}",errors)
    result={"valid":not errors,"errors":errors,"target":str(ROOT)}; print(json.dumps(result,indent=2)); return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
