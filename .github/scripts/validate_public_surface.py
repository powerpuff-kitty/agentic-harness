#!/usr/bin/env python3
"""Check literal public repository references and the declared quick-start fixture.

This is a narrow documentation regression check, not a secret scanner, semantic
privacy review, CLI execution test, or Git-history scrubber. No network is used.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path
from urllib.parse import unquote

PUBLIC_REPOSITORIES = frozenset({
    "agentic-harness", "agentic-harness-agents", "agentic-harness-cli",
})
REPOSITORY_NAME = re.compile(
    r"(?<![a-z0-9_-])agentic-harness(?:-[a-z0-9]+)*(?![a-z0-9_-])",
    re.IGNORECASE,
)
EXCLUDED_DIRECTORIES = frozenset({".git", ".venv", "venv", "node_modules", "__pycache__"})
MAX_TEXT_BYTES = 2 * 1024 * 1024
START = "<!-- ah-quick-start -->"
END = "<!-- /ah-quick-start -->"


def unapproved_references(value: str) -> bool:
    """Recognize literal names and one level of URL percent encoding."""
    return any(
        match.group().lower() not in PUBLIC_REPOSITORIES
        for match in REPOSITORY_NAME.finditer(unquote(value))
    )


def safe_path(path: str) -> str:
    """Do not echo a disallowed identifier even when it occurs in a filename."""
    value = REPOSITORY_NAME.sub(
        lambda match: match.group() if match.group().lower() in PUBLIC_REPOSITORIES
        else "[unapproved-reference]",
        unquote(path),
    )
    return value.encode("unicode_escape").decode("ascii")


def reference_errors(root: Path) -> list[str]:
    errors: list[str] = []
    if root.is_symlink() or not root.is_dir():
        return ["public-surface: root must be a real directory"]

    def walk_error(_error: OSError) -> None:
        errors.append("public-surface: directory traversal incomplete")

    for directory, dirs, filenames in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        # Check path names before exclusions so an identifier cannot hide there.
        for name in sorted(dirs + filenames):
            relative = (base / name).relative_to(root).as_posix()
            if unapproved_references(relative):
                errors.append(f"{safe_path(relative)}: unapproved repository reference in path")
        retained = []
        for name in sorted(dirs):
            if name in EXCLUDED_DIRECTORIES:
                continue
            path = base / name
            if path.is_symlink():
                errors.append(f"{safe_path(path.relative_to(root).as_posix())}: symlink not scanned")
            else:
                retained.append(name)
        dirs[:] = retained
        for name in sorted(filenames):
            path = base / name
            label = safe_path(path.relative_to(root).as_posix())
            if path.is_symlink() or not path.is_file():
                errors.append(f"{label}: non-regular file not scanned")
                continue
            try:
                with path.open("rb") as source:
                    data = source.read(MAX_TEXT_BYTES + 1)
                # Binary payloads are outside this text-only validator's scope.
                if b"\x00" in data:
                    continue
                if len(data) > MAX_TEXT_BYTES:
                    errors.append(f"{label}: text size limit exceeded; not scanned")
                    continue
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"{label}: unsupported text encoding; not scanned")
                continue
            except OSError:
                errors.append(f"{label}: unreadable file; not scanned")
                continue
            for line_number, line in enumerate(text.splitlines(), 1):
                if unapproved_references(line):
                    errors.append(f"{label}:{line_number}: unapproved repository reference")
    return sorted(set(errors))


def quick_start_errors(root: Path) -> list[str]:
    """Compare docs with data, never execute shell text taken from a document."""
    try:
        contract = json.loads((root / "catalog/quick-start.json").read_text(encoding="utf-8"))
        readme = (root / "README.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError):
        return ["quick-start: missing, unreadable or invalid fixture/README"]
    if not isinstance(contract, dict) or type(contract.get("format_version")) is not int or contract["format_version"] != 1:
        return ["quick-start: unsupported fixture format"]
    if contract.get("kind") != "public-quick-start":
        return ["quick-start: invalid fixture kind"]
    commands = contract.get("commands")
    if not isinstance(commands, list) or not commands or any(
        not isinstance(command, list) or not command
        or any(not isinstance(arg, str) or not arg for arg in command)
        or command[0] != "ah"
        for command in commands
    ):
        return ["quick-start: commands must be nonempty ah argument arrays"]
    if readme.count(START) != 1 or readme.count(END) != 1:
        return ["quick-start: expected exactly one marked README example"]
    if readme.index(START) > readme.index(END):
        return ["quick-start: invalid marker order"]
    block = readme.split(START, 1)[1].split(END, 1)[0].strip()
    match = re.fullmatch(r"```bash\n(.*?)\n```", block, flags=re.DOTALL)
    if match is None:
        return ["quick-start: example must be one bash fence"]
    try:
        actual = [shlex.split(line, comments=False) for line in match.group(1).splitlines() if line.strip()]
    except ValueError:
        return ["quick-start: invalid argument quoting"]
    if actual != commands:
        return ["quick-start: README differs from catalog/quick-start.json"]
    return []


def validate_public_surface(root: Path) -> list[str]:
    return reference_errors(root) + quick_start_errors(root)


def main() -> int:
    if len(sys.argv) > 2:
        print("usage: validate_public_surface.py [ROOT]", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2]
    errors = validate_public_surface(root)
    if errors:
        print("Public surface validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Public text references and quick-start fixture valid; CLI behavior not executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
