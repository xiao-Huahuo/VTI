"""Single-dispatch Ollama receipt transport with conservative request guards."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from journal import Journal, immutable_bytes, immutable_json, sha, utc_now


class BudgetStop(RuntimeError):
    pass


class AmbiguousExternalCall(RuntimeError):
    pass


class ReceiptTransport:
    def __init__(self, journal: Journal, *, max_requests: int, max_input_tokens: int,
                 max_output_tokens: int, max_cost: float, input_reserve_per_request: int = 32768,
                 output_reserve_per_request: int = 2048):
        self.journal = journal
        self.limits = {"requests": max_requests, "input": max_input_tokens,
                       "output": max_output_tokens, "cost": max_cost}
        self.reserve = {"input": input_reserve_per_request, "output": output_reserve_per_request}
        if any(value < 0 for value in self.limits.values()) or max_requests == 0:
            raise ValueError("Positive request and nonnegative token/cost limits required")

    def totals(self) -> dict[str, int | float]:
        totals: dict[str, int | float] = {"requests": 0, "input": 0, "output": 0, "cost": 0.0}
        calls = self.journal.root / "raw/model_calls"
        if not calls.exists():
            return totals
        for path in calls.iterdir():
            if not path.is_dir() or not (path / "dispatched.json").exists():
                continue
            totals["requests"] += 1
            response = path / "response.json"
            if response.exists():
                item = json.loads(response.read_text(encoding="utf-8"))
                totals["input"] += max(int(item.get("prompt_eval_count") or 0), self.reserve["input"])
                totals["output"] += max(int(item.get("eval_count") or 0), self.reserve["output"])
            else:
                totals["input"] += self.reserve["input"]
                totals["output"] += self.reserve["output"]
        return totals

    def _guard(self) -> None:
        totals = self.totals()
        if totals["requests"] + 1 > self.limits["requests"]:
            raise BudgetStop("MAX_REQUESTS reached")
        if totals["input"] + self.reserve["input"] > self.limits["input"]:
            raise BudgetStop("MAX_INPUT_TOKENS conservative reserve reached")
        if totals["output"] + self.reserve["output"] > self.limits["output"]:
            raise BudgetStop("MAX_OUTPUT_TOKENS conservative reserve reached")
        if totals["cost"] > self.limits["cost"]:
            raise BudgetStop("MAX_COST_IF_AVAILABLE reached")

    def call_once(self, client: Any, request: dict[str, Any], *, step: int) -> Any:
        calls = self.journal.root / "raw/model_calls"
        if calls.exists() and any(
            json.loads((folder / "prepared.json").read_text(encoding="utf-8"))["step"] == step
            for folder in calls.iterdir() if folder.is_dir() and (folder / "prepared.json").is_file()
        ):
            raise AmbiguousExternalCall("A request for this operation was already prepared; no resend")
        self._guard()
        call_id = f"{step:05d}-{os.urandom(8).hex()}"
        folder = self.journal.root / "raw/model_calls" / call_id
        folder.mkdir(parents=True)
        body = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        immutable_json(folder / "prepared.json", {"step": step, "request": request,
                                                    "request_sha256": hashlib.sha256(body).hexdigest(),
                                                    "at_utc": utc_now()})
        immutable_json(folder / "dispatched.json", {"step": step, "at_utc": utc_now()})
        raw_capable = hasattr(client, "_request_raw")
        original_raw = client._request_raw if raw_capable else None
        if raw_capable:
            def capture_raw(*args: Any, **kwargs: Any) -> Any:
                response = original_raw(*args, **kwargs)
                immutable_bytes(folder / "raw_http_response.bin", response.content)
                immutable_json(folder / "raw_http_receipt.json",
                               {"step": step, "status_code": response.status_code,
                                "sha256": sha(folder / "raw_http_response.bin"), "at_utc": utc_now()})
                return response
            client._request_raw = capture_raw
        try:
            response = client.chat(**request)
        except BaseException as exc:
            immutable_json(folder / "failure.json", {"step": step, "at_utc": utc_now(),
                                                     "type": type(exc).__name__, "message": str(exc),
                                                     "terminal": True, "retry_allowed": False})
            raise AmbiguousExternalCall("Ollama dispatch failed; automatic retry forbidden") from exc
        finally:
            if raw_capable:
                client._request_raw = original_raw
        if raw_capable and not (folder / "raw_http_response.bin").is_file():
            immutable_json(folder / "failure.json", {"step": step, "at_utc": utc_now(),
                                                     "type": "RawCaptureMissing", "terminal": True,
                                                     "retry_allowed": False})
            raise AmbiguousExternalCall("Ollama response lacked raw HTTP capture; no retry")
        raw = response.model_dump(mode="json") if hasattr(response, "model_dump") else response
        if not isinstance(raw, dict):
            immutable_json(folder / "failure.json", {"step": step, "at_utc": utc_now(),
                                                     "type": "MalformedResponse", "terminal": True,
                                                     "retry_allowed": False})
            raise AmbiguousExternalCall("Malformed Ollama response; automatic retry forbidden")
        if raw_capable and raw.get("model") != request.get("model"):
            immutable_json(folder / "failure.json", {"step": step, "at_utc": utc_now(),
                                                     "type": "ReturnedModelIdentityDrift", "terminal": True,
                                                     "expected_model": request.get("model"),
                                                     "returned_model": raw.get("model"),
                                                     "retry_allowed": False})
            raise AmbiguousExternalCall("Returned model identity drift; no retry")
        immutable_json(folder / "response.json", raw)
        immutable_json(folder / "response_receipt.json", {"step": step,
                                                          "response_sha256": sha(folder / "response.json"),
                                                          "raw_http_captured": raw_capable,
                                                          "at_utc": utc_now()})
        return response
