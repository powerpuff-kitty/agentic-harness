#!/usr/bin/env python3
"""Agentic Repo Harness deterministic CLI."""
from __future__ import annotations
import argparse, json, shutil, sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SOURCE_ROOT / "templates" / "base"
PACKS = SOURCE_ROOT / "packs"
SKILLS = SOURCE_ROOT / "skills"


def copy_missing(src: Path, dst: Path) -> list[str]:
    created=[]
    for p in src.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(src); out=dst/rel
        if out.exists(): continue
        out.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p,out); created.append(str(rel))
    return created


def patch_manifest(path: Path, name: str|None, maturity: str|None, packs: list[str]) -> None:
    if not path.exists(): return
    text=path.read_text()
    if name:
        lines=text.splitlines()
        for i,line in enumerate(lines):
            if line.strip().startswith("name:"):
                indent=line[:len(line)-len(line.lstrip())]; lines[i]=f"{indent}name: {name}"; break
        text="\n".join(lines)+"\n"
    if maturity:
        text=text.replace("maturity: prototype",f"maturity: {maturity}",1)
    if packs:
        lines=text.splitlines(); out=[]; in_packs=False
        for line in lines:
            if line.startswith("packs:"):
                out.append("packs:"); out.extend(f"  - {p}" for p in packs); in_packs=True; continue
            if in_packs and line.startswith("  - "): continue
            if in_packs and line and not line.startswith(" "): in_packs=False
            out.append(line)
        text="\n".join(out)+"\n"
    path.write_text(text)


def install_modules(target: Path, packs: list[str], skills: list[str]) -> None:
    for name in packs:
        src=PACKS/name
        if not src.exists(): raise SystemExit(f"unknown pack: {name}")
        dst=target/".agentic"/"packs"/name
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src,dst)
    for name in skills:
        src=SKILLS/name
        if not src.exists(): raise SystemExit(f"unknown skill: {name}")
        dst=target/".agents"/"skills"/name
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src,dst)


def cmd_init(a):
    target=Path(a.target).resolve(); target.mkdir(parents=True,exist_ok=True)
    if any(target.iterdir()) and not a.allow_existing:
        raise SystemExit("target is not empty; use --allow-existing or UPGRADE")
    created=copy_missing(TEMPLATE,target)
    packs=a.pack or ["web-app"]; skills=a.skill or ["agentic-app","codebase-audit","security-review"]
    install_modules(target,packs,skills); patch_manifest(target/"agentic.yaml",a.name,a.maturity,packs)
    print(json.dumps({"mode":"INIT","target":str(target),"created":created,"packs":packs,"skills":skills},indent=2))


def cmd_upgrade(a):
    target=Path(a.target).resolve()
    if not target.exists(): raise SystemExit("target does not exist")
    created=copy_missing(TEMPLATE,target); packs=a.pack or []; skills=a.skill or []
    install_modules(target,packs,skills)
    if packs or a.name or a.maturity: patch_manifest(target/"agentic.yaml",a.name,a.maturity,packs)
    print(json.dumps({"mode":"UPGRADE","target":str(target),"created":created,"packs":packs,"skills":skills,"preserved_existing":True},indent=2))


def load_audit(path: str) -> dict:
    return json.loads(Path(path).read_text())


def cmd_audit(a):
    sys.path.insert(0,str(SOURCE_ROOT/"scripts")); import codebase_audit
    result=codebase_audit.audit(Path(a.target).resolve()); print(json.dumps(result,indent=2))
    return 1 if any(f.get("severity") in {"critical","high"} for f in result.get("findings",[])) else 0


def cmd_compare(a):
    before,after=load_audit(a.before),load_audit(a.after)
    keys=sorted(set(before.get("scores",{}))|set(after.get("scores",{})))
    result={"overall":{"before":before.get("overall"),"after":after.get("overall"),"delta":(after.get("overall",0)-before.get("overall",0))},"scores":{}}
    for k in keys:
        b,e=before.get("scores",{}).get(k),after.get("scores",{}).get(k)
        result["scores"][k]={"before":b,"after":e,"delta":None if b is None or e is None else e-b}
    print(json.dumps(result,indent=2))


def cmd_gate(a):
    data=load_audit(a.audit); failures=[]
    if data.get("overall",0)<a.min_overall: failures.append(f"overall {data.get('overall')} < {a.min_overall}")
    for item in a.min_score:
        name,value=item.split("=",1); actual=data.get("scores",{}).get(name)
        if actual is None or actual<float(value): failures.append(f"{name} {actual} < {value}")
    print(json.dumps({"passed":not failures,"failures":failures},indent=2)); return 1 if failures else 0


def parser():
    p=argparse.ArgumentParser(prog="arh",description="Agentic Repo Harness: compose, upgrade, audit, compare, and gate agent-native repositories")
    s=p.add_subparsers(dest="command",required=True)
    for name,func in [("init",cmd_init),("upgrade",cmd_upgrade)]:
        q=s.add_parser(name); q.add_argument("target"); q.add_argument("--name"); q.add_argument("--maturity",choices=["prototype","startup","production","critical"]); q.add_argument("--pack",action="append",default=[]); q.add_argument("--skill",action="append",default=[]); q.set_defaults(func=func)
        if name=="init": q.add_argument("--allow-existing",action="store_true")
    q=s.add_parser("audit"); q.add_argument("target",nargs="?",default="."); q.set_defaults(func=cmd_audit)
    q=s.add_parser("compare"); q.add_argument("before"); q.add_argument("after"); q.set_defaults(func=cmd_compare)
    q=s.add_parser("gate"); q.add_argument("audit"); q.add_argument("--min-overall",type=float,default=0); q.add_argument("--min-score",action="append",default=[],metavar="DIMENSION=N"); q.set_defaults(func=cmd_gate)
    return p


def main():
    a=parser().parse_args(); return a.func(a) or 0

if __name__=="__main__": raise SystemExit(main())
