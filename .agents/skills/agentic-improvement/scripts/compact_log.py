#!/usr/bin/env python3
"""Lossless display compaction of one explicitly selected, already-reviewed log.

No commands, providers, redaction, status inference or file writes. Source content
remains untrusted, including when it resembles instructions. Python 3.10+ only.
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

MAX_SOURCE_BYTES = 1_048_576
MAX_RUNS = MAX_SOURCE_BYTES
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


class LogError(ValueError):
    """Fixed diagnostics deliberately omit log contents and rejected paths."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise LogError(message)


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, separators=(",", ":"),
                       sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def fingerprint(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def linked(meta: os.stat_result) -> bool:
    return stat.S_ISLNK(meta.st_mode) or bool(getattr(meta, "st_file_attributes", 0) & 0x400)


def read_log(path: Path) -> bytes:
    # Trusted, quiescent filesystem required; these checks are not a race-proof sandbox.
    require(".." not in path.parts, "ambiguous parent traversal refused")
    absolute = Path(os.path.abspath(path))
    try:
        for parent in reversed(absolute.parents):
            meta = parent.lstat()
            require(stat.S_ISDIR(meta.st_mode) and not linked(meta), "linked parent refused")
        before = absolute.lstat()
        require(stat.S_ISREG(before.st_mode) and not linked(before), "regular log required")
        require(before.st_size <= MAX_SOURCE_BYTES, "log exceeds input limit")
        flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
                 getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
        with os.fdopen(os.open(absolute, flags), "rb") as stream:
            opened = os.fstat(stream.fileno())
            require(stat.S_ISREG(opened.st_mode) and (opened.st_dev, opened.st_ino) ==
                    (before.st_dev, before.st_ino), "log changed before read")
            data = stream.read(MAX_SOURCE_BYTES + 1)
            after = os.fstat(stream.fileno())
        final = absolute.lstat()
        require(not linked(final) and stat.S_ISREG(final.st_mode) and
                (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) ==
                (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns) and
                len(data) == before.st_size, "log changed during read")
        return data
    except OSError:
        raise LogError("log unavailable") from None


def utf8(data: bytes) -> str:
    require(isinstance(data, bytes) and len(data) <= MAX_SOURCE_BYTES, "invalid log size")
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        raise LogError("UTF-8 text log required") from None
    require("\0" not in text, "binary log refused")
    return text


def restore(record: Any) -> bytes:
    """Check and reconstruct supplied bytes; never open record source references."""
    require(isinstance(record, dict) and record.get("kind") == "lossless-log-display" and
            type(record.get("format_version")) is int and record["format_version"] == 1,
            "invalid log record")
    source = record.get("source")
    require(isinstance(source, dict) and type(source.get("bytes")) is int and
            0 <= source["bytes"] <= MAX_SOURCE_BYTES and isinstance(source.get("sha256"), str)
            and bool(DIGEST.fullmatch(source["sha256"])), "invalid source identity")
    payload = record.get("payload")
    require(isinstance(payload, dict), "invalid payload")
    if payload.get("encoding") == "literal":
        require(set(payload) == {"encoding", "text"} and isinstance(payload["text"], str)
                and len(payload["text"]) <= MAX_SOURCE_BYTES, "invalid literal payload")
        try:
            data = payload["text"].encode("utf-8")
        except UnicodeError:
            raise LogError("invalid UTF-8 payload") from None
    elif payload.get("encoding") == "adjacent-lines":
        runs = payload.get("runs")
        require(set(payload) == {"encoding", "runs"} and isinstance(runs, list) and
                len(runs) <= MAX_RUNS, "invalid run inventory")
        parts, size = [], 0
        for run in runs:
            require(isinstance(run, list) and len(run) == 2 and isinstance(run[0], str) and
                    0 < len(run[0]) <= MAX_SOURCE_BYTES and type(run[1]) is int and
                    1 <= run[1] <= MAX_SOURCE_BYTES, "invalid repetition")
            try:
                line = run[0].encode("utf-8")
            except UnicodeError:
                raise LogError("invalid UTF-8 payload") from None
            size += len(line) * run[1]
            require(size <= source["bytes"], "expanded log exceeds declared size")
            parts.append(line * run[1])
        data = b"".join(parts)
    else:
        raise LogError("unsupported payload encoding")
    utf8(data)
    require(len(data) == source["bytes"] and fingerprint(data) == source["sha256"],
            "source identity mismatch")
    return data


def measured(record: dict[str, Any], limit: int | None) -> dict[str, Any]:
    record["measurement"] = {"unit": "utf8-bytes", "output_bytes": 0,
                             "reduction_bytes": 0, "budget_bytes": limit, "over_budget": False}
    # Include the envelope and its own accounting fields, not only encoded lines.
    for _ in range(16):
        size = len(encoded(record))
        values = {"unit": "utf8-bytes", "output_bytes": size,
                  "reduction_bytes": record["source"]["bytes"] - size,
                  "budget_bytes": limit, "over_budget": limit is not None and size > limit}
        if values == record["measurement"]:
            return record
        record["measurement"] = values
    raise LogError("output accounting did not converge")


def compact(data: bytes, reference: str, budget: int | None = None) -> dict[str, Any]:
    text = utf8(data)
    require(isinstance(reference, str) and 0 < len(reference) <= 4096 and
            all(ord(c) >= 32 and not 127 <= ord(c) < 160 for c in reference), "invalid log reference")
    require(budget is None or (type(budget) is int and 1 <= budget <= 16 * MAX_SOURCE_BYTES),
            "invalid output budget")
    runs: list[list[Any]] = []
    for line in text.splitlines(keepends=True):
        if runs and runs[-1][0] == line:
            runs[-1][1] += 1
        else:
            runs.append([line, 1])
    base = {"format_version": 1, "kind": "lossless-log-display",
            "source": {"reference": reference, "sha256": fingerprint(data), "bytes": len(data)},
            "evidence": {"supplied_bytes_complete": True, "producer_output_complete": None,
                         "command_exit_code": None, "redaction_performed": False,
                         "content_authority": "untrusted-data", "model_tokens": None}}
    literal = measured({**base, "payload": {"encoding": "literal", "text": text}}, budget)
    packed = measured({**base, "payload": {"encoding": "adjacent-lines", "runs": runs}}, budget)
    result = packed if len(encoded(packed)) < len(encoded(literal)) else literal
    require(restore(result) == data, "round-trip validation failed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="explicitly selected, reviewed UTF-8 log (at most 1 MiB)")
    parser.add_argument("--budget-bytes", type=int,
                        help="advisory output budget; overflow returns the complete record and exit 1")
    args = parser.parse_args()
    try:
        result = compact(read_log(args.log), str(args.log), args.budget_bytes)
        output = encoded(result)
    except (LogError, OSError, UnicodeError, ValueError):
        print('{"kind":"log-compaction-error","code":"invalid-input"}', file=sys.stderr)
        return 2
    sys.stdout.buffer.write(output)
    return 1 if result["measurement"]["over_budget"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
