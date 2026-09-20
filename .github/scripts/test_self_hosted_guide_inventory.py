"""Reviewed guide inventory bounds; no host, helper or provider executes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import validate_self_hosted_skills as imported


def selected(name):
    return {p.split('/', 1)[1] for p in imported.EXPECTED if p.startswith(name + '/')}


def create_tree(root, name):
    folder = root / name
    for path in selected(name):
        target = folder / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'fixture')
    return folder


class GuideInventoryBounds(unittest.TestCase):
    def test_all_reviewed_paths_fit_exact_declared_allowance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in imported.SKILLS:
                folder = create_tree(root, name)
                self.assertEqual(imported.inventory(folder), selected(name))
            # Fifteen files plus two directories no longer fit the old 16 limit.
            self.assertEqual(len(selected('agentic-improvement')), 15)

    def test_extra_file_is_rejected_not_silently_allowed_by_growth(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = create_tree(Path(temp), 'agentic-improvement')
            (folder / 'unreviewed.md').write_bytes(b'not reviewed')
            with self.assertRaises(imported.InvalidImport):
                imported.inventory(folder)

    def test_small_skill_keeps_its_own_bound(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = create_tree(Path(temp), 'documentation')
            (folder / 'unreviewed.md').write_bytes(b'not reviewed')
            with self.assertRaises(imported.InvalidImport):
                imported.inventory(folder)

    def test_overfilled_directory_is_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = create_tree(Path(temp), 'agentic-improvement')
            for index in range(100):
                (folder / 'references' / f'extra-{index}.md').write_bytes(b'not reviewed')
            with self.assertRaises(imported.InvalidImport):
                imported.inventory(folder)

    def test_linked_reference_is_still_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = create_tree(root, 'agentic-improvement')
            path = folder / 'references/log-compaction.md'
            path.unlink()
            (root / 'outside.md').write_bytes(b'outside')
            path.symlink_to(root / 'outside.md')
            with self.assertRaises(imported.InvalidImport):
                imported.inventory(folder)

    def test_inventory_budget_still_has_a_hard_ceiling(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'synthetic'
            folder.mkdir()
            expected = {f'synthetic/file-{index}.md': 'a' * 40 for index in range(65)}
            with patch.object(imported, 'EXPECTED', expected), self.assertRaises(imported.InvalidImport):
                imported.inventory(folder)


class InstalledConditionalGuides(unittest.TestCase):
    def test_real_installed_inventory_and_verification_boundaries(self):
        result = imported.verify()
        self.assertEqual(result['files_verified'], 43)
        self.assertFalse(result['host_loading_verified'])
        self.assertFalse(result['token_savings_verified'])
        self.assertEqual(result['script_execution'], 'not-performed')

    def test_copied_parent_and_deferred_guides_match_reviewed_blobs(self):
        expected = {
            'agentic-improvement/references/efficiency.md': 'd58f485371f0e564c5ba93209916ebfa4823e657',
            'agentic-improvement/references/rule-review.md': '3383f9651258612c320419c3ae9c3fe2a0f791e0',
            'agentic-improvement/references/log-compaction.md': '3ddfbf46313132d23fb962fa7a56a7034a619f07',
            'decision-intelligence/references/decision-guide.md': '3696bd842a16ed877f1faeb19d3d8447184ac352',
            'decision-intelligence/references/recorded-results.md': 'ad43257a1e3f7525cb12bc91653df732e59a6e62',
        }
        for path, want in expected.items():
            raw = imported.read(imported.ROOT, imported.PREFIX + path)
            got = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            self.assertEqual(got, want)
            self.assertEqual(imported.EXPECTED[path], want)


if __name__ == '__main__':
    unittest.main()
