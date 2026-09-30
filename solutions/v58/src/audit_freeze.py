#!/usr/bin/env python3
"""Read-only, relocation-aware V58 design and prospective amendment audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def src_and_project() -> tuple[Path, Path]:
    src = next(parent for parent in Path(__file__).resolve().parents if parent.name == "src")
    project = next(parent for parent in src.parents if (parent / "CURRENT_STATE.json").is_file())
    return src, project


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_digest(snapshot: Path) -> tuple[str, int]:
    files = sorted(path for path in snapshot.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(snapshot).as_posix().encode() + b"\0")
        digest.update(sha(path).encode() + b"\n")
    return digest.hexdigest(), len(files)


def audit() -> dict:
    src, root = src_and_project()
    old = root / "history/pre_v58_root_20260930"
    old_freeze = old / "study_freeze"
    manifest = read_json(root / "study_freeze/V58_AMENDMENT_MANIFEST_20260930.json")
    original = read_json(old_freeze / "FREEZE_MANIFEST.json")
    v58 = read_json(old_freeze / "V58_POLICY_ORDER.json")
    amendment = read_json(root / "study_freeze/V58_PRIMARY_METRIC_AMENDMENT_20260930.json")
    v55_manifest = read_json(root / "history/v55_formal/FINAL_PRE_EXECUTION_MANIFEST.json")
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("amendment_manifest_files", all(
        (root / item["path"]).is_file() and sha(root / item["path"]) == item["sha256"]
        for item in manifest["files"].values()
    ))
    check("original_freeze_design_files", all(
        sha(old_freeze / name) == expected
        for name, expected in original["files_sha256"].items()
    ))
    check("original_freeze_source", sha(old / "docs/proposals/THREE_BLOCK_FINAL_SOURCE_20260930.txt") == original["source_sha256"])
    check("original_freeze_generator", sha(old_freeze / "create_design_freeze.py") == original["generator_sha256"])
    check("original_freeze_status", original["status"] == "DESIGN_FROZEN_EXECUTION_BLOCKED")

    cases = {case["symbol"]: case for case in v58["cases"]}
    check("four_frozen_cases", set(cases) == set("ABCD") and
          [(c["rank"], c["question_id"], c["sessions"]) for c in v58["cases"]] == [
              (29, "gpt4_ec93e27f", 47), (30, "gpt4_45189cb4", 45),
              (31, "08f4fc43", 47), (32, "e8a79c70", 44)])
    orders = [block["order"] for block in v58["blocks"]]
    check("12_unique_valid_orders", len(orders) == len(set(orders)) == 12 and
          all(sorted(order) == list("ABCD") for order in orders))
    check("frozen_block_numbers", [block["block"] for block in v58["blocks"]] == list(range(1, 13)))
    check("12_N_V_pairs", all({block["slot1"], block["slot2"]} == {"N", "V"} for block in v58["blocks"]))
    cells = Counter((order[i - 1], order[i], i + 1) for order in orders for i in (1, 2, 3))
    positions = Counter((letter, i + 1) for order in orders for i, letter in enumerate(order))
    check("36_of_36_exact_cover", len(cells) == 36 and set(cells.values()) == {1})
    check("all_case_positions_three_times", len(positions) == 16 and set(positions.values()) == {3})
    check("24_sequences_96_trials", len(v58["blocks"]) * 2 == 24 and len(v58["blocks"]) * 2 * 4 == 96)
    check("4096_assignments", 2 ** len(v58["blocks"]) == 4096)

    frozen_engine = root / "history/v45/code/redis_v45_ollama_deterministic_gate.py"
    check("v45_engine_hash", sha(frozen_engine) == v55_manifest["files_sha256"]["history/v45/code/redis_v45_ollama_deterministic_gate.py"])
    check("v55_source_hashes", all(
        sha(root / "history" / name) == v55_manifest["files_sha256"][name]
        for name in ("v55_formal/code/run_v55.py", "v55_formal/code/checkpoint.py", "v55_formal/code/schema.py")
    ))
    engine_text = frozen_engine.read_text(encoding="utf-8")
    check("frozen_retrieval_text_rule", 'row.get("memory") or row.get("text") or row.get("data") or ""' in engine_text)
    v55_text = (root / "history/v55_formal/code/run_v55.py").read_text(encoding="utf-8")
    check("v55_search_path", 'search(qa.question, filters={"user_id": user_id}, top_k=TOP_K)' in v55_text and
          'search_rows = v45.normalize_results(search_raw)' in v55_text and 'v45.text_hashes_in_order(search_rows)' in v55_text)
    check("footprint_copy_byte_identity", sha(src / "retrieval_footprint.py") == amendment["representation"]["source_code_sha256"])
    check("footprint_original_byte_identity", sha(old / "v57_design/code/retrieval_footprint.py") == amendment["representation"]["source_code_sha256"])

    asset = amendment["embedding_asset"]
    asset_record = read_json(old / "v57_design/DOWNLOADABLE_ASSETS.json")["measurement_embedding"]
    check("embedding_record_matches_amendment", all((
        asset_record["fastembed_version"] == asset["fastembed_version"],
        asset_record["hf_repo"] == asset["hf_repo"],
        asset_record["observed_hf_revision"] == asset["observed_revision"],
        asset_record["snapshot_tree_sha256"] == asset["snapshot_tree_sha256"],
        asset_record["fastembed_name"] == amendment["representation"]["embedding_name"],
        asset_record["dims"] == amendment["representation"]["embedding_dimensions"],
        v55_manifest["runtime_versions"]["fastembed"] == asset["fastembed_version"],
    )))
    snapshot = old / ".runtime/fastembed-cache/models--Qdrant--bge-small-en-v1.5-onnx-Q/snapshots" / asset["observed_revision"]
    digest, file_count = snapshot_digest(snapshot) if snapshot.is_dir() else (None, 0)
    check("embedding_snapshot_tree", file_count == 5 and digest == asset["snapshot_tree_sha256"])

    dataset = src.parent / "inputs/longmemeval-v1/longmemeval_s_cleaned.json"
    check("dataset_hash", dataset.is_file() and sha(dataset) == original["dataset_sha256"])
    if checks["dataset_hash"]:
        rows = {row["question_id"]: row for row in read_json(dataset)}
        check("dataset_case_session_binding", all(
            case["question_id"] in rows and len(rows[case["question_id"]]["haystack_sessions"]) == case["sessions"]
            for case in cases.values()
        ))
    else:
        check("dataset_case_session_binding", False)

    check("prospective_status", amendment["pre_amendment_formal_runs"] == 0 and
          amendment["pre_amendment_formal_model_calls"] == 0 and amendment["pre_amendment_formal_outcomes_observed"] == 0)
    check("unique_metric_binding", amendment["representation"]["name"] == "Ordered Top-5 Retrieval Footprint" and
          amendment["representation"]["output_dimensions"] == 1925 and
          amendment["representation"]["output_dtype"] == "float32" and
          amendment["distance"]["name"] == "Euclidean L2" and
          amendment["distance"]["conversion_before_distance"] == "both float32 footprints to float64")
    check("unchanged_inference", "4096" in amendment["unchanged_primary"]["randomization"] and
          amendment["unchanged_primary"]["p_value"] == "count(permuted_delta>=observed_delta-1e-12)/4096" and
          amendment["unchanged_primary"]["decision"] == "delta>0 and p<0.05")

    return {
        "schema": "science-v58-post-amendment-freeze-audit-v1",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(checks.values()) else "FAIL_CLOSED",
        "checks": checks,
        "check_count": len(checks),
        "passed_count": sum(checks.values()),
        "amendment_sha256": sha(root / "study_freeze/V58_PRIMARY_METRIC_AMENDMENT_20260930.json"),
        "amendment_manifest_sha256": sha(root / "study_freeze/V58_AMENDMENT_MANIFEST_20260930.json"),
        "footprint_sha256": sha(src / "retrieval_footprint.py"),
        "embedding_snapshot_sha256": digest,
        "embedding_snapshot_file_count": file_count,
        "model_calls": 0,
        "formal_run_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output is None:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(f"{result['status']}: {result['passed_count']}/{result['check_count']} checks -> {args.output}")
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
