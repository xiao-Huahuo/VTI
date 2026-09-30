"""Frozen V58 policy dispersion and exact within-order randomization test."""
from __future__ import annotations

import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from retrieval_footprint import OUTPUT_DIMS


def _vector(value: Any) -> np.ndarray:
    array = np.asarray(value, dtype=np.float32)
    if array.shape != (OUTPUT_DIMS,) or not np.isfinite(array).all():
        raise ValueError("Invalid frozen 1925D float32 footprint")
    return array.astype(np.float64)


def euclidean(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right, ord=2))


def policy_statistic(records: list[dict[str, Any]], assignments: dict[int, dict[int, str]]) -> dict[str, Any]:
    if len(records) != 96:
        raise ValueError("V58 requires 96 trial retrieval observations")
    seen: set[tuple[int, int, int]] = set()
    cells: dict[tuple[str, str, int], list[tuple[str, np.ndarray]]] = defaultdict(list)
    for item in records:
        block, slot, position = int(item["block"]), int(item["slot"]), int(item["position"])
        key = (block, slot, position)
        if key in seen or block not in assignments or slot not in assignments[block]:
            raise ValueError("Duplicate or unknown V58 observation")
        seen.add(key)
        if position not in (1, 2, 3, 4) or item["target"] not in "ABCD":
            raise ValueError("Invalid V58 target or position")
        if position == 1:
            if item["predecessor"] is not None:
                raise ValueError("First trial must have no predecessor")
            continue
        if item["predecessor"] not in "ABCD" or item["predecessor"] == item["target"]:
            raise ValueError("Invalid predecessor")
        policy = assignments[block][slot]
        cells[(policy, item["target"], position)].append((item["predecessor"], _vector(item["footprint"])))
    if len(seen) != 96:
        raise ValueError("Missing V58 observations")
    per_cell: list[dict[str, Any]] = []
    for policy in ("N", "V"):
        for target in "ABCD":
            for position in (2, 3, 4):
                values = cells[(policy, target, position)]
                if len(values) != 3 or {x[0] for x in values} != set("ABCD") - {target}:
                    raise ValueError("Broken predecessor-position exact cover")
                vectors = [x[1] for x in values]
                distances = [euclidean(vectors[i], vectors[j]) for i, j in itertools.combinations(range(3), 2)]
                per_cell.append({"policy": policy, "target": target, "position": position,
                                 "predecessors": [x[0] for x in values], "distance_pairs": distances,
                                 "dispersion": sum(distances) / 3.0})
    native = sum(x["dispersion"] for x in per_cell if x["policy"] == "N") / 12.0
    verified = sum(x["dispersion"] for x in per_cell if x["policy"] == "V") / 12.0
    return {"native_dispersion": native, "verified_dispersion": verified,
            "delta": native - verified, "cells": per_cell}


def exact_randomization(records: list[dict[str, Any]], blocks: list[dict[str, Any]]) -> dict[str, Any]:
    if len(blocks) != 12 or [int(x["block"]) for x in blocks] != list(range(1, 13)):
        raise ValueError("Expected 12 frozen order blocks")
    observed_assignments = {int(b["block"]): {1: b["slot1"], 2: b["slot2"]} for b in blocks}
    if any(set(x.values()) != {"N", "V"} for x in observed_assignments.values()):
        raise ValueError("Each block must contain N and V")
    expected = {(int(b["block"]), slot, position):
                (b["order"][position - 1], b["order"][position - 2] if position > 1 else None)
                for b in blocks for slot in (1, 2) for position in (1, 2, 3, 4)}
    if len(records) != len(expected) or any(
        (int(r["block"]), int(r["slot"]), int(r["position"])) not in expected or
        (r["target"], r["predecessor"]) != expected[(int(r["block"]), int(r["slot"]), int(r["position"]))]
        for r in records
    ):
        raise ValueError("Observation differs from frozen order")
    observed = policy_statistic(records, observed_assignments)
    distribution: list[float] = []
    for bits in itertools.product((0, 1), repeat=12):
        assignments = {block: (dict(labels) if bits[block - 1] == 0 else {1: labels[2], 2: labels[1]})
                       for block, labels in observed_assignments.items()}
        distribution.append(policy_statistic(records, assignments)["delta"])
    tail = sum(value >= observed["delta"] - 1e-12 for value in distribution)
    per_order = []
    by_key = {(int(r["block"]), int(r["slot"]), int(r["position"])): r for r in records}
    for block in blocks:
        block_id = int(block["block"])
        paired = [euclidean(_vector(by_key[(block_id, 1, position)]["footprint"]),
                            _vector(by_key[(block_id, 2, position)]["footprint"]))
                  for position in (2, 3, 4)]
        per_order.append({"block": block_id, "order": block["order"],
                          "slot1_policy": block["slot1"], "slot2_policy": block["slot2"],
                          "paired_target_position_distances": paired,
                          "mean_paired_distance": sum(paired) / 3.0})
    return {"schema": "c33-v58-exact-policy-randomization-v1",
            "native_dispersion": observed["native_dispersion"],
            "verified_dispersion": observed["verified_dispersion"],
            "effect": observed["delta"], "exact_p_value": tail / 4096,
            "number_of_assignments": 4096, "right_tail_count": tail,
            "significant": observed["delta"] > 0 and tail / 4096 < 0.05,
            "per_cell_statistics": observed["cells"],
            "per_order_raw_statistics": per_order,
            "all_assignment_effects": distribution}


def load_records(paths: list[Path]) -> list[dict[str, Any]]:
    records = []
    for path in paths:
        records.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line)
    return records
