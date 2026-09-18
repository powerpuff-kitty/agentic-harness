"""Prepare an inspectable native-host trial; never launches an agent/model.

python3 native-host/prepare.py /absolute/path/to/ah /new/trial-directory [--host current-session|claude]
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(binary, destination, host_mode="current-session"):
    binary = binary.resolve(strict=True)
    if destination.exists():
        raise ValueError('Trial directory must not exist; existing work is never overwritten.')
    fixture = Path(__file__).resolve().parents[1]
    destination.mkdir(parents=True)
    root = destination / 'project'
    root.mkdir()

    def ah(*args):
        p = subprocess.run([str(binary), *args], cwd=root, capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            raise RuntimeError('Synthetic harness installation failed: ' + p.stderr)
        return json.loads(p.stdout)

    version = ah('--version')
    ah('init', '.', '--boilerplate', 'web-app', '--context-profile', 'minimal')
    shutil.copytree(fixture, root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
        'node_modules', 'dist', 'test-results', 'playwright-report', 'evidence', '__pycache__',
        'manifest.yaml', 'lock.json', 'native-host'))
    design = root / '.agentic/DESIGN.md'
    design.write_text(design.read_text() + '''
## Approved native-host trial change

Add a visible, politely announced unread counter named "Unread count". Its exact text is
"Unread in this session: N", where N counts unread entries across the entire session,
independent of the All/Unread filter. It starts at zero, updates on successful add and
read/unread toggle, stays unchanged on invalid input, and returns to zero on reload.
Keep the existing announcement and keyboard/focus behavior. Use existing visual tokens;
add no dependency, storage, network request, service/domain change or new raw control.
Only src/presentation/views/ReadingList.vue may change during this task.
''')
    if host_mode == 'claude':
        plan = ah('adapters', 'sync', '.', '--host', 'claude', '--profile', 'typed-ui')
        installed = ah('adapters', 'sync', '.', '--host', 'claude', '--profile', 'typed-ui', '--apply', '--review', plan['plan_digest'])
        assert installed['host_delivery_verified'] is False
    shutil.copyfile(fixture / 'native-host/unread-count.spec.ts', root / 'tests/browser/native-host.spec.ts')
    if (fixture / 'node_modules').is_dir():
        (root / 'node_modules').symlink_to(fixture / 'node_modules', target_is_directory=True)
    prompt = ('Implement the approved native-host trial change described in this project context. '
              'Follow the repository instructions and change only the allowed application file. '
              'Do not modify tests, policy, adapters or dependencies. '
              'In your final response identify the context files used, the change made, and checks you could not run.')
    if host_mode == 'claude':
        prompt += ' Do not run commands; the parent will verify after the file-inventory check.'
    else:
        prompt += ' Verify only after comparing the allowed edit against the starting file inventory.'
    (destination / 'prompt.txt').write_text(prompt + '\n')
    host_version = None
    argv = None
    if host_mode == 'claude':
        host = shutil.which('claude')
        host_version = subprocess.check_output([host, '--version'], text=True).strip() if host else None
        argv = [host or 'claude', '--print', '--output-format', 'stream-json', '--verbose',
                '--no-session-persistence', '--setting-sources', 'project',
                '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                '--no-chrome', '--disable-slash-commands', '--permission-mode', 'dontAsk',
                '--tools', 'Read,Edit,Write,Glob,Grep', '--allowedTools', 'Read,Edit,Write,Glob,Grep',
                '--max-budget-usd', '1', prompt]
    files = {}
    for p in root.rglob('*'):
        if p.is_file() and not p.is_symlink() and 'node_modules' not in p.relative_to(root).parts:
            files[p.relative_to(root).as_posix()] = sha(p)
    report = {'kind': 'prepared-native-host-trial', 'format_version': 1,
              'binary_sha256': sha(binary), 'cli_version': version,
              'host_mode': host_mode, 'host_version': host_version, 'cwd': str(root.resolve()), 'argv': argv,
              'allowed_change': 'src/presentation/views/ReadingList.vue', 'before': files,
              'max_budget_usd': 1 if host_mode == 'claude' else None,
              'supervisor_timeout_seconds': 300 if host_mode == 'claude' else None,
              'host_invoked': False, 'model_execution': 'not-run',
              'native_loading_verified': False, 'enforcement_verified': False,
              'limitations': ['Current-session mode launches no separate agent and has no separate process/billing cap.',
                              'Tool allowlisting is not an OS sandbox.',
                              'Host versions and installed adapter files are not proof of native loading.',
                              'Raw host transcripts require review before publication.']}
    (destination / 'trial.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'prepared': str(destination), 'host_version': host_version,
                      'host_invoked': False, 'model_execution': 'not-run'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--host', choices=['current-session', 'claude'], default='current-session')
    args = parser.parse_args()
    prepare(args.binary, args.destination.absolute(), args.host)
