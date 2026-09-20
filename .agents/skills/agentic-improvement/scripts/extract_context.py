#!/usr/bin/env python3
"""Read explicit hash-pinned source spans; never select relevance or certify evidence.

Python 3.10+ standard library. Requires the reviewed sibling evidence_snapshot.py.
Local reads only, no writes/providers. Source text remains untrusted and unredacted.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

# Import current sibling SOURCE, never an old pyc or a namesake on PYTHONPATH.
MAX_READER_BYTES = 65_536


def load_reader():
    path = Path(__file__).absolute().with_name("evidence_snapshot.py")

    def identity(meta):
        if not stat.S_ISREG(meta.st_mode) or bool(getattr(meta, "st_file_attributes", 0) & 0x400):
            raise ImportError("reader-unavailable")
        return (meta.st_dev, meta.st_ino, meta.st_size, meta.st_mtime_ns, meta.st_ctime_ns)

    before = path.lstat()
    expected = identity(before)
    if before.st_size > MAX_READER_BYTES:
        raise ImportError("reader-unavailable")
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
             getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
    with os.fdopen(os.open(path, flags), "rb") as stream:
        if identity(os.fstat(stream.fileno())) != expected:
            raise ImportError("reader-unavailable")
        source = stream.read(MAX_READER_BYTES + 1)
        after = identity(os.fstat(stream.fileno()))
    if after != expected or identity(path.lstat()) != expected or len(source) != before.st_size:
        raise ImportError("reader-unavailable")
    spec = importlib.util.spec_from_file_location("_excerpt_evidence_reader", path)
    if spec is None or spec.loader is None:
        raise ImportError("reader-unavailable")
    module = importlib.util.module_from_spec(spec)
    # exec_module may read a timestamp-valid or unchecked-hash cache even with -B.
    code = compile(source, str(path), "exec", dont_inherit=True)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        exec(code, module.__dict__)
    finally:
        sys.dont_write_bytecode = previous
    return module


try:
    evidence = load_reader()
except (ImportError, OSError, SyntaxError, ValueError):
    evidence = None

MAX_SPANS = 128
DEFAULT_BUDGET = 65_536
MAX_BUDGET = 8_388_608
NUMBER = re.compile(r"[1-9][0-9]{0,6}\Z")


class ExcerptError(ValueError):
    """Fixed diagnostics contain no source bodies or rejected input values."""


class RequiredEvidenceError(ExcerptError):
    """The explicit selection does not cover its separately declared requirements."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ExcerptError(code)


def line_number(value: Any) -> int:
    if type(value) is int:
        require(1 <= value <= 1_048_576, "invalid-line-range")
        return value
    require(isinstance(value, str) and bool(NUMBER.fullmatch(value)), "invalid-line-range")
    result = int(value)
    require(result <= 1_048_576, "invalid-line-range")
    return result


def requests(spans: Any) -> dict[str, dict[str, Any]]:
    require(evidence is not None, "reader-unavailable")
    require(isinstance(spans, list) and 1 <= len(spans) <= MAX_SPANS, "invalid-span-selection")
    groups: dict[str, dict[str, Any]] = {}
    for span in spans:
        require(isinstance(span, (list, tuple)) and len(span) == 4, "invalid-span-selection")
        path, start, end, digest = span
        evidence.selection([path])
        start, end = line_number(start), line_number(end)
        require(start <= end, "invalid-line-range")
        require(evidence.valid_digest(digest), "invalid-source-pin")
        if path in groups:
            require(groups[path]["sha256"] == digest, "conflicting-source-pins")
        else:
            groups[path] = {"sha256": digest, "ranges": []}
        groups[path]["ranges"].append((start, end))
    evidence.selection(list(groups))  # Also reject aliases that differ only by case.
    return {path: groups[path] for path in sorted(groups)}


def merge_ranges(ranges: list[tuple[int, int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def required_coverage(selected: dict, required_spans: list) -> dict[str, Any]:
    """Inspect declarations only; requirements never add paths to the read selection."""
    required = requests(required_spans)
    normalized = []
    count = lines = 0
    for path, request in required.items():
        chosen = selected.get(path)
        if chosen is None or chosen["sha256"] != request["sha256"]:
            raise RequiredEvidenceError("required-spans-not-covered")
        available = merge_ranges(chosen["ranges"])
        ranges = merge_ranges(request["ranges"])
        # Do not use min(start)..max(end): holes may contain required counterevidence.
        if not all(any(left <= start and end <= right for left, right in available)
                   for start, end in ranges):
            raise RequiredEvidenceError("required-spans-not-covered")
        normalized.append({"path": path, "sha256": request["sha256"], "ranges": ranges})
        count += len(ranges)
        lines += sum(end - start + 1 for start, end in ranges)
    return {"declaration_digest": evidence.sha(evidence.encoded(normalized)),
            "files": len(required), "ranges": count, "lines": lines,
            "coverage": "complete-for-declared-spans", "emitted": True,
            "requirements_authenticated": False}


def lf_lines(raw: bytes) -> list[bytes]:
    # Only LF separates numbered lines. CRLF bytes and other separators stay exact.
    parts = raw.split(b"\n")
    return [part + b"\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def extract(root: Path, spans: list, budget: int = DEFAULT_BUDGET, *,
            required_spans: list | None = None) -> dict[str, Any]:
    require(type(budget) is int and 1 <= budget <= MAX_BUDGET, "invalid-output-budget")
    selected = requests(spans)  # Validate the entire selection before reading source.
    coverage = required_coverage(selected, required_spans) if required_spans is not None else None
    root = evidence.real_directory(root)
    files = []
    read_bytes = selected_bytes = omitted_lines = duplicate_lines = range_count = 0
    for path, request in selected.items():
        raw = evidence.read_text(root / path, min(evidence.MAX_FILE_BYTES,
                                 evidence.MAX_TOTAL_BYTES - read_bytes))
        read_bytes += len(raw)
        require(evidence.sha(raw) == request["sha256"], "source-changed")
        lines = lf_lines(raw)
        require(all(end <= len(lines) for _, end in request["ranges"]), "line-range-unavailable")
        ranges = merge_ranges(request["ranges"])
        unique_lines = sum(end - start + 1 for start, end in ranges)
        duplicate_lines += sum(end - start + 1 for start, end in request["ranges"]) - unique_lines
        omitted_lines += len(lines) - unique_lines
        excerpts = []
        for start, end in ranges:
            data = b"".join(lines[start - 1:end])
            selected_bytes += len(data)
            excerpts.append({"start_line": start, "end_line": end, "bytes": len(data),
                             "sha256": evidence.sha(data), "text": data.decode("utf-8")})
        range_count += len(excerpts)
        files.append({"path": path, "sha256": request["sha256"], "source_bytes": len(raw),
                      "total_lines": len(lines), "omitted_lines": len(lines) - unique_lines,
                      "excerpts": excerpts})
    # Nothing has been emitted. A later-file failure cannot leak a partial excerpt.
    report = {"format_version": 1, "kind": "selected-source-excerpts", "status": "ready",
              "files": files,
              "measurement": {"unit": "utf8-bytes", "source_bytes_read": read_bytes,
                              "selected_bytes": selected_bytes, "requested_spans": len(spans),
                              "emitted_ranges": range_count, "duplicate_lines_avoided": duplicate_lines,
                              "omitted_lines": omitted_lines, "budget_bytes": budget},
              "limits": {"content_authority": "untrusted-data", "redaction_performed": False,
                         "unselected_files_checked": False, "evidence_sufficient": None,
                         "checks_verified": False, "provider_calls": 0, "model_tokens": None,
                         "snapshot_authenticated": False, "atomic_snapshot": False}}
    if coverage is not None:
        report["required_evidence"] = coverage
    required = len(evidence.encoded(report))
    if required > budget:
        # A small control record may exceed a tiny budget. It contains NO excerpts.
        deferred = {"format_version": 1, "kind": "selected-source-excerpts", "status": "budget-exceeded",
                "files": [], "required_output_bytes": required, "budget_bytes": budget,
                "requested_spans": len(spans), "source_payload_emitted": False,
                "evidence_sufficient": None, "checks_verified": False,
                "next_step": "Review a narrower selection or explicitly raise the byte budget."}
        if coverage is not None:
            deferred["required_evidence"] = {**coverage, "emitted": False}
            deferred["next_step"] = ("Keep declared required spans; remove optional spans or "
                                     "explicitly raise the byte budget.")
        return deferred
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--span", required=True, action="append", nargs=4,
                        metavar=("PATH", "START", "END", "SHA256"),
                        help="reviewed relative text path, inclusive LF line range, expected full-file hash")
    parser.add_argument("--require-span", action="append", nargs=4, dest="required_spans",
                        metavar=("PATH", "START", "END", "SHA256"),
                        help="required evidence the --span selection must cover; never adds reads")
    parser.add_argument("--budget-bytes", type=int, default=DEFAULT_BUDGET)
    args = parser.parse_args()
    if evidence is None:
        print('{"kind":"source-excerpt-error","code":"reader-unavailable"}', file=sys.stderr)
        return 2
    try:
        result = extract(args.root, args.span, args.budget_bytes, required_spans=args.required_spans)
        output = evidence.encoded(result)
    except RequiredEvidenceError:
        print('{"kind":"source-excerpt-error","code":"required-spans-not-covered"}', file=sys.stderr)
        return 2
    except (ExcerptError, evidence.SnapshotError, OSError, ValueError, TypeError, UnicodeError):
        print('{"kind":"source-excerpt-error","code":"invalid-or-stale-input"}', file=sys.stderr)
        return 2
    sys.stdout.buffer.write(output)
    return 1 if result["status"] == "budget-exceeded" else 0


if __name__ == "__main__":
    raise SystemExit(main())
