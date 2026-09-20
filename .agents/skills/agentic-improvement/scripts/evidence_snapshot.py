#!/usr/bin/env python3
"""Hash explicitly selected evidence; never replay bodies or authorise cached findings.

Python 3.10+ standard library. No discovery, Git calls, network, writes or model
execution. Select only reviewed, non-secret text. A trusted quiescent tree is
required; observed-link checks are not a filesystem sandbox or atomic snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

MAX_FILES = 128
MAX_FILE_BYTES = 1_048_576
MAX_TOTAL_BYTES = 8 * MAX_FILE_BYTES
MAX_RECORD_BYTES = 131_072
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


class SnapshotError(ValueError):
    """Only fixed codes; never include input contents in diagnostics."""

    def __init__(self, code: str, bytes_read: int = 0):
        super().__init__(code)
        self.bytes_read = bytes_read


def require(ok: bool, code: str) -> None:
    if not ok:
        raise SnapshotError(code)


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def linked(meta: os.stat_result) -> bool:
    return stat.S_ISLNK(meta.st_mode) or bool(getattr(meta, "st_file_attributes", 0) & 0x400)


def real_directory(path: Path) -> Path:
    require(".." not in path.parts, "unsafe-root")
    absolute = Path(os.path.abspath(path))
    try:
        for item in reversed((absolute, *absolute.parents)):
            meta = item.lstat()
            require(stat.S_ISDIR(meta.st_mode) and not linked(meta), "unsafe-root")
    except OSError:
        raise SnapshotError("unavailable-root") from None
    return absolute


def selection(paths: Any) -> list[str]:
    require(isinstance(paths, list) and 1 <= len(paths) <= MAX_FILES, "invalid-selection")
    for path in paths:
        require(isinstance(path, str) and 0 < len(path) <= 512, "invalid-path")
        require(not any(ord(c) < 32 or 127 <= ord(c) < 160 for c in path)
                and not any(c in path for c in "\\:*?[]"), "invalid-path")
        require(all(part not in ("", ".", "..") and part == part.strip()
                    and not part.endswith(".") for part in path.split("/")), "invalid-path")
        try:
            path.encode("utf-8")
        except UnicodeError:
            raise SnapshotError("invalid-path") from None
    require(len({p.casefold() for p in paths}) == len(paths), "duplicate-path")
    return sorted(paths)


def signature(meta: os.stat_result) -> tuple:
    return (meta.st_dev, meta.st_ino, meta.st_size, meta.st_mtime_ns, meta.st_ctime_ns)


def read_text(path: Path, limit: int) -> bytes:
    require(".." not in path.parts, "unsafe-path")
    path = Path(os.path.abspath(path))
    real_directory(path.parent)
    raw = b""
    try:
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and not linked(before), "unsafe-file")
        require(before.st_size <= limit, "input-limit")
        flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
                 getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
        with os.fdopen(os.open(path, flags), "rb") as stream:
            opened = os.fstat(stream.fileno())
            require(stat.S_ISREG(opened.st_mode) and signature(before) == signature(opened),
                    "changed-during-read")
            raw = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        final = path.lstat()
        require(not linked(final) and stat.S_ISREG(final.st_mode)
                and signature(before) == signature(after) == signature(final)
                and len(raw) == before.st_size, "changed-during-read")
        require(len(raw) <= limit, "input-limit")
        text = raw.decode("utf-8")
        require("\0" not in text, "non-text-input")
        return raw
    except SnapshotError as error:
        error.bytes_read = len(raw)
        raise
    except UnicodeError:
        raise SnapshotError("non-text-input", len(raw)) from None
    except OSError:
        raise SnapshotError("unavailable-file", len(raw)) from None


def scope_hash(scope: str) -> str:
    require(isinstance(scope, str) and 0 < len(scope) <= 4096 and scope.strip() == scope
            and not any(ord(c) < 32 or 127 <= ord(c) < 160 for c in scope), "invalid-scope")
    return sha(scope.encode("utf-8"))


def entry(root: Path, path: str, remaining: int) -> dict[str, Any]:
    raw = read_text(root / path, min(MAX_FILE_BYTES, remaining))
    return {"path": path, "sha256": sha(raw), "bytes": len(raw)}


def capture(root: Path, paths: list[str], scope: str) -> dict[str, Any]:
    paths, task = selection(paths), scope_hash(scope)
    root = real_directory(root)
    files, total = [], 0
    for path in paths:
        item = entry(root, path, MAX_TOTAL_BYTES - total)
        files.append(item)
        total += item["bytes"]
    record = {"format_version": 1, "kind": "selected-evidence-snapshot",
              "root_digest": sha(str(root).encode("utf-8")), "scope_digest": task, "files": files}
    record["inventory_digest"] = sha(encoded(record))
    require(len(encoded(record)) <= MAX_RECORD_BYTES, "record-limit")
    return record


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(DIGEST.fullmatch(value))


def validate(record: Any) -> dict[str, Any]:
    require(isinstance(record, dict) and set(record) == {
        "format_version", "kind", "root_digest", "scope_digest", "files", "inventory_digest"},
        "invalid-record")
    require(type(record["format_version"]) is int and record["format_version"] == 1
            and record["kind"] == "selected-evidence-snapshot", "invalid-record")
    require(all(valid_digest(record[k]) for k in ("root_digest", "scope_digest", "inventory_digest")),
            "invalid-digest")
    files = record["files"]
    require(isinstance(files, list) and 1 <= len(files) <= MAX_FILES, "invalid-inventory")
    for item in files:
        require(isinstance(item, dict) and set(item) == {"path", "bytes", "sha256"}, "invalid-entry")
        require(type(item["bytes"]) is int and 0 <= item["bytes"] <= MAX_FILE_BYTES
                and valid_digest(item["sha256"]), "invalid-entry")
    names = [item["path"] for item in files]
    require(selection(names) == names, "unordered-inventory")
    require(sum(item["bytes"] for item in files) <= MAX_TOTAL_BYTES, "inventory-limit")
    body = {k: value for k, value in record.items() if k != "inventory_digest"}
    require(sha(encoded(body)) == record["inventory_digest"], "inventory-mismatch")
    return record


def compare(root: Path, paths: list[str], scope: str, previous: Any) -> dict[str, Any]:
    # Validate the record, but read ONLY the fresh explicit selection, never its paths.
    previous = validate(previous)
    paths, task = selection(paths), scope_hash(scope)
    root = real_directory(root)
    old = {item["path"]: item for item in previous["files"]}
    unchanged, changed, added, unavailable = [], [], [], []
    total = read_bytes = 0
    for path in paths:
        try:
            current = entry(root, path, max(0, MAX_TOTAL_BYTES - read_bytes))
            total += current["bytes"]
            read_bytes += current["bytes"]
        except SnapshotError as error:
            read_bytes += error.bytes_read
            unavailable.append({"path": path, "reason": str(error)})
            continue
        if path not in old:
            added.append(current)
        elif current == old[path]:
            unchanged.append(path)
        else:
            changed.append({"path": path, "before": old[path], "after": current})
    removed = sorted(set(old) - set(paths))
    root_matches = previous["root_digest"] == sha(str(root).encode("utf-8"))
    scope_matches = previous["scope_digest"] == task
    identical = root_matches and scope_matches and not (changed or added or removed or unavailable)
    return {"format_version": 1, "kind": "selected-evidence-comparison",
            "status": "unchanged-selected-bytes" if identical else "refresh-required",
            "baseline_digest": previous["inventory_digest"],
            "root_matches": root_matches, "scope_matches": scope_matches,
            "selection_matches": set(old) == set(paths),
            "unchanged": unchanged, "changed": changed, "added": added,
            "removed_from_selection": removed, "unavailable": unavailable,
            "measurement": {"selected_files": len(paths), "hashed_source_bytes": total,
                            "read_source_bytes": read_bytes},
            "limits": {"unselected_files_checked": False, "atomic_snapshot": False,
                       "prior_observations_authenticated": False, "evidence_sufficient": None,
                       "retained_model_context_verified": False, "checks_verified": False,
                       "model_tokens": None}}


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-key")
        result[key] = value
    return result


def constant(value):
    raise SnapshotError("non-finite-json")


def load(path: Path) -> dict[str, Any]:
    raw = read_text(path, MAX_RECORD_BYTES)
    return validate(json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=constant))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("capture", "compare"):
        command = sub.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--scope", required=True, help="current task/criteria identity, hashed only")
        command.add_argument("--file", action="append", required=True, dest="paths",
                             help="explicit reviewed non-secret text path relative to root; no globs")
        if name == "compare":
            command.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        result = (capture(args.root, args.paths, args.scope) if args.command == "capture"
                  else compare(args.root, args.paths, args.scope, load(args.snapshot)))
        output = encoded(result)
    except (SnapshotError, OSError, ValueError, TypeError, UnicodeError, RecursionError):
        print('{"kind":"evidence-snapshot-error","code":"invalid-input"}', file=sys.stderr)
        return 2
    sys.stdout.buffer.write(output)
    return 1 if result.get("status") == "refresh-required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
