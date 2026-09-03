#!/usr/bin/env python3
"""Agentic Harness deterministic CLI."""
from __future__ import annotations
import argparse, json, shutil, sys
from pathlib import Path
SOURCE_ROOT=Path(__file__).resolve().parents[1]; TEMPLATES=SOURCE_ROOT/"templates"; PACKS=SOURCE_ROOT/"packs"; SKILLS=SOURCE_ROOT/"skills"; PRESETS=SOURCE_ROOT/"presets"

def copy_missing(src,dst):
 created=[]
 if not src.exists(): return created
 for p in src.rglob("*"):
  if not p.is_file(): continue
  rel=p.relative_to(src); out=dst/rel
  if out.exists(): continue
  out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,out); created.append(str(rel))
 return created

def copy_overlay(src,dst):
 changed=[]
 if not src.exists(): return changed
 for p in src.rglob("*"):
  if not p.is_file(): continue
  rel=p.relative_to(src); out=dst/rel; out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,out); changed.append(str(rel))
 return changed

def template_chain(name):
 chain=[]; seen=set()
 while name:
  if name in seen: raise SystemExit("template inheritance cycle")
  seen.add(name); root=TEMPLATES/name; meta=root/"template.json"
  if not meta.exists(): raise SystemExit(f"unknown template: {name}")
  data=json.loads(meta.read_text()); chain.append((name,root,data)); name=data.get("extends")
 return list(reversed(chain))
def resolve(template,preset,packs,skills):
 if preset:
  path=PRESETS/f"{preset}.json"
  if not path.exists(): raise SystemExit(f"unknown preset: {preset}")
  data=json.loads(path.read_text()); template=data.get("template",template); packs=packs or data.get("packs",[]); skills=skills or data.get("skills",[])
 chain=template_chain(template); leaf=chain[-1][2]
 return chain, packs or leaf.get("default_packs",[]), skills or leaf.get("default_skills",[])
def patch_manifest(path,name,maturity,packs):
 if not path.exists(): return
 text=path.read_text(); lines=text.splitlines()
 if name:
  for i,line in enumerate(lines):
   if line.strip().startswith("name:"): lines[i]=line[:len(line)-len(line.lstrip())]+f"name: {name}"; break
 text="\n".join(lines)+"\n"
 if maturity:
  import re; text=re.sub(r"maturity:\s*(prototype|startup|production|critical)",f"maturity: {maturity}",text,count=1)
 if packs:
  lines=text.splitlines(); out=[]; inside=False
  for line in lines:
   if line.startswith("packs:"): out.append("packs:"); out.extend(f"  - {p}" for p in packs); inside=True; continue
   if inside and line.startswith("  - "): continue
   if inside and line and not line.startswith(" "): inside=False
   out.append(line)
  text="\n".join(out)+"\n"
 path.write_text(text)
def install_modules(target,packs,skills):
 for kind,names,root,dstdir in [("pack",packs,PACKS,target/".agentic/packs"),("skill",skills,SKILLS,target/".agents/skills")]:
  for name in names:
   src=root/name
   if not src.exists(): raise SystemExit(f"unknown {kind}: {name}")
   dst=dstdir/name
   if dst.exists(): shutil.rmtree(dst)
   dst.parent.mkdir(parents=True,exist_ok=True); shutil.copytree(src,dst)
def compose(target,template,preset,packs,skills,preserve):
 chain,packs,skills=resolve(template,preset,packs,skills); created=[]; overlaid=[]
 created+=copy_missing(TEMPLATES/"base",target)
 for name,root,_ in chain:
  if name=="base": continue
  if preserve: created+=copy_missing(root/"overlay",target)
  else: overlaid+=copy_overlay(root/"overlay",target)
 install_modules(target,packs,skills); return [x[0] for x in chain],packs,skills,created,overlaid
def cmd_init(a):
 target=Path(a.target).resolve(); target.mkdir(parents=True,exist_ok=True)
 if any(target.iterdir()) and not a.allow_existing: raise SystemExit("target is not empty; use --allow-existing or upgrade")
 chain,packs,skills,created,overlaid=compose(target,a.template,a.preset,a.pack,a.skill,False); patch_manifest(target/"agentic.yaml",a.name,a.maturity,packs)
 print(json.dumps({"mode":"INIT","target":str(target),"templates":chain,"preset":a.preset,"created":created,"overlaid":overlaid,"packs":packs,"skills":skills},indent=2))
def cmd_upgrade(a):
 target=Path(a.target).resolve()
 if not target.exists(): raise SystemExit("target does not exist")
 chain,packs,skills,created,_=compose(target,a.template,a.preset,a.pack,a.skill,True); patch_manifest(target/"agentic.yaml",a.name,a.maturity,packs)
 print(json.dumps({"mode":"UPGRADE","target":str(target),"templates":chain,"preset":a.preset,"created":created,"packs":packs,"skills":skills,"preserved_existing":True},indent=2))
def load_audit(p): return json.loads(Path(p).read_text())
def cmd_audit(a):
 sys.path.insert(0,str(SOURCE_ROOT/"scripts")); import codebase_audit; result=codebase_audit.audit(Path(a.target).resolve()); print(json.dumps(result,indent=2)); return 1 if any(f.get("severity") in {"critical","high"} for f in result.get("findings",[])) else 0
def cmd_compare(a):
 b,e=load_audit(a.before),load_audit(a.after); keys=sorted(set(b.get("scores",{}))|set(e.get("scores",{}))); r={"overall":{"before":b.get("overall"),"after":e.get("overall"),"delta":e.get("overall",0)-b.get("overall",0)},"scores":{}}
 for k in keys:
  x,y=b.get("scores",{}).get(k),e.get("scores",{}).get(k); r["scores"][k]={"before":x,"after":y,"delta":None if x is None or y is None else y-x}
 print(json.dumps(r,indent=2))
def cmd_gate(a):
 d=load_audit(a.audit); failures=[]
 if d.get("overall",0)<a.min_overall: failures.append(f"overall {d.get('overall')} < {a.min_overall}")
 for item in a.min_score:
  n,v=item.split("=",1); actual=d.get("scores",{}).get(n)
  if actual is None or actual<float(v): failures.append(f"{n} {actual} < {v}")
 print(json.dumps({"passed":not failures,"failures":failures},indent=2)); return 1 if failures else 0
def parser():
 invoked=Path(sys.argv[0]).name or "ah"
 if invoked in {"python","python3","agentic.py"}: invoked="ah"
 p=argparse.ArgumentParser(prog=invoked,description="Agentic Harness"); s=p.add_subparsers(dest="command",required=True)
 for n,f in [("init",cmd_init),("upgrade",cmd_upgrade)]:
  q=s.add_parser(n); q.add_argument("target"); q.add_argument("--template",default="base",choices=[p.name for p in TEMPLATES.iterdir() if p.is_dir()]); q.add_argument("--preset"); q.add_argument("--name"); q.add_argument("--maturity",choices=["prototype","startup","production","critical"]); q.add_argument("--pack",action="append",default=[]); q.add_argument("--skill",action="append",default=[]); q.set_defaults(func=f)
  if n=="init": q.add_argument("--allow-existing",action="store_true")
 q=s.add_parser("audit"); q.add_argument("target",nargs="?",default="."); q.set_defaults(func=cmd_audit)
 q=s.add_parser("compare"); q.add_argument("before"); q.add_argument("after"); q.set_defaults(func=cmd_compare)
 q=s.add_parser("gate"); q.add_argument("audit"); q.add_argument("--min-overall",type=float,default=0); q.add_argument("--min-score",action="append",default=[]); q.set_defaults(func=cmd_gate)
 return p
def main(): a=parser().parse_args(); return a.func(a) or 0
if __name__=="__main__": raise SystemExit(main())
