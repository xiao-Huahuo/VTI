#!/usr/bin/env python3
"""Preflight validator for the V32 Redis × Mem0 2.0.19 exact paired replay."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

REDIS_COMMIT = "94192c39e2a4a154f441a5411e3d73c4f54974a6"
MEM0_VERSION = "2.0.19"
SUPPORTED = {(3, 10), (3, 11), (3, 12)}


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


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    py = (sys.version_info.major, sys.version_info.minor)
    repo = args.repo.resolve()
    cache_dir = args.cache_dir.resolve() if args.cache_dir else None
    checks = {
        "python_supported": py in SUPPORTED,
        "redis_repo_exists": repo.is_dir(),
        "redis_commit_matches": git_head(repo) == REDIS_COMMIT,
        "mem0_version_matches": package_version("mem0ai") == MEM0_VERSION,
        "qdrant_client_installed": package_version("qdrant-client") is not None,
        "openai_installed": package_version("openai") is not None,
        "openai_api_key_present": bool(os.environ.get("OPENAI_API_KEY")),
        "cache_dir_exists_or_unspecified": cache_dir is None or cache_dir.exists(),
    }
    result = {
        "schema": "redis-exact-preflight-v32",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "redis_head": git_head(repo),
        "expected_redis_commit": REDIS_COMMIT,
        "mem0ai_version": package_version("mem0ai"),
        "expected_mem0ai_version": MEM0_VERSION,
        "qdrant_client_version": package_version("qdrant-client"),
        "openai_version": package_version("openai"),
        "checks": checks,
        "ready": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
