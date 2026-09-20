#!/usr/bin/env python3
"""Run the frozen 12-case C33 V34 Redis paired pilot after fail-closed preflight."""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--cohort-file", type=Path, required=True)
    p.add_argument("--work-root", type=Path, required=True)
    p.add_argument("--results-dir", type=Path, required=True)
    p.add_argument("--probe", type=Path, required=True)
    p.add_argument("--answer-model", default="gpt-4o")
    p.add_argument("--judge-model", default="gpt-4o")
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--no-judge", action="store_true")
    args = p.parse_args()

    repo = args.repo.resolve()
    cache = args.cache_dir.resolve()
    cohort_file = args.cohort_file.resolve()
    work_root = args.work_root.resolve()
    results_dir = args.results_dir.resolve()
    probe = args.probe.resolve()

    cohort = json.loads(cohort_file.read_text(encoding="utf-8"))
    cases = cohort.get("cases", [])
    if len(cases) != 12:
        raise RuntimeError(f"Frozen cohort must contain exactly 12 cases, got {len(cases)}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required")

    if results_dir.exists() and any(results_dir.iterdir()) and not args.resume:
        raise RuntimeError("results-dir is non-empty; use a fresh directory or pass --resume")
    results_dir.mkdir(parents=True, exist_ok=True)
    work_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "c33-v34-redis-pilot-run-manifest-v40",
        "started_at": utcnow(),
        "python": platform.python_version(),
        "redis_head": git_head(repo),
        "cohort_file": str(cohort_file),
        "probe": str(probe),
        "answer_model": args.answer_model,
        "judge_model": None if args.no_judge else args.judge_model,
        "top_k": args.top_k,
        "fail_after_successful_sessions": 3,
        "raw_benchmark_text_persisted_in_final_runtime_package": False,
        "retain_work_state": False,
        "cases": [],
    }
    failures = 0

    for case in cases:
        rank = int(case["rank"])
        qid = str(case["question_id"])
        stem = f"case_{rank:02d}_{qid}"
        output = results_dir / f"{stem}.json"
        error_output = results_dir / f"{stem}_error.json"
        if args.resume and output.is_file():
            prior = json.loads(output.read_text(encoding="utf-8"))
            if str(prior.get("question_id")) != qid:
                raise RuntimeError(f"Existing output {output} belongs to another question")
            manifest["cases"].append({"rank": rank, "question_id": qid, "status": "existing"})
            continue

        cmd = [
            sys.executable,
            str(probe),
            "--repo", str(repo),
            "--cache-dir", str(cache),
            "--cohort-file", str(cohort_file),
            "--split", "small",
            "--question-id", qid,
            "--fail-after", "3",
            "--top-k", str(args.top_k),
            "--answer-model", args.answer_model,
            "--work", str(work_root / stem),
            "--output", str(output),
        ]
        if not args.no_judge:
            cmd += ["--with-judge", "--judge-model", args.judge_model]

        started = utcnow()
        proc = subprocess.run(cmd, text=True, capture_output=True)
        stdout_sha = __import__("hashlib").sha256(proc.stdout.encode()).hexdigest()
        stderr_sha = __import__("hashlib").sha256(proc.stderr.encode()).hexdigest()
        entry = {
            "rank": rank,
            "question_id": qid,
            "started_at": started,
            "finished_at": utcnow(),
            "returncode": proc.returncode,
            "output": str(output),
            "stdout_sha256": stdout_sha,
            "stdout_bytes": len(proc.stdout.encode("utf-8")),
            "stderr_sha256": stderr_sha,
            "stderr_bytes": len(proc.stderr.encode("utf-8")),
        }
        if proc.returncode == 0 and output.is_file():
            entry["status"] = "completed"
            if error_output.exists():
                error_output.unlink()
        else:
            failures += 1
            entry["status"] = "failed"
            error_output.write_text(
                json.dumps({
                    "schema": "c33-v34-redis-pilot-case-error-v40",
                    "rank": rank,
                    "question_id": qid,
                    "returncode": proc.returncode,
                    "stdout_sha256": stdout_sha,
                    "stderr_sha256": stderr_sha,
                    "timestamp": utcnow(),
                }, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        # Work state can contain raw benchmark/provider text. The formal package retains only hashed receipts.
        case_work = work_root / stem
        if case_work.exists():
            shutil.rmtree(case_work)
        entry["work_state_deleted_after_case"] = True
        manifest["cases"].append(entry)
        (results_dir / "RUN_MANIFEST_V40.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    manifest["finished_at"] = utcnow()
    manifest["failure_count"] = failures
    manifest["complete"] = failures == 0 and len(manifest["cases"]) == 12
    (results_dir / "RUN_MANIFEST_V40.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"complete": manifest["complete"], "failure_count": failures, "results_dir": str(results_dir)}, indent=2))
    if failures:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
