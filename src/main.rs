use include_dir::{include_dir, Dir, DirEntry};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};

static TEMPLATES: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/templates");
static PACKS: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/packs");
static SKILLS: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/skills");
static PRESETS: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/presets");

const SKIP: &[&str] = &[".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt", "target", ".venv", "venv", "coverage"];
const CODE_EXT: &[&str] = &["py","js","mjs","cjs","ts","tsx","jsx","vue","rs","go","java","kt","swift","rb","php","cs","c","cc","cpp","h","hpp"];
const MANIFESTS: &[&str] = &["package.json","pyproject.toml","requirements.txt","Cargo.toml","go.mod","pom.xml","build.gradle","Gemfile","composer.json"];
const LOCKFILES: &[&str] = &["package-lock.json","pnpm-lock.yaml","yarn.lock","bun.lock","bun.lockb","uv.lock","poetry.lock","Cargo.lock","go.sum","Gemfile.lock","composer.lock"];

fn die(msg: impl AsRef<str>) -> ! { eprintln!("{}", msg.as_ref()); std::process::exit(2) }
fn pretty(v: Value) { println!("{}", serde_json::to_string_pretty(&v).unwrap()) }

fn embedded_text(dir: &Dir<'_>, path: &str) -> Option<String> {
    dir.get_file(path).and_then(|f| f.contents_utf8()).map(str::to_string)
}
fn embedded_dir<'a>(dir: &'a Dir<'a>, path: &str) -> Option<&'a Dir<'a>> { dir.get_dir(path) }

fn copy_embedded(dir: &Dir<'_>, dst: &Path, preserve: bool) -> io::Result<Vec<String>> {
    fn walk(dir: &Dir<'_>, root: &Path, dst: &Path, preserve: bool, out: &mut Vec<String>) -> io::Result<()> {
        for entry in dir.entries() {
            match entry {
                DirEntry::Dir(d) => walk(d, root, dst, preserve, out)?,
                DirEntry::File(f) => {
                    let rel = f.path().strip_prefix(root).unwrap_or(f.path());
                    let target = dst.join(rel);
                    if preserve && target.exists() { continue; }
                    if let Some(parent) = target.parent() { fs::create_dir_all(parent)?; }
                    fs::write(&target, f.contents())?;
                    out.push(rel.to_string_lossy().into_owned());
                }
            }
        }
        Ok(())
    }
    let mut out = vec![];
    walk(dir, dir.path(), dst, preserve, &mut out)?;
    Ok(out)
}

#[derive(Default)]
struct ComposeOpts { template: String, preset: Option<String>, packs: Vec<String>, skills: Vec<String>, name: Option<String>, maturity: Option<String> }

fn template_meta(name: &str) -> Value {
    let p = format!("{name}/template.json");
    serde_json::from_str(&embedded_text(&TEMPLATES, &p).unwrap_or_else(|| die(format!("unknown template: {name}")))).unwrap_or_else(|e| die(format!("invalid {p}: {e}")))
}
fn template_chain(mut name: String) -> Vec<String> {
    let mut chain = vec![]; let mut seen = BTreeSet::new();
    loop {
        if !seen.insert(name.clone()) { die("template inheritance cycle") }
        let meta = template_meta(&name); chain.push(name.clone());
        match meta.get("extends").and_then(Value::as_str) { Some(parent) => name = parent.to_string(), None => break }
    }
    chain.reverse(); chain
}
fn resolve(mut o: ComposeOpts) -> (Vec<String>, ComposeOpts) {
    if let Some(preset) = &o.preset {
        let p = format!("{preset}.json");
        let data: Value = serde_json::from_str(&embedded_text(&PRESETS, &p).unwrap_or_else(|| die(format!("unknown preset: {preset}")))).unwrap();
        if let Some(t) = data.get("template").and_then(Value::as_str) { o.template=t.into(); }
        if o.packs.is_empty() { o.packs = data.get("packs").and_then(Value::as_array).map(|a| a.iter().filter_map(Value::as_str).map(str::to_string).collect()).unwrap_or_default(); }
        if o.skills.is_empty() { o.skills = data.get("skills").and_then(Value::as_array).map(|a| a.iter().filter_map(Value::as_str).map(str::to_string).collect()).unwrap_or_default(); }
    }
    let chain=template_chain(o.template.clone()); let leaf=template_meta(chain.last().unwrap());
    if o.packs.is_empty() { o.packs=leaf.get("default_packs").and_then(Value::as_array).map(|a| a.iter().filter_map(Value::as_str).map(str::to_string).collect()).unwrap_or_default(); }
    if o.skills.is_empty() { o.skills=leaf.get("default_skills").and_then(Value::as_array).map(|a| a.iter().filter_map(Value::as_str).map(str::to_string).collect()).unwrap_or_default(); }
    (chain,o)
}
fn patch_manifest(path:&Path,name:Option<&str>,maturity:Option<&str>,packs:&[String]) -> io::Result<()> {
    if !path.exists(){return Ok(())} let mut text=fs::read_to_string(path)?;
    if let Some(name)=name { let mut done=false; text=text.lines().map(|l| { if !done && l.trim_start().starts_with("name:"){done=true; format!("{}name: {}", &l[..l.len()-l.trim_start().len()], name)} else {l.to_string()} }).collect::<Vec<_>>().join("\n")+"\n"; }
    if let Some(m)=maturity { for old in ["prototype","startup","production","critical"] { let needle=format!("maturity: {old}"); if text.contains(&needle){text=text.replacen(&needle,&format!("maturity: {m}"),1);break} } }
    if !packs.is_empty(){ let mut out=vec![]; let mut inside=false; for l in text.lines(){ if l=="packs:"{out.push("packs:".to_string());out.extend(packs.iter().map(|p|format!("  - {p}")));inside=true;continue} if inside&&l.starts_with("  - "){continue} if inside&&!l.starts_with(' '){inside=false} out.push(l.to_string()); } text=out.join("\n")+"\n"; }
    fs::write(path,text)
}
fn install_modules(target:&Path, packs:&[String], skills:&[String]) -> io::Result<()> {
    for (kind,names,root,dstroot) in [("pack",packs,&PACKS,target.join(".agentic/packs")),("skill",skills,&SKILLS,target.join(".agents/skills"))] {
        for name in names { let d=embedded_dir(root,name).unwrap_or_else(||die(format!("unknown {kind}: {name}"))); let dst=dstroot.join(name); if dst.exists(){fs::remove_dir_all(&dst)?} fs::create_dir_all(&dst)?; copy_embedded(d,&dst,false)?; }
    } Ok(())
}
fn compose(target:&Path,o:ComposeOpts,preserve:bool)->io::Result<Value>{
    let (chain,o)=resolve(o); let mut created=vec![]; let base=embedded_dir(&TEMPLATES,"base").unwrap(); created.extend(copy_embedded(base,target,true)?);
    for name in chain.iter().filter(|n|n.as_str()!="base") { if let Some(overlay)=embedded_dir(&TEMPLATES,&format!("{name}/overlay")){ created.extend(copy_embedded(overlay,target,preserve)?); } }
    install_modules(target,&o.packs,&o.skills)?; patch_manifest(&target.join("agentic.yaml"),o.name.as_deref(),o.maturity.as_deref(),&o.packs)?;
    Ok(json!({"templates":chain,"preset":o.preset,"created":created,"packs":o.packs,"skills":o.skills}))
}

fn all_files(root:&Path)->Vec<PathBuf>{ fn walk(p:&Path,root:&Path,out:&mut Vec<PathBuf>){ if let Ok(rd)=fs::read_dir(p){for e in rd.flatten(){let path=e.path();let rel=path.strip_prefix(root).unwrap_or(&path);if rel.components().any(|c|SKIP.contains(&c.as_os_str().to_string_lossy().as_ref())){continue} if path.is_dir(){walk(&path,root,out)}else{out.push(path)}}}} let mut v=vec![];walk(root,root,&mut v);v }
fn is_test_path(s:&str)->bool{ let x=s.to_ascii_lowercase(); ["test","tests","spec","specs"].iter().any(|n|x.split(|c:char|"/_.-".contains(c)).any(|p|p==*n)) }
fn clamp(v:i64)->i64{v.max(0).min(100)}
fn codebase_audit(root:&Path)->Value{
    let files=all_files(root); let mut code=0;let mut loc=0i64;let mut large=vec![];let mut todos=0i64;let mut tests=0;let mut workflows=0;let mut docs=0;let mut manifests=vec![];let mut locks=vec![];let mut security=false;let mut agent=false;let mut ops=false;
    for p in &files { let rel=p.strip_prefix(root).unwrap_or(p).to_string_lossy().replace('\\',"/");let name=p.file_name().unwrap_or_default().to_string_lossy();let ext=p.extension().unwrap_or_default().to_string_lossy(); if ["md","mdx","rst","txt"].contains(&ext.as_ref()){docs+=1} if MANIFESTS.contains(&name.as_ref()){manifests.push(rel.clone())} if LOCKFILES.contains(&name.as_ref()){locks.push(rel.clone())} if is_test_path(&rel){tests+=1} if rel.starts_with(".github/workflows/"){workflows+=1} if rel.to_ascii_lowercase().contains("security"){security=true} if ["AGENTS.md","CLAUDE.md","GEMINI.md","agentic.yaml"].contains(&name.as_ref())||rel.contains("/skills/"){agent=true} if ["runbook","deploy","rollback","observability","monitor","incident","backup"].iter().any(|x|rel.to_ascii_lowercase().contains(x)){ops=true}
        if CODE_EXT.contains(&ext.as_ref()){code+=1;if let Ok(t)=fs::read_to_string(p){let n=t.lines().count() as i64;loc+=n;if n>800{large.push(rel.clone())} for m in ["TODO","FIXME","HACK","XXX"]{todos+=t.matches(m).count() as i64}}}
    }
    let ci=workflows>0;let has_tests=tests>0;let has_docs=docs>0||root.join("README.md").exists()||root.join("docs").exists();let has_lock=manifests.is_empty()||!locks.is_empty();
    let mut s=BTreeMap::new();s.insert("code_quality",clamp(75-5*large.len() as i64-todos.min(15)));s.insert("maintainability",clamp(72-4*large.len() as i64+if has_docs{5}else{-8}));s.insert("architecture",if root.join("ARCHITECTURE.md").exists()||root.join("docs/architecture").exists(){78}else{58});s.insert("testing",if has_tests&&ci{78}else if has_tests{62}else{38});s.insert("security",clamp((if security{72}else{48})+if ci{6}else{-5}));s.insert("performance",if root.join("docs/performance.md").exists()||root.join("benchmarks").exists(){70}else{55});s.insert("dependency_health",clamp((if has_lock{78}else{58})+if ci{4}else{0}));s.insert("documentation",if has_docs{82}else{42});s.insert("agent_docs",if agent{86}else{50});s.insert("operations",if ops&&ci{76}else if ci{60}else{40});
    let weights=[("code_quality",12),("maintainability",12),("architecture",12),("testing",12),("security",16),("performance",6),("dependency_health",8),("documentation",8),("agent_docs",7),("operations",7)];let overall=weights.iter().map(|(k,w)|s[*k]*w).sum::<i64>()/100;
    let mut f=vec![]; if !has_tests{f.push(json!({"severity":"high","dimension":"testing","message":"No tests/spec files detected."}))} if !ci{f.push(json!({"severity":"high","dimension":"operations","message":"No GitHub Actions workflow detected."}))} if !security{f.push(json!({"severity":"high","dimension":"security","message":"No security guidance/configuration detected."}))} if !ops{f.push(json!({"severity":"medium","dimension":"operations","message":"No deployment/rollback/runbook/observability material detected."}))}
    json!({"overall":overall,"target_maturity":"unknown","scores":s,"readiness":{"prototype":clamp(overall+15),"startup":clamp(overall+if has_tests&&ci{3}else{-8}),"production":clamp(overall-if has_tests&&ci&&security&&ops{8}else{20}),"critical":clamp(overall-if has_tests&&ci&&security&&ops{22}else{35})},"profile":{"root":root,"files":files.len(),"code_files":code,"code_loc":loc,"doc_files":docs,"tests_detected":tests,"workflows":workflows,"manifests":manifests,"lockfiles":locks,"large_code_files":large,"todo_markers":todos},"findings":f,"checks":{"performed":["repository structure","file/LOC scan","test/CI presence","docs/security/agent/operations presence","manifest/lockfile presence"],"not_checked":["build execution","test execution","coverage","dependency vulnerabilities","runtime performance","branch protection","deployment environment"]}})
}
fn secret_scan(root:&Path)->Value{ let mut findings=vec![];for p in all_files(root){if fs::metadata(&p).map(|m|m.len()>1_000_000).unwrap_or(true){continue}if let Ok(t)=fs::read_to_string(&p){for (typ,needle) in [("private_key","-----BEGIN PRIVATE KEY-----"),("private_key","-----BEGIN RSA PRIVATE KEY-----"),("private_key","-----BEGIN OPENSSH PRIVATE KEY-----"),("aws_access_key","AKIA")]{for (i,l) in t.lines().enumerate(){if l.contains(needle){findings.push(json!({"severity":"high","type":typ,"path":p.strip_prefix(root).unwrap_or(&p),"line":i+1}))}}}}}json!({"passed":findings.is_empty(),"findings":findings,"note":"high-signal baseline only; use platform secret scanning/gitleaks for production"}) }
fn validate_repo(root:&Path)->Value{let mut errors=vec![];for f in ["AGENTS.md","agentic.yaml","PRODUCT.md","ARCHITECTURE.md","DESIGN.md","REFERENCE.md","SECURITY.md"]{if !root.join(f).exists()&&!TEMPLATES.get_file(format!("base/{f}")).is_some(){errors.push(format!("base template missing {f}"))}}let manifest=if root.join("agentic.yaml").exists(){fs::read_to_string(root.join("agentic.yaml")).unwrap_or_default()}else{embedded_text(&TEMPLATES,"base/agentic.yaml").unwrap_or_default()};for token in ["version:","project:","maturity:","packs:","agent:","forbidden:"]{if !manifest.contains(token){errors.push(format!("agentic manifest missing {token}"))}}json!({"valid":errors.is_empty(),"errors":errors,"target":root})}
fn harness_audit(root:&Path)->Value{let core=["AGENTS.md","agentic.yaml","PRODUCT.md","ARCHITECTURE.md","DESIGN.md","REFERENCE.md","SECURITY.md","docs/decisions","docs/plans","evals","examples"];let rec=["docs/testing","docs/operations","docs/research","docs/tasks"];let present:Vec<_>=core.iter().filter(|p|root.join(p).exists()).cloned().collect();let missing:Vec<_>=core.iter().filter(|p|!root.join(p).exists()).cloned().collect();let weak:Vec<_>=rec.iter().filter(|p|!root.join(p).exists()).cloned().collect();let score=clamp((100*present.len() as i64/core.len() as i64)-2*weak.len() as i64);json!({"target":root,"score":score,"present":present,"weak":weak,"missing":missing,"conflicting":[],"recommendations":missing.iter().chain(weak.iter()).map(|p|format!("Add or resolve {p}")).collect::<Vec<_>>()})}

fn usage(prog:&str){println!("Agentic Harness\n\nusage: {prog} <command> [options]\n\ncommands:\n  init TARGET [--template NAME] [--preset NAME] [--pack NAME] [--skill NAME]\n  upgrade TARGET [same options]\n  audit [TARGET]\n  compare BEFORE.json AFTER.json\n  gate AUDIT.json [--min-overall N] [--min-score dimension=N]\n  validate [TARGET]\n  security-scan [TARGET]\n  harness-audit [TARGET]")}
fn parse_compose(args:&[String])->(PathBuf,ComposeOpts,bool){if args.is_empty(){die("missing target")}let target=PathBuf::from(&args[0]);let mut o=ComposeOpts{template:"base".into(),..Default::default()};let mut allow=false;let mut i=1;while i<args.len(){match args[i].as_str(){"--template"=>{i+=1;o.template=args.get(i).cloned().unwrap_or_else(||die("--template requires value"))},"--preset"=>{i+=1;o.preset=args.get(i).cloned()},"--pack"=>{i+=1;o.packs.push(args.get(i).cloned().unwrap_or_else(||die("--pack requires value")))},"--skill"=>{i+=1;o.skills.push(args.get(i).cloned().unwrap_or_else(||die("--skill requires value")))},"--name"=>{i+=1;o.name=args.get(i).cloned()},"--maturity"=>{i+=1;o.maturity=args.get(i).cloned()},"--allow-existing"=>allow=true,x=>die(format!("unknown option: {x}"))}i+=1}(target,o,allow)}

fn main(){let argv:Vec<String>=env::args().collect();let prog=Path::new(&argv[0]).file_name().and_then(|x|x.to_str()).unwrap_or("ah");if argv.len()<2||["-h","--help"].contains(&argv[1].as_str()){usage(prog);return}let code=match argv[1].as_str(){"init"=>{let(t,o,allow)=parse_compose(&argv[2..]);fs::create_dir_all(&t).unwrap();if !allow&&fs::read_dir(&t).map(|mut x|x.next().is_some()).unwrap_or(false){die("target is not empty; use --allow-existing or upgrade")}let mut r=compose(&t,o,false).unwrap();r["mode"]=json!("INIT");r["target"]=json!(t);pretty(r);0},"upgrade"=>{let(t,o,_)=parse_compose(&argv[2..]);if !t.exists(){die("target does not exist")}let mut r=compose(&t,o,true).unwrap();r["mode"]=json!("UPGRADE");r["target"]=json!(t);r["preserved_existing"]=json!(true);pretty(r);0},"audit"=>{let p=PathBuf::from(argv.get(2).map(String::as_str).unwrap_or("."));let r=codebase_audit(&p);let fail=r["findings"].as_array().unwrap().iter().any(|f|matches!(f["severity"].as_str(),Some("high"|"critical")));pretty(r);if fail{1}else{0}},"security-scan"=>{let p=PathBuf::from(argv.get(2).map(String::as_str).unwrap_or("."));let r=secret_scan(&p);let pass=r["passed"].as_bool().unwrap_or(false);pretty(r);if pass{0}else{1}},"validate"=>{let p=PathBuf::from(argv.get(2).map(String::as_str).unwrap_or("."));let r=validate_repo(&p);let pass=r["valid"].as_bool().unwrap_or(false);pretty(r);if pass{0}else{1}},"harness-audit"=>{let p=PathBuf::from(argv.get(2).map(String::as_str).unwrap_or("templates/base"));let r=harness_audit(&p);let fail=!r["missing"].as_array().unwrap().is_empty();pretty(r);if fail{1}else{0}},"compare"=>{if argv.len()<4{die("compare requires before and after JSON")}let b:Value=serde_json::from_str(&fs::read_to_string(&argv[2]).unwrap()).unwrap();let a:Value=serde_json::from_str(&fs::read_to_string(&argv[3]).unwrap()).unwrap();let mut scores=serde_json::Map::new();let keys:BTreeSet<_>=b["scores"].as_object().into_iter().flat_map(|m|m.keys().cloned()).chain(a["scores"].as_object().into_iter().flat_map(|m|m.keys().cloned())).collect();for k in keys{let x=b["scores"][&k].as_i64();let y=a["scores"][&k].as_i64();scores.insert(k,json!({"before":x,"after":y,"delta":match(x,y){(Some(x),Some(y))=>Some(y-x),_=>None}}));}pretty(json!({"overall":{"before":b["overall"],"after":a["overall"],"delta":a["overall"].as_i64().unwrap_or(0)-b["overall"].as_i64().unwrap_or(0)},"scores":scores}));0},"gate"=>{if argv.len()<3{die("gate requires audit JSON")}let d:Value=serde_json::from_str(&fs::read_to_string(&argv[2]).unwrap()).unwrap();let mut min=0f64;let mut req=vec![];let mut i=3;while i<argv.len(){match argv[i].as_str(){"--min-overall"=>{i+=1;min=argv[i].parse().unwrap_or(0.0)},"--min-score"=>{i+=1;req.push(argv[i].clone())},x=>die(format!("unknown option: {x}"))}i+=1}let mut failures=vec![];if d["overall"].as_f64().unwrap_or(0.0)<min{failures.push(format!("overall {} < {min}",d["overall"]))}for x in req{if let Some((n,v))=x.split_once('='){let v:f64=v.parse().unwrap_or(0.0);let a=d["scores"][n].as_f64();if a.map(|a|a<v).unwrap_or(true){failures.push(format!("{n} {:?} < {v}",a))}}}let ok=failures.is_empty();pretty(json!({"passed":ok,"failures":failures}));if ok{0}else{1}},_=>{usage(prog);2}};std::process::exit(code)}

#[cfg(test)] mod tests { use super::*; #[test] fn embedded_base_exists(){assert!(TEMPLATES.get_file("base/AGENTS.md").is_some())} #[test] fn chain_works(){assert_eq!(template_chain("web-app".into()).first().unwrap(),"base")} #[test] fn secret_fixture(){let p=env::temp_dir().join(format!("ah-test-{}",std::process::id()));let _=fs::remove_dir_all(&p);fs::create_dir_all(&p).unwrap();fs::write(p.join("x"),"-----BEGIN PRIVATE KEY-----").unwrap();assert!(!secret_scan(&p)["passed"].as_bool().unwrap());let _=fs::remove_dir_all(p);} }
