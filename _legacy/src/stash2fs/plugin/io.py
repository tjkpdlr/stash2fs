"""Stash plugin stderr log protocol."""

from __future__ import annotations

import json
import sys
from typing import Any


def _prefix(level_char: bytes) -> str:
    return (b"\x01" + level_char + b"\x02").decode()


def _emit(level_char: bytes, message: str) -> None:
    print(_prefix(level_char) + message + "\n", file=sys.stderr, flush=True)


class StashLogSink:
    """Log via Stash's SOH+level+STX stderr protocol."""

    def trace(self, msg: str) -> None:
        _emit(b"t", msg)

    def debug(self, msg: str) -> None:
        _emit(b"d", msg)

    def info(self, msg: str) -> None:
        _emit(b"i", msg)

    def warning(self, msg: str) -> None:
        _emit(b"w", msg)

    def error(self, msg: str) -> None:
        _emit(b"e", msg)

    def progress(self, fraction: float) -> None:
        progress = min(max(0.0, fraction), 1.0)
        _emit(b"p", str(progress))


def read_fragment() -> dict[str, Any]:
    raw = sys.stdin.read()
    data: dict[str, Any] = json.loads(raw)
    return data
