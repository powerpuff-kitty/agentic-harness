import subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ValidationTests(unittest.TestCase):
 def test_repo_validation(self):
  r=subprocess.run([sys.executable,str(ROOT/"scripts/validate_repo.py"),str(ROOT)],capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_secret_scanner_clean_fixture(self):
  with tempfile.TemporaryDirectory() as td:
   Path(td,"x.txt").write_text("TOKEN=placeholder")
   r=subprocess.run([sys.executable,str(ROOT/"scripts/security_scan.py"),td],capture_output=True); self.assertEqual(r.returncode,0)
 def test_secret_scanner_detects_private_key_header(self):
  with tempfile.TemporaryDirectory() as td:
   Path(td,"x.txt").write_text("-----BEGIN PRIVATE KEY-----")
   r=subprocess.run([sys.executable,str(ROOT/"scripts/security_scan.py"),td],capture_output=True); self.assertEqual(r.returncode,1)
if __name__=="__main__": unittest.main()
