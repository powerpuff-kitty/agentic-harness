#!/usr/bin/env python3
"""Bounded JSON values/bytes for reference inspectors; no acquisition or authority.

Only exact built-in JSON types are accepted. This is a transport boundary, not
schema validation or authentication. Duplicate keys are detectable only when the
original bytes/text pass through loads(), not after another decoder discarded them.
"""
from __future__ import annotations

import json
import math

MAX_BYTES = 262_144
MAX_DEPTH = 32
MAX_NODES = 32_768


class StrictJSONError(ValueError):
    """Fixed-code diagnostic that never includes the supplied content."""


def _limit(value: int) -> None:
    if type(value) is not int or not 0 < value <= MAX_BYTES:
        raise StrictJSONError("invalid-byte-limit")


def _validate(value: object, max_bytes: int) -> None:
    active: set[int] = set()
    nodes = 0
    text_bytes = 0

    def visit(item: object, depth: int) -> None:
        nonlocal nodes, text_bytes
        nodes += 1
        if nodes > MAX_NODES:
            raise StrictJSONError("node-limit-exceeded")
        if depth > MAX_DEPTH:
            raise StrictJSONError("depth-limit-exceeded")
        kind = type(item)
        if item is None or kind in (bool, int):
            return
        if kind is float:
            if not math.isfinite(item):
                raise StrictJSONError("non-finite-number")
            return
        if kind is str:
            if len(item) > max_bytes:
                raise StrictJSONError("size-limit-exceeded")
            try:
                text_bytes += len(item.encode("utf-8"))
            except UnicodeError:
                raise StrictJSONError("invalid-utf8") from None
            if text_bytes > max_bytes:
                raise StrictJSONError("size-limit-exceeded")
            return
        if kind not in (dict, list):
            raise StrictJSONError("unsupported-json-type")
        if id(item) in active:
            raise StrictJSONError("cyclic-input")
        if len(item) > MAX_NODES:
            raise StrictJSONError("node-limit-exceeded")
        active.add(id(item))
        try:
            if kind is dict:
                for key, child in item.items():
                    if type(key) is not str:
                        raise StrictJSONError("non-string-object-key")
                    visit(key, depth + 1)
                    visit(child, depth + 1)
            else:
                for child in item:
                    visit(child, depth + 1)
        finally:
            active.remove(id(item))

    visit(value, 0)


def dumps(value: object, *, max_bytes: int = MAX_BYTES) -> bytes:
    """Return deterministic UTF-8 JSON or a fixed-code error; preserve the input."""
    _limit(max_bytes)
    _validate(value, max_bytes)
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False)
    parts: list[bytes] = []
    size = 0
    try:
        for chunk in encoder.iterencode(value):
            data = chunk.encode("utf-8")
            size += len(data)
            if size > max_bytes:
                raise StrictJSONError("size-limit-exceeded")
            parts.append(data)
    except StrictJSONError:
        raise
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError):
        raise StrictJSONError("invalid-json-value") from None
    return b"".join(parts)


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError("duplicate-object-key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise StrictJSONError("non-finite-number")


def loads(raw: bytes | str, *, max_bytes: int = MAX_BYTES) -> object:
    """Decode explicit UTF-8 input only; do not read files or follow references."""
    _limit(max_bytes)
    if type(raw) not in (bytes, str):
        raise StrictJSONError("unsupported-json-input")
    if len(raw) > max_bytes:
        raise StrictJSONError("size-limit-exceeded")
    try:
        if type(raw) is bytes:
            text = raw.decode("utf-8")
        else:
            text = raw
        if len(text.encode("utf-8")) > max_bytes:
            raise StrictJSONError("size-limit-exceeded")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except StrictJSONError:
        raise
    except UnicodeError:
        raise StrictJSONError("invalid-utf8") from None
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise StrictJSONError("invalid-json-input") from None
    # Also rejects finite syntax such as 1e9999 that float decoding overflowed.
    dumps(value, max_bytes=max_bytes)
    return value
