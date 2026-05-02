"""Single-flight lock for WSAA token refresh.

A single process must not request two TAs in parallel for the same
service: AFIP rate-limits LoginCms aggressively (it expects you to cache
for the full 12 h). A module-level lock per service serializes the
refresh; readers that find a fresh token in DB don't take the lock.

Threading-safe (FastAPI runs handlers in a thread pool by default).
For multi-process deployments, the DB row itself acts as the source of
truth — concurrent inserts are tolerated because the auth service
always reads the most recent non-expired row.
"""
from __future__ import annotations

import threading

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def lock_for(service: str) -> threading.Lock:
    """Return the lock for a given AFIP service, creating it on demand."""
    lock = _locks.get(service)
    if lock is not None:
        return lock
    with _locks_guard:
        # Double-checked: another thread may have just created it.
        lock = _locks.get(service)
        if lock is None:
            lock = threading.Lock()
            _locks[service] = lock
    return lock


__all__ = ["lock_for"]
