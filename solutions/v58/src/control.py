"""Cooperative pause requests; mutable UI state is separate from scientific raw receipts."""
from __future__ import annotations

import json
import os
import tempfile
import threading
import uuid
from pathlib import Path
from typing import Any

from journal import immutable_json, utc_now

STOP_REQUESTED = threading.Event()
PAUSED_EXIT = 75


class SafePause(RuntimeError):
    pass


def status(root: Path, **fields: Any) -> None:
    folder = root / "control"
    folder.mkdir(parents=True, exist_ok=True)
    payload = {"at_utc": utc_now(), "pid": os.getpid(), **fields}
    fd, temporary = tempfile.mkstemp(prefix=".status-", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, folder / "status.json")
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def request_pause(root: Path, source: str = "user") -> dict[str, Any]:
    if not root.is_dir() or not (root / "raw").is_dir():
        raise FileNotFoundError("Run or batch has not been created")
    path = root / "control/pause.request.json"
    try:
        immutable_json(path, {"requested_at_utc": utc_now(), "source": source})
    except FileExistsError:
        pass
    return json.loads(path.read_text(encoding="utf-8"))


def requested(*roots: Path) -> bool:
    return STOP_REQUESTED.is_set() or any((root / "control/pause.request.json").exists() for root in roots)


def clear_pause(root: Path) -> None:
    path = root / "control/pause.request.json"
    if path.exists():
        history = root / "control/history"
        history.mkdir(parents=True, exist_ok=True)
        os.replace(path, history / f"resumed-{uuid.uuid4().hex}.json")


def checkpoint_pause(root: Path, step: int, **fields: Any) -> None:
    immutable_json(root / "control/history" / f"paused-{uuid.uuid4().hex}.json",
                   {"at_utc": utc_now(), "last_committed_step": step, **fields})
    status(root, phase="PAUSED", last_committed_step=step, **fields)
    raise SafePause(f"Paused safely after checkpoint {step}")
