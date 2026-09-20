#!/usr/bin/env python3
"""Offline counterfactual audit for the frozen AMB v2.0.0 Mem0 public trace.

The script is deliberately provider-free. It consumes a minimal frozen evidence
fixture or the original AMB results JSON, removes a provenance-identified stale
retrieval from ma-03-q1, and recomputes the Layer-1 query outcome and AMB token
estimate under the benchmark's published scoring logic.
"""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

QUERY_ID = "ma-03-q1"
EXPECTED = ["race condition", "queue"]
STALE_SUBSTRINGS = [
    "connection pool to 100",
    "connection timeout of 5 seconds",
]


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def check_keywords(results: list[dict[str, Any]], keywords: list[str]) -> bool:
    combined = " ".join(str(r.get("content", "")) for r in results).lower()
    return all(kw.lower() in combined for kw in keywords)


def is_provenance_stale(content: str) -> bool:
    low = content.lower()
    return all(s.lower() in low for s in STALE_SUBSTRINGS)


def find_query_record(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    for category in data.get("categories", []):
        for detail in category.get("details", []):
            if detail.get("queryId") == QUERY_ID:
                return category, detail
    raise KeyError(f"query {QUERY_ID!r} not found")


def audit(data: dict[str, Any]) -> dict[str, Any]:
    category, detail = find_query_record(data)
    dirty_results = deepcopy(detail.get("topResults", []))
    clean_results = [r for r in dirty_results if not is_provenance_stale(str(r.get("content", "")))]

    dirty_pass = check_keywords(dirty_results, EXPECTED)
    clean_pass = check_keywords(clean_results, EXPECTED)

    query = str(detail.get("query", ""))
    dirty_tokens = estimate_tokens(query) + sum(
        estimate_tokens(str(r.get("content", ""))) for r in dirty_results
    )
    clean_tokens = estimate_tokens(query) + sum(
        estimate_tokens(str(r.get("content", ""))) for r in clean_results
    )

    recorded_score = int(detail.get("score", 1 if dirty_pass else 0))
    clean_score = 1 if clean_pass else 0

    cat_passed_recorded = int(category.get("passed", 0))
    cat_total = int(category.get("total", len(category.get("details", []))))
    cat_passed_clean = cat_passed_recorded - recorded_score + clean_score
    cat_score_clean = (cat_passed_clean / cat_total * 100.0) if cat_total else 0.0

    total_tokens_recorded = data.get("meta", {}).get("totalTokens")
    total_tokens_clean = None
    if isinstance(total_tokens_recorded, (int, float)):
        total_tokens_clean = total_tokens_recorded - dirty_tokens + clean_tokens

    return {
        "frozen_benchmark": "AlekseiMarchenko/agent-memory-benchmark@55d4f02d61388525105ffe34fe3f9d2c846d25bf",
        "benchmark_version": data.get("version"),
        "public_result_timestamp": data.get("timestamp"),
        "query_id": QUERY_ID,
        "query": query,
        "expected_keywords": EXPECTED,
        "dirty": {
            "retrieval_count": len(dirty_results),
            "retrieved_content": [r.get("content") for r in dirty_results],
            "pass": dirty_pass,
            "score": recorded_score,
            "estimated_tokens": dirty_tokens,
        },
        "verified_clean_counterfactual": {
            "operation": "remove only the provenance-identified stale l2-04/fix-agent retrieval",
            "retrieval_count": len(clean_results),
            "retrieved_content": [r.get("content") for r in clean_results],
            "pass": clean_pass,
            "score": clean_score,
            "estimated_tokens": clean_tokens,
        },
        "delta": {
            "retrieval_count": len(clean_results) - len(dirty_results),
            "query_score": clean_score - recorded_score,
            "query_estimated_tokens": clean_tokens - dirty_tokens,
            "multi_agent_passed": cat_passed_clean - cat_passed_recorded,
            "multi_agent_score_percentage_points": cat_score_clean - float(category.get("score", 0.0)),
            "total_estimated_tokens": (
                total_tokens_clean - total_tokens_recorded
                if total_tokens_clean is not None and total_tokens_recorded is not None
                else None
            ),
        },
        "category_counterfactual": {
            "recorded_passed": cat_passed_recorded,
            "recorded_total": cat_total,
            "recorded_score": category.get("score"),
            "clean_passed": cat_passed_clean,
            "clean_total": cat_total,
            "clean_score": cat_score_clean,
        },
        "benchmark_counterfactual": {
            "recorded_overall_score": data.get("overallScore"),
            "clean_overall_score": data.get("overallScore") if clean_score == recorded_score else None,
            "recorded_total_estimated_tokens": total_tokens_recorded,
            "clean_total_estimated_tokens": total_tokens_clean,
        },
        "answer_stage": {
            "status": "NOT_APPLICABLE_LAYER1",
            "reason": "Layer-1 scoring operates directly on retrieved contents and contains no separate answer-generation stage.",
        },
        "interpretation": "retrieval contamination is causally present in the public trace; this exact trace is score-neutral under the frozen Layer-1 scoring rule",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit(data)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
