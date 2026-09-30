#!/usr/bin/env python3
"""Immutable, validated per-unit snapshots for long V46 replays."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_tree(path: Path) -> str:
    if not path.is_dir():
        raise FileNotFoundError(path)
    h = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file() and item.name != "_checkpoint.json"):
        relative = file.relative_to(path).as_posix()
        h.update(relative.encode("utf-8") + b"\0" + sha_file(file).encode("ascii") + b"\n")
    return h.hexdigest()


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Checkpoints:
    def __init__(self, root: Path, identity: dict[str, Any]):
        self.root = root.resolve()
        self.identity_path = self.root / "identity.json"
        if self.identity_path.exists():
            observed = json.loads(self.identity_path.read_text(encoding="utf-8"))
            if observed != identity:
                raise RuntimeError("Run identity drift; create a new run_id instead of resuming")
        else:
            if self.root.exists() and any(self.root.iterdir()):
                raise RuntimeError(f"Refusing to adopt a nonempty unregistered run directory: {root}")
            self.root.mkdir(parents=True, exist_ok=True)
            atomic_json(self.identity_path, identity)

    def checkpoint_path(self, arm: str, unit: int) -> Path:
        if not arm.replace("_", "").isalnum() or unit < 0:
            raise ValueError("invalid arm or unit")
        return self.root / "checkpoints" / arm / f"{unit:03d}"

    def receipt_path(self, arm: str, unit: int) -> Path:
        return self.root / "receipts" / arm / f"{unit:03d}.json"

    def commit(self, arm: str, unit: int, source: Path, receipt: dict[str, Any]) -> Path:
        target = self.checkpoint_path(arm, unit)
        meta = self.receipt_path(arm, unit)
        if target.exists() or meta.exists():
            raise FileExistsError(f"Immutable checkpoint already exists: {arm}/{unit}")
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = target.parent / f".{unit:03d}.{os.getpid()}.{os.urandom(4).hex()}.tmp"
        shutil.copytree(source, staging)
        digest = sha_tree(staging)
        data = {"arm": arm, "unit": unit, "created_at": now(),
                "snapshot_sha256": digest, "receipt": receipt}
        atomic_json(staging / "_checkpoint.json", data)
        os.replace(staging, target)
        atomic_json(meta, data)
        return target

    def validate(self, arm: str, unit: int) -> dict[str, Any]:
        target = self.checkpoint_path(arm, unit)
        meta = self.receipt_path(arm, unit)
        if not target.is_dir():
            raise RuntimeError(f"Incomplete checkpoint: {arm}/{unit}")
        internal = target / "_checkpoint.json"
        if not internal.is_file():
            raise RuntimeError(f"Checkpoint has no internal receipt: {arm}/{unit}")
        data = json.loads(internal.read_text(encoding="utf-8"))
        if meta.is_file() and json.loads(meta.read_text(encoding="utf-8")) != data:
            raise RuntimeError(f"Checkpoint receipt mismatch: {arm}/{unit}")
        if data.get("arm") != arm or data.get("unit") != unit:
            raise RuntimeError(f"Checkpoint label drift: {arm}/{unit}")
        if sha_tree(target) != data.get("snapshot_sha256"):
            raise RuntimeError(f"Checkpoint hash mismatch: {arm}/{unit}")
        if not meta.is_file():
            atomic_json(meta, data)
        return data

    def latest(self, arm: str) -> tuple[int, Path, dict[str, Any]] | None:
        folder = self.root / "checkpoints" / arm
        if not folder.exists():
            return None
        indices = sorted(int(path.name) for path in folder.glob("[0-9][0-9][0-9]") if path.is_dir())
        if not indices:
            return None
        if indices != list(range(indices[-1] + 1)):
            raise RuntimeError(f"Noncontiguous checkpoints for {arm}: {indices}")
        unit = indices[-1]
        data = self.validate(arm, unit)
        return unit, self.checkpoint_path(arm, unit), data

    def attempt(self, arm: str, unit: int, source: Path) -> Path:
        """Copy a valid predecessor into a new attempt; preserve failed attempts."""
        folder = self.root / "attempts" / arm
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / f"{unit:03d}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{os.urandom(3).hex()}"
        shutil.copytree(source, target)
        return target

    def record_error(self, arm: str, unit: int, error: Exception, attempt: Path) -> Path:
        folder = self.root / "errors" / arm
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{unit:03d}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{os.urandom(3).hex()}.json"
        atomic_json(path, {"arm": arm, "unit": unit, "at": now(),
                           "type": type(error).__name__, "message": str(error),
                           "attempt": str(attempt.relative_to(self.root))})
        return path

    def save_stage(self, name: str, result: dict[str, Any]) -> Path:
        path = self.root / "stages" / f"{name}.json"
        if path.exists():
            raise FileExistsError(f"Immutable stage result already exists: {path}")
        atomic_json(path, result)
        return path

    def read_stage(self, name: str) -> dict[str, Any] | None:
        path = self.root / "stages" / f"{name}.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
