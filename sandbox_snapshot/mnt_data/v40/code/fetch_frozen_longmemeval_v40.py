#!/usr/bin/env python3
"""Fetch the exact LongMemEval cleaned-S file frozen for the V34 Redis pilot."""
from __future__ import annotations

import argparse
import hashlib
import os
import urllib.request
from pathlib import Path

REVISION = "98d7416c24c778c2fee6e6f3006e7a073259d48f"
FILENAME = "longmemeval_s_cleaned.json"
EXPECTED_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
URL = f"https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/{REVISION}/{FILENAME}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cache-dir", type=Path, required=True)
    args = p.parse_args()
    target = args.cache_dir.resolve() / "longmemeval-v1" / FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and sha256_file(target) == EXPECTED_SHA256:
        print(target)
        return
    tmp = target.with_suffix(target.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()
    request = urllib.request.Request(URL, headers={"User-Agent": "C33-V34-research-pilot/1.0"})
    with urllib.request.urlopen(request, timeout=300) as response, tmp.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    digest = sha256_file(tmp)
    if digest != EXPECTED_SHA256:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"Dataset SHA256 mismatch: expected {EXPECTED_SHA256}, got {digest}")
    os.replace(tmp, target)
    print(target)


if __name__ == "__main__":
    main()
