#!/usr/bin/env python3
"""High-signal repository secret scan. Not a replacement for a dedicated scanner."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
SKIP={".git","node_modules","vendor","dist","build","target",".venv","venv"}
PATTERNS={
 "private_key":re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
 "github_token":re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
 "aws_access_key":re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
 "generic_bearer":re.compile(r"(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9._-]{24,}"),
}
def main():
 findings=[]
 for p in ROOT.rglob("*"):
  if not p.is_file() or any(part in SKIP for part in p.parts): continue
  try:
   if p.stat().st_size>1_000_000: continue
   text=p.read_text(errors="ignore")
  except OSError: continue
  for name,rx in PATTERNS.items():
   for m in rx.finditer(text):
    line=text.count("\n",0,m.start())+1; findings.append({"severity":"high","type":name,"path":str(p.relative_to(ROOT)),"line":line})
 result={"passed":not findings,"findings":findings,"note":"high-signal baseline only; use platform secret scanning/gitleaks for production"}; print(json.dumps(result,indent=2)); return 1 if findings else 0
if __name__=="__main__": raise SystemExit(main())
