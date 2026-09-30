"""Immutable V58 raw receipts and copy-on-commit state snapshots."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def tree_sha(path: Path) -> str:
    if not path.is_dir():
        raise FileNotFoundError(path)
    value = hashlib.sha256()
    for item in sorted(x for x in path.rglob("*") if x.is_file() and x.name != "_checkpoint.json"):
        value.update(item.relative_to(path).as_posix().encode() + b"\0" + sha(item).encode() + b"\n")
    return value.hexdigest()


def immutable_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_dir(path.parent)


def immutable_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_dir(path.parent)


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Journal:
    def __init__(self, root: Path, identity: dict[str, Any], *, resume: bool):
        self.root = root.resolve()
        self.identity = identity
        identity_path = self.root / "raw/identity.json"
        if resume:
            if not identity_path.is_file() or json.loads(identity_path.read_text()) != identity:
                raise RuntimeError("Missing or mismatched run identity; resume rejected")
        else:
            if self.root.exists():
                raise FileExistsError("run_id already exists")
            self.root.mkdir(parents=True)
            for name in ("raw", "checkpoints", "processed"):
                (self.root / name).mkdir()
            immutable_json(identity_path, identity)

    def checkpoint_path(self, step: int) -> Path:
        return self.root / "checkpoints" / f"{step:05d}"

    def commit(self, step: int, source: Path, receipt: dict[str, Any]) -> Path:
        if step < 0 or self.checkpoint_path(step).exists():
            raise FileExistsError("checkpoint step already committed or invalid")
        if step > 0:
            self.validate(step - 1)
        elif any(self.root.joinpath("checkpoints").iterdir()):
            raise RuntimeError("initial checkpoint is not first")
        stage = Path(tempfile.mkdtemp(prefix=f".{step:05d}.", dir=self.root / "checkpoints"))
        try:
            shutil.copytree(source, stage / "state")
            state_hash = tree_sha(stage / "state")
            payload = {"step": step, "at_utc": utc_now(), "state_sha256": state_hash,
                       "identity_sha256": sha(self.root / "raw/identity.json"), "receipt": receipt}
            immutable_json(stage / "_checkpoint.json", payload)
            _fsync_dir(stage)
            os.replace(stage, self.checkpoint_path(step))
            _fsync_dir(self.root / "checkpoints")
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        return self.checkpoint_path(step)

    def validate(self, step: int) -> dict[str, Any]:
        path = self.checkpoint_path(step)
        marker = path / "_checkpoint.json"
        if not marker.is_file():
            raise RuntimeError(f"Missing completion marker at step {step}")
        item = json.loads(marker.read_text(encoding="utf-8"))
        if item["step"] != step or item["identity_sha256"] != sha(self.root / "raw/identity.json"):
            raise RuntimeError("Checkpoint identity mismatch")
        if tree_sha(path / "state") != item["state_sha256"]:
            raise RuntimeError("Checkpoint state corruption")
        return item

    def latest(self) -> tuple[int, Path, dict[str, Any]] | None:
        entries = sorted(x for x in (self.root / "checkpoints").iterdir() if x.is_dir() and x.name.isdigit())
        if not entries:
            return None
        numbers = [int(x.name) for x in entries]
        if numbers != list(range(numbers[-1] + 1)):
            raise RuntimeError("Noncontiguous checkpoint chain")
        for step in numbers:
            self.validate(step)
        last = numbers[-1]
        return last, self.checkpoint_path(last) / "state", self.validate(last)

    def create_attempt(self, step: int, source: Path) -> Path:
        attempt = self.root / "raw/attempts" / f"{step:05d}-{os.getpid()}-{os.urandom(4).hex()}"
        attempt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, attempt)
        return attempt

    def begin_step(self, step: int, kind: str) -> None:
        immutable_json(self.root / "raw/operations" / f"{step:05d}.json",
                       {"step": step, "kind": kind, "started_at_utc": utc_now()})

    def ensure_no_pending_calls(self, committed_step: int) -> None:
        calls = self.root / "raw/model_calls"
        if calls.exists():
            for path in calls.iterdir():
                if not path.is_dir():
                    continue
                prepared = json.loads((path / "prepared.json").read_text(encoding="utf-8"))
                body = json.dumps(prepared["request"], ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":")).encode()
                if hashlib.sha256(body).hexdigest() != prepared["request_sha256"]:
                    raise RuntimeError("Raw request hash mismatch")
                if (path / "dispatched.json").exists() and (
                    not (path / "response.json").exists() or prepared["step"] > committed_step
                ):
                    raise RuntimeError("Uncommitted or ambiguous dispatched request; automatic resume forbidden")
                if (path / "response.json").exists():
                    receipt = path / "response_receipt.json"
                    if not receipt.is_file() or json.loads(receipt.read_text())["response_sha256"] != sha(path / "response.json"):
                        raise RuntimeError("Raw response hash mismatch")
                raw_http = path / "raw_http_response.bin"
                if raw_http.exists():
                    receipt = path / "raw_http_receipt.json"
                    if not receipt.is_file() or json.loads(receipt.read_text())["sha256"] != sha(raw_http):
                        raise RuntimeError("Raw HTTP response hash mismatch")
        operations = self.root / "raw/operations"
        if operations.exists() and any(int(path.stem) > committed_step for path in operations.glob("[0-9]*.json")):
            raise RuntimeError("Uncommitted operation; automatic resume forbidden")

    def readback(self) -> dict[str, Any]:
        latest = self.latest()
        if latest is None:
            return {"status": "NO_CHECKPOINT", "checkpoints": 0}
        self.ensure_no_pending_calls(latest[0])
        return {"status": "PASS", "checkpoints": latest[0] + 1,
                "last_state_sha256": latest[2]["state_sha256"]}
