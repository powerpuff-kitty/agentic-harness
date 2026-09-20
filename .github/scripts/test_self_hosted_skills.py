#!/usr/bin/env python3
"""Import and mutation tests, not empirical model trials or host activation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import validate_self_hosted_skills as check


class SelfHostedSkills(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'checkout'
        self.root.mkdir()
        paths = [*(check.PREFIX + p for p in check.EXPECTED), '.agentic/lock.json',
                 '.agentic/manifest.yaml', 'AGENTS.md', check.INDEX,
                 check.PREFIX + 'typesafe-ai/SKILL.md']
        for relative in paths:
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
        self.assertEqual(report['files_verified'], 36)
        self.assertEqual(len(report['skills']), 7)
        self.assertEqual(len(report['declared_skills']), 8)
        self.assertEqual(report['missing_declared_skills'], [])
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
        (self.root / 'AGENTS.md').write_text('# Router with no selected local links\n')
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

    def test_independent_vendor_bytes_are_not_overwritten(self):
        path = self.root / check.PREFIX / 'typesafe-ai/SKILL.md'
        path.write_bytes(b'unrelated custom vendor bytes\n')
        before = path.read_bytes()
        check.verify(self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_removed_selected_manifest_declaration_is_rejected(self):
        """Regression failed before the fix with InvalidImport not raised."""
        path = self.root / '.agentic/manifest.yaml'
        text = path.read_text(encoding='utf-8')
        self.assertIn('  - decision-intelligence\n', text)
        path.write_text(text.replace('  - decision-intelligence\n', ''), encoding='utf-8')
        self.reject()

    def test_missing_manifest_rejected(self):
        (self.root / '.agentic/manifest.yaml').unlink()
        self.reject()

    def test_every_removed_declaration_rejected(self):
        path = self.root / '.agentic/manifest.yaml'
        original = path.read_text(encoding='utf-8')
        for name in [*check.SKILLS, *check.INDEPENDENT]:
            path.write_text(original.replace('  - ' + name + '\n', ''), encoding='utf-8')
            with self.subTest(skill=name):
                self.reject()
        path.write_text(original, encoding='utf-8')

    def test_duplicate_unknown_and_missing_skill_sections_rejected(self):
        path = self.root / '.agentic/manifest.yaml'
        original = path.read_text(encoding='utf-8')
        variants = [original.replace('skills:\n', 'skills:\n  - decision-intelligence\n'),
                    original.replace('skills:\n', 'skills:\n  - unknown-skill\n'),
                    original + '\nskills:\n  - documentation\n',
                    original.replace('skills:\n', 'not_skills:\n')]
        for value in variants:
            path.write_text(value, encoding='utf-8')
            self.reject()

    def test_unsupported_yaml_forms_do_not_bypass_binding(self):
        path = self.root / '.agentic/manifest.yaml'
        original = path.read_text(encoding='utf-8')
        variants = ['skills: [decision-intelligence]\n', 'skills: *shared\n',
                    'skills:\n  - &name documentation\n', 'skills:\n  - "documentation"\n',
                    original + '\n"skills": []\n', original + "\n'skills': []\n",
                    original + '\n<<: *override\n', original + '\n---\n']
        for value in variants:
            path.write_text(value, encoding='utf-8')
            self.reject()

    def test_comments_do_not_change_selection(self):
        path = self.root / '.agentic/manifest.yaml'
        text = path.read_text().replace('skills:\n', 'skills: # selected\n')
        text = text.replace('  - documentation\n', '  # scoped guide\n  - documentation # selected\n')
        path.write_text(text)
        self.assertEqual(check.verify(self.root)['missing_declared_skills'], [])

    def test_missing_independent_entrypoint_rejected(self):
        (self.root / check.PREFIX / 'typesafe-ai/SKILL.md').unlink()
        self.reject()

    def test_unreviewed_directory_rejected(self):
        (self.root / check.PREFIX / 'unreviewed-skill').mkdir()
        self.reject()

    def test_missing_or_incomplete_index_rejected(self):
        path = self.root / check.INDEX
        original = path.read_text()
        path.unlink()
        self.reject()
        path.write_text(original.replace('(codebase-audit/SKILL.md)', '(absent/SKILL.md)'))
        self.reject()

    def test_extra_lock_skill_rejected(self):
        self.mutate_lock(lambda lock: lock['skills'].update({'unreviewed-skill': check.VERSION}))
        self.reject()

    def test_boolean_lock_version_rejected(self):
        self.mutate_lock(lambda lock: lock.update(format_version=True))
        self.reject()

    def test_shared_lifecycle_guides_are_local_and_source_mapped(self):
        for relative, upstream in check.SHARED_SOURCES.items():
            self.assertTrue(upstream.startswith('references/'))
            self.assertIn(relative, check.EXPECTED)
            self.assertTrue((self.root / check.PREFIX / relative).is_file())

    def test_lifecycle_mode_guides_are_local_and_referenced(self):
        skill = self.root / check.PREFIX / 'agentic-app'
        body = (skill / 'SKILL.md').read_text(encoding='utf-8')
        for name in ('composition', 'completion'):
            relative = 'references/' + name + '.md'
            self.assertIn('(' + relative + ')', body)
            self.assertIn('agentic-app/' + relative, check.EXPECTED)
            self.assertTrue((skill / relative).is_file())

    def test_optional_helper_declaration_and_no_auto_execution(self):
        folder = self.root / check.PREFIX / 'agentic-improvement'
        declaration = json.loads((folder / 'bundle.json').read_text())
        self.assertEqual(declaration['format_version'], 2)
        self.assertEqual(declaration['optional_scripts'][0]['path'], 'scripts/compact_log.py')
        self.assertEqual(declaration['optional_scripts'][0]['execution'], 'explicit-invocation-only')
        self.assertEqual({item['path'] for item in declaration['optional_scripts']},
                         {'scripts/compact_log.py', 'scripts/evidence_snapshot.py', 'scripts/extract_context.py'})
        self.assertEqual(check.verify(self.root)['script_execution'], 'not-performed')

    def test_actual_imported_helper_preserves_synthetic_log(self):
        check.verify(self.root)
        helper = self.root / check.PREFIX / 'agentic-improvement/scripts/compact_log.py'
        source = self.root / 'synthetic.log'
        raw = b'check=unit attempt=1\n' + b'waiting\n' * 1000 + b'FAIL rare assertion\n'
        source.write_bytes(raw)
        run = subprocess.run([sys.executable, str(helper), str(source)],
                             capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        output = json.loads(run.stdout)
        restored = ''.join(text * count for text, count in output['payload']['runs']).encode()
        self.assertEqual(restored, raw)
        self.assertEqual(source.read_bytes(), raw)
        self.assertEqual(output['source']['sha256'], 'sha256:' + hashlib.sha256(raw).hexdigest())
        self.assertIsNone(output['evidence']['command_exit_code'])
        self.assertIsNone(output['evidence']['producer_output_complete'])
        self.assertEqual(output['measurement']['output_bytes'], len(run.stdout))

    def test_unreviewed_helper_file_rejected(self):
        path = self.root / check.PREFIX / 'agentic-improvement/scripts/unreviewed.py'
        path.write_text('raise AssertionError("must not execute")\n')
        self.reject()

    def test_actual_imported_freshness_helper_detects_changed_evidence(self):
        check.verify(self.root)
        helper = self.root / check.PREFIX / 'agentic-improvement/scripts/evidence_snapshot.py'
        source = self.root / 'sample-evidence.md'
        source.write_bytes(b'allow\n')
        command = [sys.executable, str(helper), 'capture', '--root', str(self.root),
                   '--scope', 'fixture', '--file', 'sample-evidence.md']
        initial = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(initial.returncode, 0, initial.stderr)
        snapshot = self.root.parent / 'snapshot.json'
        snapshot.write_bytes(initial.stdout)  # Test-owned file, not a helper write.
        command[2] = 'compare'
        command.append(str(snapshot))
        unchanged = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        self.assertEqual(json.loads(unchanged.stdout)['status'], 'unchanged-selected-bytes')
        self.assertEqual(source.read_bytes(), b'allow\n')
        source.write_bytes(b'deny!\n')
        changed = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(changed.returncode, 1, changed.stderr)
        result = json.loads(changed.stdout)
        self.assertEqual(result['changed'][0]['path'], 'sample-evidence.md')
        self.assertFalse(result['limits']['checks_verified'])
        self.assertIsNone(result['limits']['model_tokens'])
        self.assertEqual(source.read_bytes(), b'deny!\n')
        self.assertEqual(snapshot.read_bytes(), initial.stdout)

    def test_actual_decision_graph_helper_and_canonical_shape(self):
        from jsonschema import Draft202012Validator
        check.verify(self.root)
        schema = json.loads((check.ROOT / 'catalog/schema/decision-graph.v1.schema.json').read_text())
        validator = Draft202012Validator(schema)
        value = {'format_version': 1, 'kind': 'decision-graph', 'id': 'review.fixture', 'revision': 1,
                 'nodes': [{'id': name, 'spec_id': 'fixture.support', 'spec_revision': 1,
                            'depends_on': ['b'] if name == 'c' else []} for name in ('a', 'b', 'c')],
                 'reducers': [{'id': 'summary', 'type': 'deterministic', 'inputs': ['a', 'c']}]}
        helper = self.root / check.PREFIX / 'decision-intelligence/scripts/review_graph.py'
        source = self.root / 'graph.json'
        command = [sys.executable, str(helper), str(source), '--group-size', '2']
        validator.validate(value)
        data = json.dumps(value).encode()
        source.write_bytes(data)
        run = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['layers'][0]['groups'], [['a', 'b']])
        self.assertEqual(result['layers'][1]['groups'], [['c']])
        self.assertEqual(len(result['repeated_spec_references'][0]['nodes']), 3)
        self.assertFalse(result['boundaries']['consequence_authorized'])
        self.assertEqual(source.read_bytes(), data)
        value['nodes'][1]['depends_on'] = ['c']
        validator.validate(value)  # Schema validity alone cannot rule out a cycle.
        source.write_text(json.dumps(value))
        run = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(json.loads(run.stdout)['layers'], [])
        value['extension'] = 'metadata allowed by the canonical additive schema'
        validator.validate(value)
        source.write_text(json.dumps(value))
        run = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stderr)['code'], 'unsupported-fields')
        self.assertEqual(check.verify(self.root)['script_execution'], 'not-performed')

    def test_actual_excerpt_helper_preserves_pins_ranges_and_budget(self):
        check.verify(self.root)
        helper = self.root / check.PREFIX / 'agentic-improvement/scripts/extract_context.py'
        source = self.root / 'source.txt'
        raw = b'prefix\nnecessary evidence\nsuffix\n'
        source.write_bytes(raw)
        pin = 'sha256:' + hashlib.sha256(raw).hexdigest()
        command = [sys.executable, str(helper), '--root', str(self.root),
                   '--span', 'source.txt', '2', '2', pin, '--span', 'source.txt', '2', '2', pin]
        run = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        record = json.loads(run.stdout)
        self.assertEqual(record['files'][0]['excerpts'][0]['text'], 'necessary evidence\n')
        self.assertEqual(record['measurement']['duplicate_lines_avoided'], 1)
        self.assertEqual(record['files'][0]['omitted_lines'], 2)
        self.assertIsNone(record['limits']['evidence_sufficient'])
        overflow = subprocess.run(command + ['--budget-bytes', '1'], capture_output=True, timeout=10)
        self.assertEqual(overflow.returncode, 1, overflow.stderr)
        self.assertEqual(json.loads(overflow.stdout)['files'], [])
        self.assertNotIn(b'necessary evidence', overflow.stdout)
        self.assertEqual(source.read_bytes(), raw)
        required = ['--require-span', 'source.txt', '2', '2', pin]
        guarded = subprocess.run(command + required, capture_output=True, timeout=10)
        self.assertEqual(guarded.returncode, 0, guarded.stderr)
        self.assertTrue(json.loads(guarded.stdout)['required_evidence']['emitted'])
        missing = subprocess.run(command + ['--require-span', 'source.txt', '1', '3', pin],
                                 capture_output=True, timeout=10)
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, b'')
        self.assertEqual(json.loads(missing.stderr)['code'], 'required-spans-not-covered')
        deferred = subprocess.run(command + required + ['--budget-bytes', '1'],
                                  capture_output=True, timeout=10)
        self.assertEqual(deferred.returncode, 1, deferred.stderr)
        self.assertFalse(json.loads(deferred.stdout)['required_evidence']['emitted'])
        self.assertNotIn(b'necessary evidence', deferred.stdout)
        self.assertEqual(source.read_bytes(), raw)
        source.write_bytes(raw.replace(b'necessary', b'incorrect'))
        stale = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(stale.returncode, 2)
        self.assertEqual(stale.stdout, b'')
        self.assertEqual(check.verify(self.root)['script_execution'], 'not-performed')


if __name__ == '__main__':
    check.verify()  # Check the real checkout before testing isolated mutations.
    unittest.main()