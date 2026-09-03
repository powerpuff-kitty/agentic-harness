import os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class AliasTests(unittest.TestCase):
 def test_direct_python_help_defaults_to_ah(self):
  r=subprocess.run([sys.executable,str(ROOT/"scripts/agentic.py"),"--help"],text=True,capture_output=True)
  self.assertEqual(r.returncode,0,r.stderr)
  self.assertIn("usage: ah",r.stdout)

 def test_ah_launcher_help(self):
  r=subprocess.run([str(ROOT/"ah"),"--help"],text=True,capture_output=True)
  self.assertEqual(r.returncode,0,r.stderr)
  self.assertIn("usage: ah",r.stdout)

 def test_install_custom_alias(self):
  with tempfile.TemporaryDirectory() as td:
   r=subprocess.run([str(ROOT/"install.sh"),"--prefix",td,"--command","agentic-test"],text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stderr)
   alias=Path(td)/"bin/agentic-test"
   self.assertTrue(alias.exists())
   h=subprocess.run([str(alias),"--help"],text=True,capture_output=True)
   self.assertEqual(h.returncode,0,h.stderr)
   self.assertIn("usage: agentic-test",h.stdout)

if __name__=="__main__": unittest.main()
