#!/usr/bin/env python3
"""Fail-closed preflight for the frozen C33 V34 Redis formal pilot."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

REDIS_COMMIT = "94192c39e2a4a154f441a5411e3d73c4f54974a6"
MEM0_VERSION = "2.0.19"
DATASET_FILE = "longmemeval_s_cleaned.json"
DATASET_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
SUPPORTED = {(3, 10), (3, 11), (3, 12)}
SELECTION_PREFIX = "C33-V34-REDIS|"
N = 12
MIN_SESSIONS = 4
FAIL_AFTER = 3


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_head(repo: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def load_rows(path: Path) -> list[dict[str, Any]] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, list) else None


def derive_cohort(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = []
    for row in rows:
        qid = str(row.get("question_id"))
        sessions = row.get("haystack_sessions")
        if not isinstance(sessions, list) or len(sessions) < MIN_SESSIONS:
            continue
        eligible.append({
            "question_id": qid,
            "question_type": str(row.get("question_type")),
            "session_count": len(sessions),
            "selection_sha256": hashlib.sha256((SELECTION_PREFIX + qid).encode("utf-8")).hexdigest(),
        })
    eligible.sort(key=lambda x: x["selection_sha256"])
    return eligible[:N]


def normalize_frozen(cohort: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "question_id": str(x["question_id"]),
            "question_type": str(x["question_type"]),
            "session_count": int(x["session_count"]),
            "selection_sha256": str(x["selection_sha256"]),
        }
        for x in cohort.get("cases", [])
    ]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--cohort-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    repo = args.repo.resolve()
    cache_dir = args.cache_dir.resolve()
    cohort_file = args.cohort_file.resolve()
    dataset_path = cache_dir / "longmemeval-v1" / DATASET_FILE
    py = (sys.version_info.major, sys.version_info.minor)

    try:
        cohort = json.loads(cohort_file.read_text(encoding="utf-8"))
    except Exception:
        cohort = {}
    rows = load_rows(dataset_path)
    derived = derive_cohort(rows) if rows is not None else []
    frozen = normalize_frozen(cohort) if cohort else []

    session_counts = []
    if rows is not None:
        session_counts = [len(r.get("haystack_sessions", [])) for r in rows if isinstance(r.get("haystack_sessions"), list)]
    eligible_count = sum(1 for n in session_counts if n >= MIN_SESSIONS)

    checks = {
        "python_supported": py in SUPPORTED,
        "redis_repo_exists": repo.is_dir(),
        "redis_commit_matches": git_head(repo) == REDIS_COMMIT,
        "mem0_version_matches": package_version("mem0ai") == MEM0_VERSION,
        "qdrant_client_installed": package_version("qdrant-client") is not None,
        "openai_installed": package_version("openai") is not None,
        "openai_api_key_present": bool(os.environ.get("OPENAI_API_KEY")),
        "cohort_file_valid": len(frozen) == N,
        "dataset_file_present": dataset_path.is_file(),
        "dataset_sha256_matches": sha256_file(dataset_path) == DATASET_SHA256,
        "dataset_row_count_500": rows is not None and len(rows) == 500,
        "eligible_count_500": eligible_count == 500,
        "cohort_recomputed_matches_frozen": derived == frozen,
        "fault_point_valid_for_all_cases": bool(frozen) and all(x["session_count"] > FAIL_AFTER for x in frozen),
    }
    result = {
        "schema": "c33-v34-redis-preflight-v40",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "redis_head": git_head(repo),
        "expected_redis_commit": REDIS_COMMIT,
        "mem0ai_version": package_version("mem0ai"),
        "expected_mem0ai_version": MEM0_VERSION,
        "qdrant_client_version": package_version("qdrant-client"),
        "openai_version": package_version("openai"),
        "dataset_path": str(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "expected_dataset_sha256": DATASET_SHA256,
        "dataset_row_count": len(rows) if rows is not None else None,
        "eligible_count": eligible_count if rows is not None else None,
        "session_count_min": min(session_counts) if session_counts else None,
        "session_count_max": max(session_counts) if session_counts else None,
        "frozen_cohort_question_ids": [x["question_id"] for x in frozen],
        "derived_cohort_question_ids": [x["question_id"] for x in derived],
        "checks": checks,
        "ready": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
