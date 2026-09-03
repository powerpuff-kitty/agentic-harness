import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CLI=ROOT/"scripts/agentic.py"
class CliTests(unittest.TestCase):
 def test_init_composes_template_pack_and_skill(self):
  with tempfile.TemporaryDirectory() as td:
   target=Path(td)/"app"
   r=subprocess.run([sys.executable,str(CLI),"init",str(target),"--name","demo","--pack","web-app","--skill","security-review"],text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stderr); self.assertTrue((target/"AGENTS.md").exists()); self.assertTrue((target/".agentic/packs/web-app/PACK.md").exists()); self.assertTrue((target/".agents/skills/security-review/SKILL.md").exists()); self.assertIn("name: demo",(target/"agentic.yaml").read_text())
 def test_gate_fails_threshold(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"a.json"; p.write_text(json.dumps({"overall":70,"scores":{"security":60}}))
   r=subprocess.run([sys.executable,str(CLI),"gate",str(p),"--min-overall","80","--min-score","security=75"],capture_output=True)
   self.assertEqual(r.returncode,1)
if __name__=="__main__": unittest.main()
