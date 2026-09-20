#!/usr/bin/env python3
"""Verify reviewed self-hosted skills and declarations; never fetch, install or execute helpers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[2]
REVISION = '5cad9ec18b3eff329feab0423b4447c9d9967ec3'
SOURCE = 'powerpuff-kitty/agentic-harness-agents'
VERSION = '0.5.0-beta.1'
PREFIX = '.agents/skills/'
# Reviewed upstream Git blobs. Source paths are skills/<relative>, except LICENSE
# comes from upstream LICENSE and lifecycle's shared guides come from references/.
EXPECTED = {
    "agentic-app/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "agentic-app/SKILL.md": "83d6cbcfc4d6c2959a1ea1a8ff2b56d20414fc79",
    "agentic-app/references/completion.md": "a166f10f4e4b8c1b5115c5364c3d85bce34312c0",
    "agentic-app/references/composition.md": "e8b6b127867322b3d3a4a4a6e8aef0c5e4c1d57c",
    "agentic-app/references/context-engineering.md": "04679455159a19816b4613813d419163df00d786",
    "agentic-app/references/repository-discovery.md": "4f636266e280c4dd8eae30327cd5f9c493a14df7",
    "agentic-improvement/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "agentic-improvement/SKILL.md": "85e7e54d8bd40b8286cedbbba2039b4780da24f2",
    "agentic-improvement/bundle.json": "eba5bab206d756b4b1654841e792d37de564e2dc",
    "agentic-improvement/references/efficiency.md": "96d9c135ea6ff000f8489b3cf4baa43352e3b286",
    "agentic-improvement/references/evidence-reuse.md": "08a7337443fc2889bace1f4fd2b33ac989c2be56",
    "agentic-improvement/scripts/compact_log.py": "39db1fee08fca6614605719c0acee0854965eeac",
    "agentic-improvement/scripts/evidence_snapshot.py": "1c3fbdd1529b58a30deb91090e0d736ee27748c3",
    "codebase-audit/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "codebase-audit/SKILL.md": "b067587f94411fe4078d715899f3084f55b83ef1",
    "codebase-audit/bundle.json": "db8517805e844168fac766fc695d78274d7f11b9",
    "codebase-audit/references/language-review-packs.md": "2ca21bdfd9148ae685cb83666bbfae96be225a5b",
    "codebase-audit/references/report-template.md": "19a20626a678659afe01dd91550d1b6550cc961b",
    "codebase-audit/references/review-guide.md": "2d2b4213d5a75d4221bf4a0950edc4704768f37c",
    "decision-intelligence/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "decision-intelligence/SKILL.md": "4d5e80381ffad7d89d1c9ad2a7e4f21a512e8c90",
    "decision-intelligence/bundle.json": "7d254235c570b1fbe284fffc4657240e1bff051e",
    "decision-intelligence/references/decision-guide.md": "712c715546b631a4dae91620ec5d7d6b38ec66c2",
    "documentation/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "documentation/SKILL.md": "c419a26041754b7f57a1d0919390ac72bb4d1ca5",
    "release/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "release/SKILL.md": "fbe0ccecbf75744f4169ce1c35c3abbc4e781d23",
    "security-review/LICENSE": "20e4ac60ec40c75fd112148132f69f52a8cac5b0",
    "security-review/SKILL.md": "fccc632eaff09f1f9eb0862b5d1cf313e2b89546",
    "security-review/bundle.json": "7cf79d68f9eebe54374a206369a5881fd4c9b8b9",
    "security-review/references/report-template.md": "38386da22d81666a094c7bf69a567c6feeeabc01",
    "security-review/references/review-guide.md": "3c3e3d9e4365bbe918ba972cc1d0785913e2c57d"
}
SKILLS = tuple(sorted({p.split('/')[0] for p in EXPECTED}))
INDEPENDENT = ('typesafe-ai',)
INDEX = PREFIX + 'README.md'
LIMIT = 65_536
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)')
SHARED_SOURCES = {
    'agentic-app/references/context-engineering.md': 'references/context-engineering.md',
    'agentic-app/references/repository-discovery.md': 'references/repository-discovery.md',
}


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


def declarations(text: str) -> set[str]:
    """Own-repository authoring subset, NOT a general YAML parser.

    Exactly one unquoted top-level skills key and a two-space, plain-name block
    list are supported. Other spellings fail explicitly, never silently bypass
    the check. Full manifest/schema validation remains with catalog validation.
    """
    lines = text.splitlines()
    top_level = [line for line in lines if line.strip() and not line.lstrip().startswith('#')
                 and not line.startswith((' ', '\t'))]
    require(all(re.fullmatch(r'[a-z_][a-z0-9_]*:.*', line) for line in top_level),
            'manifest must use reviewed top-level key syntax')
    positions = [i for i, line in enumerate(lines) if re.match(r'^skills\s*:', line)]
    require(len(positions) == 1, 'one top-level skills declaration required')
    start = positions[0]
    require(re.fullmatch(r'skills: *(?:#.*)?', lines[start]) is not None,
            'skills must use reviewed block-list syntax')
    names = []
    for line in lines[start + 1:]:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line.startswith((' ', '\t')):
            break
        match = re.fullmatch(r'  - ([a-z0-9]+(?:-[a-z0-9]+)*) *(?:#.*)?', line)
        require(match is not None, 'skills must use reviewed block-list syntax')
        names.append(match.group(1))
    require(bool(names) and len(names) == len(set(names)), 'missing or duplicate skill declaration')
    return set(names)


def inventory(folder: Path, prefix: str = '') -> set[str]:
    """Bound selected skill traversal and refuse linked directories."""
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
                    require(name in ('references', 'scripts') and
                            any(p.startswith(folder.name + '/' + name + '/') for p in EXPECTED),
                            'undeclared directory')
                    walk(entry, name + '/', depth + 1)
                else:
                    require(stat.S_ISREG(meta.st_mode), 'regular input required')
                    found.add(name)
        except OSError:
            raise InvalidImport('missing or unreadable directory') from None
    walk(folder, prefix, 0)
    return found


def directory_names(root: Path) -> set[str]:
    names = set()
    try:
        for count, path in enumerate((root / PREFIX).iterdir(), 1):
            require(count <= 32, 'skill directory limit exceeded')
            meta = path.lstat()
            require(not linked(meta), 'linked skill root refused')
            if path.name == 'README.md':
                require(stat.S_ISREG(meta.st_mode), 'regular skill index required')
            else:
                require(stat.S_ISDIR(meta.st_mode), 'unexpected skill-root entry')
                names.add(path.name)
    except OSError:
        raise InvalidImport('missing or unreadable skill root') from None
    return names


def verify(root: Path = ROOT) -> dict:
    declared = declarations(read(root, '.agentic/manifest.yaml').decode('utf-8'))
    required = set(SKILLS) | set(INDEPENDENT)
    require(declared == required, 'manifest and reviewed skill selection disagree')
    lock = decode(read(root, '.agentic/lock.json'))
    require(isinstance(lock, dict) and type(lock.get('format_version')) is int
            and lock['format_version'] == 1, 'invalid lock')
    require(lock.get('agents_source') == {'repository': SOURCE, 'revision': REVISION},
            'unreviewed agents source pin')
    skills, checksums = lock.get('skills'), lock.get('checksums')
    require(isinstance(skills, dict) and isinstance(checksums, dict), 'incomplete lock')
    require(set(skills) == set(SKILLS), 'lock skill inventory mismatch')
    contents = {}
    for path, expected in EXPECTED.items():
        data = read(root, PREFIX + path)
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        require(git_blob == expected, 'source byte identity mismatch')
        require(checksums.get(PREFIX + path) == hashlib.sha256(data).hexdigest(),
                'lock checksum mismatch')
        contents[path] = data
    # Checking imported parents above prevents traversing a linked skills root.
    require(directory_names(root) == declared, 'declared and installed directories disagree')
    router_links = {target.split('#', 1)[0]
                    for target in LINK.findall(read(root, 'AGENTS.md').decode('utf-8'))}
    require(INDEX in router_links, 'missing conditional skill-index route')
    index_links = {target.split('#', 1)[0]
                   for target in LINK.findall(read(root, INDEX).decode('utf-8'))}
    for name in sorted(required):
        require(name + '/SKILL.md' in index_links, 'missing indexed skill route')
    for name in INDEPENDENT:
        require(bool(read(root, PREFIX + name + '/SKILL.md').strip()), 'missing independent skill entrypoint')
    for name in SKILLS:
        require(skills.get(name) == VERSION, 'missing selected skill version')
        actual = inventory(root / PREFIX / name)
        expected = {p.split('/', 1)[1] for p in EXPECTED if p.startswith(name + '/')}
        require(actual == expected, 'undeclared skill payload')
        if 'bundle.json' in actual:
            bundle = decode(contents[name + '/bundle.json'])
            require(set(bundle['files']) | {'bundle.json', 'LICENSE'} == actual,
                    'incomplete bundle declaration')
            require(bundle['name'] == name and bundle['kind'] == 'standalone-skill',
                    'incorrect bundle identity')
            version = bundle.get('format_version')
            require(type(version) is int and version in (1, 2), 'unsupported bundle version')
            scripts = {p for p in actual if p.startswith('scripts/')}
            if version == 2:
                optional = bundle.get('optional_scripts', [])
                require(bool(optional) and {s['path'] for s in optional} == scripts and
                        all(s['execution'] == 'explicit-invocation-only' and s['fallback']
                            for s in optional), 'invalid optional helper declaration')
            else:
                require(not scripts, 'v1 bundle cannot contain scripts')
        for file in actual:
            if not file.endswith('.md'):
                continue
            for target in LINK.findall(contents[name + '/' + file].decode('utf-8')):
                if target.startswith(('https://', '#')):
                    continue
                require(target.split('#', 1)[0] in actual, 'unresolved local guide')
    return {
        'scope': 'reviewed-self-hosted-harness-skills',
        'source_revision': REVISION, 'files_verified': len(EXPECTED),
        'skills': list(SKILLS), 'source_bytes_match': True,
        'declared_skills': sorted(declared), 'missing_declared_skills': [],
        'independent_skills': list(INDEPENDENT), 'shared_source_paths': SHARED_SOURCES,
        'network_calls': 0, 'host_loading_verified': False,
        'model_behaviour_verified': False, 'token_savings_verified': False,
        'script_execution': 'not-performed',
        'limitations': ['trusted quiescent checkout', 'reviewed hashes are not signatures',
                        'independent vendor content is not source-verified',
                        'manifest skills use a checked authoring subset, not full YAML parsing'],
    }


if __name__ == '__main__':
    try:
        print(json.dumps(verify(), sort_keys=True))
    except (InvalidImport, UnicodeError, TypeError, KeyError):
        raise SystemExit('self-hosted skill verification failed; inspect declarations, imports and lock')
