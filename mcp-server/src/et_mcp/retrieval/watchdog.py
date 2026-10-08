"""
Incremental reindex watchdog (design/03, Q-IDX-1: "watchdog fires continuously").

A lightweight polling watcher — no extra OS-notify dependency. It fingerprints a
set of source dirs (path + mtime + size) and, when the fingerprint changes,
debounces briefly then calls the supplied rebuild function. Runs in a daemon
thread so it never blocks the server.

Kept deliberately simple: for V1 single-user, poll-and-rebuild is sufficient and
robust. A push-based notifier can replace it behind this same interface later.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable, Iterable

logger = logging.getLogger(__name__)


def fingerprint(dirs: Iterable[Path], pattern: str = "*.md") -> tuple:
    items = []
    for d in dirs:
        if not d.exists():
            continue
        for p in sorted(d.rglob(pattern)):
            st = p.stat()
            items.append((str(p), int(st.st_mtime), st.st_size))
    return tuple(items)


class Watchdog:
    def __init__(
        self,
        dirs: Iterable[Path],
        rebuild: Callable[[], object],
        *,
        pattern: str = "*.md",
        interval_s: float = 5.0,
    ):
        self.dirs = [Path(d) for d in dirs]
        self.rebuild = rebuild
        self.pattern = pattern
        self.interval_s = interval_s
        self._last = fingerprint(self.dirs, pattern)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _loop(self) -> None:
        while not self._stop.wait(self.interval_s):
            current = fingerprint(self.dirs, self.pattern)
            if current != self._last:
                logger.info("[watchdog] change detected — reindexing")
                self._last = current
                try:
                    self.rebuild()
                except Exception as exc:  # surface, but keep watching
                    logger.error("[watchdog] reindex failed: %s", exc)

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._loop, name="retrieval-watchdog", daemon=True)
        self._thread.start()
        logger.info("[watchdog] watching %s for %s", [str(d) for d in self.dirs], self.pattern)

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval_s + 1)
            self._thread = None
