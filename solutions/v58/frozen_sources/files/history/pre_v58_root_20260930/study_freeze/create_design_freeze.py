#!/usr/bin/env python3
"""One-time, offline materialization of the user-approved V57–V59 design.

This script refuses to overwrite an existing freeze. It makes no model calls.
"""
from __future__ import annotations

import hashlib
import json
import random
import secrets
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "study_freeze"
SOURCE = ROOT / "docs/proposals/THREE_BLOCK_FINAL_SOURCE_20260930.txt"
DATA = Path.home() / ".cache/agent-memory-benchmark/longmemeval-v1/longmemeval_s_cleaned.json"
EXPECTED_DATA_SHA = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"

V58_CASES = [
    {"symbol": "A", "rank": 29, "question_id": "gpt4_ec93e27f", "sessions": 47},
    {"symbol": "B", "rank": 30, "question_id": "gpt4_45189cb4", "sessions": 45},
    {"symbol": "C", "rank": 31, "question_id": "08f4fc43", "sessions": 47},
    {"symbol": "D", "rank": 32, "question_id": "e8a79c70", "sessions": 44},
]
ORDERS = ["CBAD", "BCDA", "ABDC", "ACBD", "CADB", "BACD",
          "ADCB", "DABC", "DCAB", "CDBA", "BDAC", "DBCA"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(name: str, value: dict) -> None:
    with (OUT / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()


def main() -> None:
    products = ["V57_COMPATIBILITY.json", "V57_FORMAL_DESIGN.json",
                "V58_POLICY_ORDER.json", "V59_MECHANISM_COST.json", "FREEZE_MANIFEST.json"]
    if any((OUT / name).exists() for name in products):
        raise RuntimeError("Freeze products already exist; no overwrite or rerandomization")
    if sha(DATA) != EXPECTED_DATA_SHA:
        raise RuntimeError("Pinned LongMemEval dataset hash drift")
    rows = {r["question_id"]: r for r in json.loads(DATA.read_text(encoding="utf-8"))}
    expected = {"b5ef892d": 52, "1a8a66a6": 51, "gpt4_31ff4165": 42,
                "0a995998": 44, "87f22b4a": 47}
    expected.update({c["question_id"]: c["sessions"] for c in V58_CASES})
    expected.update({"gpt4_74aed68e": 45, "a06e4cfe": 53, "gpt4_d12ceb0e": 45})
    for question_id, count in expected.items():
        if len(rows[question_id]["haystack_sessions"]) != count:
            raise RuntimeError(f"Dataset case binding drift: {question_id}")

    v55_file = ROOT / "history/v55_formal/results/v55-formal-20260925-01_AGGREGATE.json"
    v55 = json.loads(v55_file.read_text(encoding="utf-8"))
    eligible = [r for r in sorted(v55["cases"], key=lambda r: r["rank"])
                if r.get("stage_a_valid") is True and r.get("e2_evaluable") is True
                and r.get("e2_positive") is True]
    first_three = eligible[:3]
    if [(r["rank"], r["question_id"]) for r in first_three] != [
        (13, "gpt4_74aed68e"), (15, "a06e4cfe"), (17, "gpt4_d12ceb0e")
    ]:
        raise RuntimeError("V59 mechanical V55 selection drift")

    cells = Counter((order[i-1], order[i], i+1) for order in ORDERS for i in (1, 2, 3))
    positions = Counter((symbol, i+1) for order in ORDERS for i, symbol in enumerate(order))
    if len(ORDERS) != 12 or len(set(ORDERS)) != 12:
        raise RuntimeError("Duplicate V58 orders")
    if len(cells) != 36 or set(cells.values()) != {1} or set(positions.values()) != {3}:
        raise RuntimeError("V58 exact cover failed")

    random_seed = secrets.token_hex(16)
    rng = random.Random(int(random_seed, 16))
    compat = [{"slot": i+1, "rank": rank, "question_id": qid, "repeat": repeat}
              for i, (rank, qid, repeat) in enumerate([
                  (1, "b5ef892d", 1), (3, "1a8a66a6", 1),
                  (4, "gpt4_31ff4165", 1), (1, "b5ef892d", 2),
                  (3, "1a8a66a6", 2), (4, "gpt4_31ff4165", 2)])]
    write_once("V57_COMPATIBILITY.json", {
        "schema": "c33-v57-ds-compatibility-freeze-v1",
        "status": "DESIGN_FROZEN_EXECUTION_BLOCKED",
        "dataset_sha256": EXPECTED_DATA_SHA,
        "scorer_sha256": sha(ROOT / "v57_design/code/count_unit_v1.py"),
        "scorer_vectors_sha256": sha(ROOT / "v57_design/COUNT_UNIT_V1_TEST_VECTORS.json"),
        "cases_sha256": sha(ROOT / "v57_design/V57_DEV_CASES.json"),
        "trajectories": compat,
        "pass_rule": {"complete": 6, "nonempty_memory": 6, "nonempty_retrieval": 6,
                      "parseable_answer": 6, "fatal_failures": 0, "correct_min": 4,
                      "correct_min_per_case": 1},
        "failure_label": "LANGMEM_DS_INCOMPATIBLE",
        "purpose": "Engineering qualification only; no causal or backend-safety claim",
        "model_request": {"model": "deepseek-flash", "thinking": "disabled",
                          "temperature": 0, "stream": False, "concurrency": 1},
        "retry_rule": "No automatic retry after client dispatch for any HTTP or transport failure",
        "receipt_rule": "Persist request body and hash before dispatch; persist raw response before parsing",
        "returned_model_id": "BIND_FROM_SIX_COMPATIBILITY_RUNS_BEFORE_FORMAL",
    })

    formal_targets = []
    for rank, qid, count in [(26, "0a995998", 44), (27, "87f22b4a", 47)]:
        assignments = []
        for start, arms in [(1, ["N", "N", "S", "S"]),
                            (5, ["N", "N", "S", "S"]), (9, ["N", "S"])]:
            rng.shuffle(arms)
            assignments.extend({"slot": start+i, "arm": arm} for i, arm in enumerate(arms))
        formal_targets.append({"rank": rank, "question_id": qid, "sessions": count,
                               "assignments": assignments})
    write_once("V57_FORMAL_DESIGN.json", {
        "schema": "c33-v57-ds-formal-design-freeze-v1",
        "status": "DESIGN_FROZEN_EXECUTION_BLOCKED",
        "random_seed_hex": random_seed,
        "predecessor": {"rank": 1, "question_id": "b5ef892d", "sessions": 52},
        "targets": formal_targets,
        "unit": "Fresh process and separate LangMem A/B; full predecessor on A; reveal arm only after predecessor-complete receipt; native reset A or empty reset B; full target on assigned backend",
        "unit_isolation": "Destroy process, managers, stores, and local embed working state between units",
        "endpoint": "Ordered Top-5 1925-dimensional BGE retrieval footprint; empty list is valid",
        "footprint_code_sha256": sha(ROOT / "v57_design/code/retrieval_footprint.py"),
        "test": "Euclidean energy statistic in float64, right-tail Fisher test over 72 allowed assignments per target, tie tolerance 1e-12",
        "decision": "p26<0.05 AND p27<0.05 for REPLICATED_CROSS_BACKEND_INFLUENCE; one significant = SINGLE_TARGET_SIGNAL; neither = INFLUENCE_NOT_DETECTED",
        "failure": "Any incomplete unit makes its target and backend result UNVERIFIABLE_EXECUTION; no replacement or rerun",
    })

    v58_orders = []
    for index, order in enumerate(ORDERS, 1):
        arms = ["N", "V"]
        rng.shuffle(arms)
        v58_orders.append({"block": index, "order": order, "slot1": arms[0], "slot2": arms[1]})
    write_once("V58_POLICY_ORDER.json", {
        "schema": "c33-v58-policy-order-design-freeze-v1",
        "status": "DESIGN_FROZEN_EXECUTION_BLOCKED",
        "random_seed_hex": random_seed,
        "cases": V58_CASES,
        "blocks": v58_orders,
        "exact_cover": "Each directed adjacent pair occurs exactly once at each target position 2, 3, 4; each case occurs 3 times at each position",
        "primary": "Native minus verified mean within-target-and-position dispersion across the three predecessor-labeled orders",
        "inference": "One-sided exact Fisher policy-label test over 2^12=4096 within-order swaps",
        "claim_boundary": "Policy effect on fixed-panel order/history-conditioned retrieval dispersion; no score, ranking, or isolated immediate-predecessor claim",
        "runtime": "Fresh independent Mem0 sequence per slot; V55-defined verified cleanup; pinned Qwen3 8B Q4",
    })

    v59_blocks = []
    for case in first_three:
        for repeat in (1, 2):
            arms = ["N", "V", "F", "P"]
            rng.shuffle(arms)
            v59_blocks.append({"rank": case["rank"], "question_id": case["question_id"],
                               "sessions": case["session_count"], "repeat": repeat,
                               "arm_execution_order": arms})
    write_once("V59_MECHANISM_COST.json", {
        "schema": "c33-v59-mechanism-cost-design-freeze-v1",
        "status": "DESIGN_FROZEN_EXECUTION_BLOCKED",
        "random_seed_hex": random_seed,
        "selection_source_sha256": sha(v55_file),
        "selection": "Earliest three V55 stage-A-valid, E2-evaluable, E2-positive ranks",
        "blocks": v59_blocks,
        "seed": "Each block independently regenerates V55's three-successful-session plus frozen-fault contaminated seed; clone before policy application",
        "arms": {"N": "Native reset in same scope", "V": "V55 verified cleanup in same scope",
                 "F": "Rotate to new user_id/run_id while retaining contaminated backend state",
                 "P": "Pristine backend clone never exposed to contaminated seed"},
        "outcomes": "Per block distances N-P, V-P, F-P; medians, ranges, sign counts; full lifecycle latency/RSS/storage receipts",
        "microbenchmark": "100 policy-only operations per N/V/F; descriptive only",
        "claim_boundary": "Exploratory mechanism and cost; no equivalence, certificate, or general cheapest-policy claim",
    })

    bound = {name: sha(OUT / name) for name in products[:-1]}
    write_once("FREEZE_MANIFEST.json", {
        "schema": "c33-three-block-design-freeze-manifest-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DESIGN_FROZEN_EXECUTION_BLOCKED",
        "source_sha256": sha(SOURCE),
        "dataset_sha256": EXPECTED_DATA_SHA,
        "generator_sha256": sha(Path(__file__)),
        "random_seed_hex": random_seed,
        "files_sha256": bound,
        "remaining_execution_gates": ["DeepSeek-LangMem adapter and raw request instrumentation",
                                      "zero-retry crash tests", "unit teardown and real backend recovery drill",
                                      "runtime identity and returned model binding", "run-specific preflight"],
        "api_calls": 0,
    })
    print(json.dumps({"status": "DESIGN_FROZEN_EXECUTION_BLOCKED", "files": products,
                      "v58_exact_cover_cells": len(cells), "api_calls": 0}))


if __name__ == "__main__":
    main()
