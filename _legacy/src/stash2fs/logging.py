"""Logging adapter for CLI and plugin contexts."""

from __future__ import annotations

import logging
import sys
from typing import Protocol


class LogSink(Protocol):
    def trace(self, msg: str) -> None: ...
    def debug(self, msg: str) -> None: ...
    def info(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...
    def progress(self, fraction: float) -> None: ...


class PythonLogSink:
    """Standard Python logging to stderr."""

    def __init__(self, level: str = "INFO") -> None:
        numeric = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=numeric,
            format="%(levelname)s: %(message)s",
            stream=sys.stderr,
            force=True,
        )
        self._logger = logging.getLogger("stash2fs")

    def trace(self, msg: str) -> None:
        self._logger.debug(msg)

    def debug(self, msg: str) -> None:
        self._logger.debug(msg)

    def info(self, msg: str) -> None:
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        self._logger.error(msg)

    def progress(self, fraction: float) -> None:
        self._logger.info("Progress: %.0f%%", fraction * 100)


_sink: LogSink | None = None


def configure_logging(sink: LogSink) -> None:
    global _sink
    _sink = sink


def get_logger() -> LogSink:
    if _sink is None:
        configure_logging(PythonLogSink())
    assert _sink is not None
    return _sink
