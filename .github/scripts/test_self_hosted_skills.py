#!/usr/bin/env python3
"""Import and mutation tests, not empirical model trials or host activation."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import validate_self_hosted_skills as check


class SelfHostedSkills(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'checkout'
        self.root.mkdir()
        for relative in [*(check.PREFIX + p for p in check.EXPECTED), '.agentic/lock.json', 'AGENTS.md']:
            source, target = check.ROOT / relative, self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def reject(self):
        with self.assertRaises(check.InvalidImport):
            check.verify(self.root)

    def mutate_lock(self, change):
        path = self.root / '.agentic/lock.json'
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_installed_payload_matches_reviewed_source(self):
        report = check.verify(self.root)
        self.assertEqual(report['files_verified'], 8)
        self.assertEqual(report['network_calls'], 0)
        self.assertFalse(report['host_loading_verified'])
        self.assertFalse(report['token_savings_verified'])

    def test_missing_each_import_fails(self):
        for relative in check.EXPECTED:
            path = self.root / check.PREFIX / relative
            original = path.read_bytes()
            path.unlink()
            with self.subTest(path=relative):
                self.reject()
            path.write_bytes(original)

    def test_customised_bytes_are_detected_not_overwritten(self):
        path = self.root / check.PREFIX / 'agentic-improvement/SKILL.md'
        path.write_bytes(path.read_bytes() + b'\nLocal edit.\n')
        before = path.read_bytes()
        self.reject()
        self.assertEqual(path.read_bytes(), before)

    def test_wrong_source_pin(self):
        self.mutate_lock(lambda lock: lock['agents_source'].update(revision='0' * 40))
        self.reject()

    def test_wrong_checksum(self):
        key = check.PREFIX + 'decision-intelligence/SKILL.md'
        self.mutate_lock(lambda lock: lock['checksums'].update({key: '0' * 64}))
        self.reject()

    def test_missing_selected_version(self):
        self.mutate_lock(lambda lock: lock['skills'].pop('agentic-improvement'))
        self.reject()

    def test_undeclared_payload(self):
        (self.root / check.PREFIX / 'agentic-improvement/new.md').write_text('unreviewed')
        self.reject()

    def test_missing_root_route(self):
        path = self.root / 'AGENTS.md'
        path.write_text('# Router with neither selected local link\n')
        self.reject()

    def test_symlink_file_and_parent_refused(self):
        path = self.root / check.PREFIX / 'agentic-improvement/SKILL.md'
        outside = self.root.parent / 'outside'
        outside.write_bytes(path.read_bytes())
        path.unlink()
        try:
            path.symlink_to(outside)
        except OSError:
            self.skipTest('symlink creation unavailable')
        self.reject()
        path.unlink()
        path.write_bytes(outside.read_bytes())
        skill = self.root / check.PREFIX / 'agentic-improvement'
        moved = self.root.parent / 'moved'
        shutil.move(skill, moved)
        skill.symlink_to(moved, target_is_directory=True)
        self.reject()

    def test_duplicate_lock_keys_rejected(self):
        (self.root / '.agentic/lock.json').write_text('{"skills":{},"skills":{}}')
        self.reject()

    def test_oversized_read_refused(self):
        path = self.root / check.PREFIX / 'decision-intelligence/SKILL.md'
        path.write_bytes(b'x' * (check.LIMIT + 1))
        self.reject()

    def test_vendor_and_unselected_files_are_not_required_or_changed(self):
        path = self.root / check.PREFIX / 'typesafe-ai/SKILL.md'
        path.parent.mkdir()
        path.write_bytes(b'unrelated custom vendor bytes\n')
        before = path.read_bytes()
        check.verify(self.root)
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    check.verify()  # Check the real checkout before testing isolated mutations.
    unittest.main()
