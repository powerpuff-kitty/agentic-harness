#!/usr/bin/env python3
"""Verify the two reviewed self-hosted skill imports; never fetch or install."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[2]
REVISION = '3bbafa3ee1c106edae94893e28b2760f5e3bc663'
SOURCE = 'powerpuff-kitty/agentic-harness-agents'
VERSION = '0.5.0-beta.1'
PREFIX = '.agents/skills/'
# Source Git blob identities reviewed at REVISION. Update only with a reviewed import.
EXPECTED = {
    'decision-intelligence/SKILL.md': '4d5e80381ffad7d89d1c9ad2a7e4f21a512e8c90',
    'decision-intelligence/references/decision-guide.md': '712c715546b631a4dae91620ec5d7d6b38ec66c2',
    'decision-intelligence/bundle.json': '7d254235c570b1fbe284fffc4657240e1bff051e',
    'decision-intelligence/LICENSE': '20e4ac60ec40c75fd112148132f69f52a8cac5b0',
    'agentic-improvement/SKILL.md': 'def06766e3f27e2dc8e048b8356e38d23079850d',
    'agentic-improvement/references/efficiency.md': '987800d6785d680df412a2a39319bff5f43799a3',
    'agentic-improvement/bundle.json': '22c849c8d25e6ddad13c8c910a187cdb8ca88b8d',
    'agentic-improvement/LICENSE': '20e4ac60ec40c75fd112148132f69f52a8cac5b0',
}
SKILLS = tuple(sorted({p.split('/')[0] for p in EXPECTED}))
LIMIT = 65_536
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)')


class InvalidImport(ValueError):
    """Diagnostics omit source content and rejected paths."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidImport(message)


def linked(meta) -> bool:
    return stat.S_ISLNK(meta.st_mode) or bool(getattr(meta, 'st_file_attributes', 0) & 0x400)


def read(root: Path, relative: str) -> bytes:
    path = root
    try:
        require(root.is_dir() and not linked(root.lstat()), 'real checkout required')
        parts = Path(relative).parts
        require(bool(parts) and all(p not in ('.', '..') for p in parts)
                and not Path(relative).is_absolute(), 'relative path required')
        for index, part in enumerate(parts):
            path = path / part
            meta = path.lstat()
            require(not linked(meta), 'linked input refused')
            require(stat.S_ISREG(meta.st_mode) if index == len(parts) - 1
                    else stat.S_ISDIR(meta.st_mode), 'regular input required')
        before = path.stat()
        with path.open('rb') as stream:
            data = stream.read(LIMIT + 1)
        after = path.lstat()
        require(not linked(after) and stat.S_ISREG(after.st_mode)
                and before.st_size == after.st_size == len(data)
                and before.st_mtime_ns == after.st_mtime_ns, 'input changed during read')
        require(len(data) <= LIMIT, 'input size limit exceeded')
        return data
    except OSError:
        raise InvalidImport('missing or unreadable input') from None


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key')
        value[key] = item
    return value


def decode(data: bytes):
    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise InvalidImport('invalid JSON input') from None


def inventory(folder: Path, prefix: str = '') -> set[str]:
    """Only two fixed skill roots; bound traversal and refuse linked directories."""
    found = set()
    visited = 0

    def walk(path, relative, depth):
        nonlocal visited
        require(depth <= 3, 'unexpected directory depth')
        try:
            entries = []
            for entry in path.iterdir():
                require(visited + len(entries) < 16, 'unexpected directory entries')
                entries.append(entry)
            for entry in sorted(entries):
                visited += 1
                meta = entry.lstat()
                require(not linked(meta), 'linked input refused')
                name = relative + entry.name
                if stat.S_ISDIR(meta.st_mode):
                    require(name == 'references', 'undeclared directory')
                    walk(entry, name + '/', depth + 1)
                else:
                    require(stat.S_ISREG(meta.st_mode), 'regular input required')
                    found.add(name)
        except OSError:
            raise InvalidImport('missing or unreadable directory') from None
    walk(folder, prefix, 0)
    return found


def verify(root: Path = ROOT) -> dict:
    lock = decode(read(root, '.agentic/lock.json'))
    require(isinstance(lock, dict), 'invalid lock')
    require(lock.get('agents_source') == {'repository': SOURCE, 'revision': REVISION},
            'unreviewed agents source pin')
    skills, checksums = lock.get('skills'), lock.get('checksums')
    require(isinstance(skills, dict) and isinstance(checksums, dict), 'incomplete lock')
    contents = {}
    for path, expected in EXPECTED.items():
        data = read(root, PREFIX + path)
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        require(git_blob == expected, 'source byte identity mismatch')
        require(checksums.get(PREFIX + path) == hashlib.sha256(data).hexdigest(),
                'lock checksum mismatch')
        contents[path] = data
    router = read(root, 'AGENTS.md').decode('utf-8')
    router_links = {match.split('#', 1)[0] for match in LINK.findall(router)}
    for name in SKILLS:
        require(skills.get(name) == VERSION, 'missing selected skill version')
        require(PREFIX + name + '/SKILL.md' in router_links, 'missing local skill route')
        actual = inventory(root / PREFIX / name)
        expected = {p.split('/', 1)[1] for p in EXPECTED if p.startswith(name + '/')}
        require(actual == expected, 'undeclared skill payload')
        bundle = decode(contents[name + '/bundle.json'])
        require(set(bundle['files']) | {'bundle.json', 'LICENSE'} == actual,
                'incomplete bundle declaration')
        require(bundle['name'] == name and bundle['kind'] == 'standalone-skill',
                'incorrect bundle identity')
        for file in bundle['files']:
            text = contents[name + '/' + file].decode('utf-8')
            for target in LINK.findall(text):
                if target.startswith(('https://', '#')):
                    continue
                require(target.split('#', 1)[0] in bundle['files'], 'unresolved local guide')
    return {
        'scope': 'two-self-hosted-documentation-skills',
        'source_revision': REVISION, 'files_verified': len(EXPECTED),
        'skills': list(SKILLS), 'source_bytes_match': True,
        'network_calls': 0, 'host_loading_verified': False,
        'model_behaviour_verified': False, 'token_savings_verified': False,
        'limitations': ['trusted quiescent checkout', 'reviewed hashes are not signatures',
                        'other declared skills and vendor payload are outside this validator'],
    }


if __name__ == '__main__':
    try:
        print(json.dumps(verify(), sort_keys=True))
    except (InvalidImport, UnicodeError, TypeError, KeyError):
        raise SystemExit('self-hosted skill verification failed; inspect selected imports and lock')
