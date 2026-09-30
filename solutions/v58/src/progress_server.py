#!/usr/bin/env python3
"""Loopback-only V58 progress dashboard with a cooperative pause control."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from audit_freeze import src_and_project
from control import request_pause
from machine_metrics import collect

SRC, PROJECT = src_and_project()
OUTPUTS = SRC.parent / "outputs"
HTML = SRC / "progress.html"
TOKEN = secrets.token_urlsafe(32)


def read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def simple(value: str) -> str:
    if not value or not value.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid identifier")
    return value


def progress(batch_id: str | None = None) -> dict:
    state = read(PROJECT / "CURRENT_STATE.json")
    controllers = [p for p in OUTPUTS.glob("v58-*-controller")
                   if "global_budget" in read(p / "raw/batch_identity.json")]
    if batch_id:
        controller = OUTPUTS / f"v58-{simple(batch_id)}-controller"
        if controller not in controllers:
            controller = None
    else:
        controller = max(controllers, key=lambda p: (p / "raw/batch_identity.json").stat().st_mtime, default=None)
    selected = read(controller / "raw/batch_identity.json").get("batch_id") if controller else None
    rows = []
    total_sessions = 0
    requests = 0
    completed = 0
    if selected:
        for block in range(1, 13):
            for slot in (1, 2):
                run_id = f"v58-{selected}-b{block:02d}-s{slot}"
                root = OUTPUTS / run_id
                info = read(root / "raw/identity.json")
                markers = sorted(root.glob("checkpoints/[0-9]*/_checkpoint.json"))
                latest = read(markers[-1]) if markers else {}
                last_step = int(latest.get("step", 0))
                # Fixed four-case session counts; count from immutable operation markers,
                # without hashing or opening Qdrant snapshots on every UI refresh.
                session_count = sum(read(path).get("kind") == "ingest" and int(path.stem) <= last_step
                                    for path in root.glob("raw/operations/[0-9]*.json"))
                calls = len(list(root.glob("raw/model_calls/*/dispatched.json")))
                status = read(root / "control/status.json")
                done = (root / "raw/sequence_complete.json").exists()
                phase = "COMPLETE" if done else status.get("phase", "WAITING" if not info else "NEEDS_READBACK")
                if phase == "RUNNING" and status.get("pid"):
                    try:
                        os.kill(int(status["pid"]), 0)
                    except (OSError, ValueError):
                        phase = "NEEDS_READBACK"
                rows.append({"run_id": run_id, "block": block, "slot": slot, "policy": info.get("policy"),
                             "phase": phase, "sessions": session_count, "total_sessions": 183,
                             "last_step": last_step, "model_requests": calls,
                             "operation": status.get("operation"),
                             "pause_requested": (root / "control/pause.request.json").exists()})
                total_sessions += session_count
                requests += calls
                completed += int(done)
    controller_status = read(controller / "control/status.json") if controller else {}
    return {"batch_id": selected, "phase": controller_status.get("phase", "NOT_STARTED"),
            "pause_requested": bool(controller and (controller / "control/pause.request.json").exists()),
            "active_run_id": controller_status.get("active_run_id"), "sequences": rows,
            "completed_sessions": total_sessions, "total_sessions": 4392,
            "completed_sequences": completed, "total_sequences": 24, "model_requests": requests,
            "regulatory_state": state.get("v58_execution_gates", {}).get("regulatory_state"),
            "formal_model_calls_recorded": state.get("v58_execution_gates", {}).get("formal_model_calls", 0)}


class MetricsCache:
    def __init__(self):
        self.value = {"sampled_at_utc": None, "loading": True}
        self.lock = threading.Lock()

    def loop(self):
        while True:
            try:
                value = collect(PROJECT)
                with self.lock:
                    self.value = value
            except Exception as exc:
                with self.lock:
                    self.value = {"error": type(exc).__name__, "sampled_at_utc": datetime.now(timezone.utc).isoformat()}
            time.sleep(4)

    def snapshot(self):
        with self.lock:
            return dict(self.value)


METRICS = MetricsCache()


class Handler(BaseHTTPRequestHandler):
    def reply(self, body: bytes, content_type: str):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.reply(HTML.read_text().replace("__CONTROL_TOKEN__", TOKEN).encode(), "text/html; charset=utf-8")
        elif self.path == "/api/status":
            self.reply(json.dumps({"progress": progress(self.server.batch_id), "machine": METRICS.snapshot()},
                                  ensure_ascii=False).encode(), "application/json; charset=utf-8")
        elif self.path == "/api/health":
            self.reply(b'{"service":"v58-progress","model_calls":0}', "application/json")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/pause" or self.headers.get("X-Control-Token") != TOKEN:
            self.send_error(403)
            return
        expected = f"http://127.0.0.1:{self.server.server_port}"
        if self.headers.get("Origin") not in (None, expected):
            self.send_error(403)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1024:
                raise ValueError("Request too large")
            body = json.loads(self.rfile.read(length))
            active = progress(self.server.batch_id)["batch_id"]
            if not active or body.get("batch_id") != active:
                raise ValueError("No matching formal batch")
            event = request_pause(OUTPUTS / f"v58-{simple(active)}-controller", "dashboard")
            self.reply(json.dumps({"status": "PAUSE_REQUESTED", **event}).encode(), "application/json")
        except (ValueError, OSError):
            self.send_error(409, "No running batch or invalid request")

    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8773)
    parser.add_argument("--batch-id")
    args = parser.parse_args()
    if args.batch_id:
        simple(args.batch_id)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.batch_id = args.batch_id
    threading.Thread(target=METRICS.loop, daemon=True).start()
    print(f"V58 dashboard: http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
