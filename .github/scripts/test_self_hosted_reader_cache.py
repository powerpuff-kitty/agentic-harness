"""Exercise copied production helpers against stale caches in disposable directories."""
import hashlib
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / '.agents/skills/agentic-improvement/scripts'


class SelfHostedReaderCache(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ('extract_context.py', 'evidence_snapshot.py'):
            shutil.copyfile(SCRIPTS / name, self.root / name)
        self.reader = self.root / 'evidence_snapshot.py'
        self.current_reader = self.reader.read_bytes()
        self.raw = b'necessary evidence\n'
        (self.root / 'source.txt').write_bytes(self.raw)
        self.command = [sys.executable, str(self.root / 'extract_context.py'), '--root', str(self.root),
                        '--span', 'source.txt', '1', '1', 'sha256:' + hashlib.sha256(self.raw).hexdigest()]

    def run_helper(self):
        return subprocess.run(self.command, capture_output=True, timeout=10)

    def inventory(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def seed_cache(self, mode, current=None):
        # Only a test-owned copy changes: stale hashing logic must not be used.
        stale = self.current_reader.replace(b'return "sha256:" + hashlib.sha256(data).hexdigest()',
                                            b'return "sha512:" + hashlib.sha256(data).hexdigest()')
        self.assertNotEqual(stale, self.current_reader)
        self.assertEqual(len(stale), len(self.current_reader))
        self.reader.write_bytes(stale)
        metadata = self.reader.stat()
        py_compile.compile(str(self.reader), doraise=True, invalidation_mode=mode)
        self.reader.write_bytes(self.current_reader if current is None else current)
        os.utime(self.reader, ns=(metadata.st_atime_ns, metadata.st_mtime_ns))

    def assert_cache_ignored(self, mode):
        cold = self.run_helper()
        self.assertEqual(cold.returncode, 0, cold.stderr)
        self.assertEqual(list(self.root.rglob('*.pyc')), [])
        self.seed_cache(mode)
        before = self.inventory()
        warm = self.run_helper()
        self.assertEqual(warm.returncode, 0, warm.stderr)
        self.assertEqual(warm.stdout, cold.stdout)
        record = json.loads(warm.stdout)
        self.assertEqual(record['files'][0]['excerpts'][0]['text'].encode(), self.raw)
        self.assertEqual(self.inventory(), before)

    def test_production_reader_ignores_stale_timestamp_cache(self):
        self.assert_cache_ignored(py_compile.PycInvalidationMode.TIMESTAMP)

    def test_production_reader_ignores_unchecked_hash_cache(self):
        self.assert_cache_ignored(py_compile.PycInvalidationMode.UNCHECKED_HASH)

    def test_invalid_current_reader_cannot_use_valid_cached_reader(self):
        self.seed_cache(py_compile.PycInvalidationMode.UNCHECKED_HASH, current=b'invalid syntax!!!\n')
        before = self.inventory()
        result = self.run_helper()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')
        self.assertEqual(json.loads(result.stderr)['code'], 'reader-unavailable')
        self.assertEqual(self.inventory(), before)


if __name__ == '__main__':
    unittest.main()
