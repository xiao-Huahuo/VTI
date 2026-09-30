#!/usr/bin/env python3
"""Restore only hash-pinned V58 source dependencies from the tracked source pack.

No network, model, dataset, environment, credential, or experiment call is made.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def project_root() -> Path:
    src = next(parent for parent in Path(__file__).resolve().parents if parent.name == "src")
    return next(parent for parent in src.parents if (parent / "CURRENT_STATE.json").is_file())


def within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_target(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "history":
        raise ValueError(f"Unsafe source target: {relative}")
    target = root.joinpath(*path.parts)
    if not within(target, root):
        raise ValueError(f"Target escapes project: {relative}")
    return target


def package_check(root: Path) -> tuple[dict[str, Any], Path]:
    folder = root / "solutions/v58/frozen_sources"
    manifest = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "science-v58-gpu-source-dependency-pack-v1":
        raise RuntimeError("Unexpected source pack schema")
    for relative, expected in manifest["files_sha256"].items():
        source = folder / "files" / relative
        safe_target(root, relative)
        if not source.is_file() or digest(source) != expected:
            raise RuntimeError(f"Frozen source pack hash mismatch: {relative}")
    bundle_info = manifest["benchmark_git_bundle"]
    bundle = root / bundle_info["path"]
    if not bundle.is_file() or digest(bundle) != bundle_info["sha256"]:
        raise RuntimeError("Frozen benchmark Git bundle hash mismatch")
    if bundle.stat().st_size != bundle_info["bytes"]:
        raise RuntimeError("Frozen benchmark Git bundle size mismatch")
    safe_target(root, bundle_info["restore_target"])
    return manifest, bundle


def target_check(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    missing = []
    mismatch = []
    for relative, expected in manifest["files_sha256"].items():
        target = safe_target(root, relative)
        if not target.is_file():
            missing.append(relative)
        elif digest(target) != expected:
            mismatch.append(relative)
    bundle_info = manifest["benchmark_git_bundle"]
    checkout = safe_target(root, bundle_info["restore_target"])
    commit = None
    if checkout.is_dir():
        result = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            commit = result.stdout.strip()
    if commit != bundle_info["expected_head"]:
        missing.append(bundle_info["restore_target"] + "@" + bundle_info["expected_head"])
    return {"status": "PASS_SOURCE_ONLY" if not missing and not mismatch else "FAIL_SOURCE_MISSING_OR_DRIFT",
            "missing": missing, "mismatch": mismatch, "benchmark_commit": commit,
            "dataset_model_environment_checked": False}


def atomic_copy(source: Path, target: Path, expected: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".v58-source-", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as sink, source.open("rb") as stream:
            shutil.copyfileobj(stream, sink, 1024 * 1024)
            sink.flush()
            os.fsync(sink.fileno())
        staged = Path(name)
        if digest(staged) != expected:
            raise RuntimeError("Staged source hash mismatch")
        os.replace(staged, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def materialize(root: Path, manifest: dict[str, Any], bundle: Path) -> dict[str, Any]:
    folder = root / "solutions/v58/frozen_sources/files"
    for relative, expected in manifest["files_sha256"].items():
        target = safe_target(root, relative)
        if target.exists():
            if not target.is_file() or digest(target) != expected:
                raise RuntimeError(f"Existing frozen source drift: {relative}")
            continue
        atomic_copy(folder / relative, target, expected)

    bundle_info = manifest["benchmark_git_bundle"]
    checkout = safe_target(root, bundle_info["restore_target"])
    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".v58-benchmark-", dir=checkout.parent) as temporary:
            staged = Path(temporary) / "checkout"
            subprocess.run(["git", "clone", "--quiet", str(bundle), str(staged)], check=True)
            subprocess.run(["git", "-C", str(staged), "checkout", "--quiet", "--detach",
                            bundle_info["expected_head"]], check=True)
            observed = subprocess.check_output(["git", "-C", str(staged), "rev-parse", "HEAD"],
                                               text=True).strip()
            if observed != bundle_info["expected_head"]:
                raise RuntimeError("Benchmark commit drift after local bundle clone")
            os.replace(staged, checkout)
    report = target_check(root, manifest)
    if report["status"] != "PASS_SOURCE_ONLY":
        raise RuntimeError(f"Source setup readback failed: {report}")
    outputs = root / "solutions/v58/outputs"
    run_id = "v58-gpu-source-setup-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = outputs / run_id
    run.mkdir(parents=True, exist_ok=False)
    for name in ("raw", "checkpoints", "processed"):
        (run / name).mkdir()
    receipt = {"schema": "science-v58-gpu-source-setup-receipt-v1",
               "at_utc": datetime.now(timezone.utc).isoformat(),
               "status": "PASS_SOURCE_ONLY_DATA_MODEL_ENV_MISSING",
               "source_manifest_sha256": digest(root / "solutions/v58/frozen_sources/MANIFEST.json"),
               "restored_file_count": len(manifest["files_sha256"]),
               "benchmark_commit": report["benchmark_commit"],
               "model_downloads": 0, "environment_installs": 0, "formal_model_calls": 0}
    with (run / "raw/receipt.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--cluster", action="store_true",
                        help="Require the project to reside under ~/projects/srx/")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Verify tracked source pack only")
    mode.add_argument("--verify-only", action="store_true", help="Verify restored source only")
    mode.add_argument("--materialize", action="store_true", help="Restore source from local pack")
    args = parser.parse_args()
    root = (args.project_root or project_root()).resolve()
    if args.cluster and not within(root, Path.home() / "projects/srx"):
        raise SystemExit("Cluster project must be inside ~/projects/srx/")
    manifest, bundle = package_check(root)
    if args.dry_run:
        report = {"status": "PASS_PACK_ONLY", "files": len(manifest["files_sha256"]),
                  "benchmark_bundle_sha256": manifest["benchmark_git_bundle"]["sha256"],
                  "model_downloads": 0, "environment_installs": 0, "formal_model_calls": 0}
    elif args.verify_only:
        report = target_check(root, manifest)
    else:
        report = materialize(root, manifest, bundle)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if str(report["status"]).startswith("FAIL"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
