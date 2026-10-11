#!/usr/bin/env python3
"""Generate/check repository-local source-review status; never certify a release.

This snapshot is not a target-project contract or a live capability probe. Evidence
references remain metadata: no remote reads, commands, providers or source pins change.
"""
from __future__ import annotations

import argparse
from datetime import date
from html import escape
from pathlib import Path
import re
import sys

import strict_json

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "registry/capabilities.json"
OUTPUT = ".agentic/docs/project/capability-status.md"
REPOSITORIES = {
    "powerpuff-kitty/agentic-harness",
    "powerpuff-kitty/agentic-harness-agents",
    "powerpuff-kitty/agentic-harness-cli",
}


class StatusError(ValueError):
    """Fixed-code diagnostic, not source content."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise StatusError(code)


def _fields(value: object, names: str) -> None:
    _require(type(value) is dict and set(value) == set(names.split()), "invalid-fields")


def _text(value: object) -> None:
    _require(type(value) is str and 0 < len(value) <= 2048
             and all(ord(c) >= 32 and not 127 <= ord(c) <= 159 for c in value), "invalid-text")


def _id(value: object) -> None:
    _require(type(value) is str and re.fullmatch(r"[a-z][a-z0-9.-]{0,127}", value) is not None,
             "invalid-id")


def _revision(value: object) -> None:
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{40}", value) is not None,
             "invalid-revision")


def _path(value: object) -> None:
    _require(type(value) is str and len(value) <= 512
             and re.fullmatch(r"[A-Za-z0-9_./-]+", value) is not None
             and not any(p in ("", ".", "..") for p in value.split("/")), "invalid-path")


def validate(value: object) -> None:
    """Validate declared snapshot consistency, not the truth of reviewed claims."""
    try:
        strict_json.dumps(value)
    except strict_json.StrictJSONError as error:
        raise StatusError("status-" + str(error)) from None
    _fields(value, "format_version scope reviewed_at sources consumer_pins capabilities")
    _require(type(value["format_version"]) is int and value["format_version"] == 1, "invalid-version")
    _require(value["scope"] == "reviewed-source-snapshot", "invalid-scope")
    _require(type(value["reviewed_at"]) is str
             and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["reviewed_at"]) is not None, "invalid-date")
    try:
        date.fromisoformat(value["reviewed_at"])
    except ValueError:
        raise StatusError("invalid-date") from None
    sources = value["sources"]
    _require(type(sources) is dict and 1 <= len(sources) <= 3, "invalid-sources")
    repositories = set()
    for name, source in sources.items():
        _id(name)
        _fields(source, "repository revision")
        _require(type(source["repository"]) is str and source["repository"] in REPOSITORIES, "unsupported-repository")
        _require(source["repository"] not in repositories, "duplicate-repository")
        repositories.add(source["repository"])
        _revision(source["revision"])
    pins = value["consumer_pins"]
    _require(type(pins) is list and len(pins) <= 16, "invalid-pins")
    pin_ids = set()
    for pin in pins:
        _fields(pin, "consumer upstream revision evidence_path")
        _require(type(pin["consumer"]) is str and type(pin["upstream"]) is str
                 and pin["consumer"] in sources and pin["upstream"] in sources
                 and pin["consumer"] != pin["upstream"], "invalid-pin-owner")
        pair = (pin["consumer"], pin["upstream"])
        _require(pair not in pin_ids, "duplicate-pin")
        pin_ids.add(pair)
        _revision(pin["revision"])
        _path(pin["evidence_path"])
    capabilities = value["capabilities"]
    _require(type(capabilities) is list and 1 <= len(capabilities) <= 128, "invalid-capabilities")
    identifiers = set()
    for item in capabilities:
        _fields(item, "id name owner implementation verification consumer_compatibility release_inclusion evidence limitation issues")
        _id(item["id"])
        _require(item["id"] not in identifiers, "duplicate-capability")
        identifiers.add(item["id"])
        _text(item["name"])
        _text(item["limitation"])
        _require(type(item["owner"]) is str and item["owner"] in sources, "invalid-owner")
        _require(item["implementation"] in ("reference-only", "implemented", "partial", "planned", "unknown"),
                 "invalid-implementation")
        _require(item["verification"] in ("source-reviewed", "not-checked"), "unsupported-verification-claim")
        # This first snapshot cannot represent executed conformance or release evidence.
        # Do not add a positive label without a separately reviewed evidence contract.
        _require(item["consumer_compatibility"] == "not-checked", "unsupported-compatibility-claim")
        _require(item["release_inclusion"] == "not-checked", "unsupported-release-claim")
        refs = item["evidence"]
        _require(type(refs) is list and len(refs) <= 32, "invalid-evidence")
        seen = set()
        for ref in refs:
            _fields(ref, "source path")
            _require(type(ref["source"]) is str and ref["source"] in sources, "invalid-evidence-owner")
            _path(ref["path"])
            pair = (ref["source"], ref["path"])
            _require(pair not in seen, "duplicate-evidence")
            seen.add(pair)
        if item["verification"] == "source-reviewed":
            _require(any(ref["source"] == item["owner"] for ref in refs), "missing-owner-evidence")
        if item["implementation"] in ("reference-only", "implemented", "partial"):
            _require(item["verification"] == "source-reviewed", "missing-source-review")
        issues = item["issues"]
        _require(type(issues) is list and 1 <= len(issues) <= 32, "invalid-issues")
        _require(all(type(n) is int and 0 < n <= 1_000_000 for n in issues), "invalid-issue-number")
        _require(len(set(issues)) == len(issues), "duplicate-issue")


def _cell(text: str) -> str:
    return escape(text).replace("|", "&#124;").replace("`", "&#96;").replace("[", "&#91;").replace("]", "&#93;")


def _link(sources: dict, owner: str, path: str) -> str:
    source = sources[owner]
    return f"https://github.com/{source['repository']}/blob/{source['revision']}/{path}"


def render(value: object) -> str:
    validate(value)
    sources = value["sources"]
    lines = ["# Capability status", "", "<!-- Generated by .github/scripts/capability_status.py; edit registry/capabilities.json. -->", "",
             f"Source review date: {value['reviewed_at']}. This is a historical snapshot, not live status.", "",
             "Source-reviewed means the listed source was reviewed; this generator does not authenticate that review, run consumers, verify a host, or approve a release.", "",
             "## Reviewed revisions", ""]
    for key, source in sorted(sources.items()):
        lines.append(f"- {key}: `{source['repository']}` at `{source['revision']}`.")
    lines += ["", "## Consumer pins", ""]
    for pin in sorted(value["consumer_pins"], key=lambda p: (p["consumer"], p["upstream"])):
        agreement = "same recorded revision" if pin["revision"] == sources[pin["upstream"]]["revision"] else "different recorded revisions"
        lines.append(f"- {pin['consumer']} pins {pin['upstream']} to `{pin['revision']}` ({agreement}); [lock evidence]({_link(sources, pin['consumer'], pin['evidence_path'])}). Compatibility is not checked by revision equality.")
    if not value["consumer_pins"]:
        lines.append("No consumer pin was reviewed.")
    lines += ["", "## Capabilities", "", "| Capability | Owner | Implementation | Verification | Consumer compatibility | Release inclusion |", "| --- | --- | --- | --- | --- | --- |"]
    for item in sorted(value["capabilities"], key=lambda c: c["id"]):
        lines.append("| " + " | ".join(_cell(item[k]) for k in ("name", "owner", "implementation", "verification", "consumer_compatibility", "release_inclusion")) + " |")
    for item in sorted(value["capabilities"], key=lambda c: c["id"]):
        lines += ["", f"### {_cell(item['name'])}", "", _cell(item["limitation"]), ""]
        for ref in sorted(item["evidence"], key=lambda r: (r["source"], r["path"])):
            lines.append(f"Source: [{ref['source']} / {ref['path']}]({_link(sources, ref['source'], ref['path'])}).")
        links = [f"[#{n}](https://github.com/powerpuff-kitty/agentic-harness/issues/{n})" for n in sorted(item["issues"])]
        lines += ["", "Remaining work: " + ", ".join(links) + "."]
    lines += ["", "## Maintenance", "", "Run `python3 .github/scripts/capability_status.py --check` to detect generated-document drift. Use `--write` only after reviewing changes to `registry/capabilities.json`.", "",
              "These commands read only the fixed local snapshot/document paths. They do not fetch referenced evidence or update consumer pins. A trusted, quiescent checkout is assumed; this is not a hostile-filesystem sandbox.", "",
              "Executed consumer conformance and command-documentation synchronization remain #197/#198. A newer source revision requires a new review, not an automatic freshness or release claim.", ""]
    return "\n".join(lines)


def _local_path(root: Path, relative: str) -> Path:
    path = root
    for part in relative.split("/"):
        path = path / part
        _require(not path.is_symlink(), "symlinked-status-path")
    return path


def check(root: Path = ROOT, *, write: bool = False) -> None:
    try:
        with _local_path(root, SOURCE).open("rb") as handle:
            raw = handle.read(strict_json.MAX_BYTES + 1)
        value = strict_json.loads(raw)
        expected = render(value).encode("utf-8")
        output = _local_path(root, OUTPUT)
        if write:
            output.write_bytes(expected)
        else:
            with output.open("rb") as handle:
                actual = handle.read(len(expected) + 1)
            _require(actual == expected, "generated-status-drift")
    except strict_json.StrictJSONError as error:
        raise StatusError("status-" + str(error)) from None
    except OSError:
        raise StatusError("status-file-unavailable") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Check the generated document (default)")
    mode.add_argument("--write", action="store_true", help="Regenerate the fixed local document")
    args = parser.parse_args()
    try:
        check(write=args.write)
    except StatusError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Capability status " + ("generated" if args.write else "checked") + "; source snapshot only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
