"""Exercise the existing CLI executor on this fixed synthetic application only.

Usage: python3 tests/execution.py /absolute/path/to/ah [--report /tmp/report.json]
Requires this fixture's npm dependencies and Playwright browser already installed.
No user-project policy is discovered or executed. All changes are disposable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import os

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('binary', type=Path)
parser.add_argument('--report', type=Path)
args = parser.parse_args()
binary = args.binary.resolve(strict=True)
fixture = Path(__file__).resolve().parents[1]
node = shutil.which('node')
npm = shutil.which('npm')
if not node or not npm or not (fixture / 'node_modules').is_dir():
    raise SystemExit('Install Node/npm and run npm ci in this fixture first.')
node = str(Path(node).resolve(strict=True))
path = os.pathsep.join(dict.fromkeys([str(Path(node).parent), str(Path(npm).parent), '/usr/bin', '/bin']))
with tempfile.TemporaryDirectory(prefix='ah-reading-execution-') as directory:
    root = Path(directory) / 'project'
    shutil.copytree(fixture, root, ignore=shutil.ignore_patterns(
        'node_modules', 'dist', 'test-results', 'playwright-report', 'evidence', '__pycache__'))
    # Installed third-party bytes are not claimed as reviewed transitive identity.
    # Only the native interpreter, policy and declared source/config are bound.
    (root / 'node_modules').symlink_to(fixture / 'node_modules', target_is_directory=True)
    settings = root / '.agentic/check-execution.json'
    settings.write_text(json.dumps({
        'format_version': 1, 'kind': 'check-execution-settings', 'tools': {'node': node},
        'environment': {'PATH': path, 'CI': '1', 'READING_LIST_PORT': '43186'},
        'max_total_ms': 300000,
    }))

    def call(*argv, expected=0):
        result = subprocess.run([str(binary), *argv], cwd=root, capture_output=True, text=True, timeout=330)
        if result.returncode != expected:
            raise AssertionError(f'Executor returned {result.returncode}, expected {expected}: {result.stdout} {result.stderr}')
        return json.loads(result.stderr if expected == 2 else result.stdout)

    config = ('--config', '.agentic/checks.native.json')
    review = call('checks', 'prepare', *config)
    policy = json.loads((root / '.agentic/checks.native.json').read_text())
    assert review['plan']['policy'] == policy
    assert [c['id'] for c in policy['checks']] == ['unit', 'types', 'build', 'browser']
    assert [c['argv'] for c in policy['checks']] == [
        ['node', '--test', 'tests/domain.test.ts'],
        ['node', 'node_modules/vue-tsc/bin/vue-tsc.js', '--noEmit'],
        ['node', 'node_modules/vite/bin/vite.js', 'build'],
        ['node', 'node_modules/@playwright/test/cli.js', 'test'],
    ]
    assert all(c['cwd'] == '.' and c['required'] is True for c in policy['checks'])
    assert review['tools']['node']['path'] == node
    assert review['checks_executed'] is False and review['execution_permitted'] is False
    assert review['execution_supported'] is True, 'This trial requires a supported execution backend.'
    # The authored synthetic trial authorizes exactly this reviewed fixed policy.
    # This is not an auto-approval path for arbitrary discovered project commands.
    run_args = ('checks', 'run', *config, '--approve-review', review['approval_digest'], '--allow-unsandboxed')
    result = call(*run_args)
    assert result['checks_passed'] is True and result['inputs_current'] is True
    assert result['completion_verified'] is False
    assert all(r['outcome']['status'] == 'passed' and r['outcome']['direct_child_reaped'] for r in result['results'])
    assert (root / 'dist/index.html').is_file()
    assert (root / 'dist/THIRD_PARTY_NOTICES.txt').is_file()

    source = root / 'src/domain/entry.ts'
    source.write_text(source.read_text() + '\n// changed after the successful trial\n')
    stale = call(*run_args, expected=2)
    assert stale['kind'] == 'diagnostic'
    missing = json.loads(settings.read_text())
    missing['tools']['node'] = str(root / 'missing-native-tool')
    settings.write_text(json.dumps(missing))
    absent = call('checks', 'prepare', *config, expected=2)
    assert absent['kind'] == 'diagnostic'
    summary = {
        'trial': 'synthetic-reading-list-executor', 'passed': True,
        'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'version': call('--version'),
        'results': [{'id': r['id'], 'outcome': r['outcome']} for r in result['results']],
        'duration_ms': result['duration_ms'], 'timing': result['timing'],
        'stale_review_rejected': True, 'missing_tool_rejected': True,
        'completion_verified': False,
        'limitations': ['No imported-evidence freshness/completion gate or native coding-host/model trial.',
                        'Installed third-party/transitive bytes and runtime versions are not authenticated by this executor.',
                        'Local macOS/Linux backend only; this trial is not a sandbox test.'],
    }
    if args.report:
        args.report.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
