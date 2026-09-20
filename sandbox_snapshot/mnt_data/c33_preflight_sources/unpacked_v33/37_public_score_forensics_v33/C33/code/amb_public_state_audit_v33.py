#!/usr/bin/env python3
"""Deterministic audit helpers for AMB v2 public result artifacts.

This script intentionally performs trace-level analysis only. It never treats
removing observed stale/residual rows as a prediction of what a fresh provider
rerun would retrieve.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CATEGORY_WEIGHTS = {
    "factual-recall": 0.15,
    "semantic-search": 0.20,
    "temporal-reasoning": 0.15,
    "conflict-resolution": 0.10,
    "selective-forgetting": 0.10,
    "cross-session": 0.15,
    "multi-agent": 0.05,
    "cost-efficiency": 0.10,
}

MEM0_TRACE_FLIPS = {"sf-02-q1", "sf-05-q1", "sf-06-q1", "ce-05-q1"}
ZEP_FALSE_PASS = "tr-06-q1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_overall(categories: list[dict[str, Any]]) -> float:
    weighted = 0.0
    total_weight = 0.0
    for category in categories:
        if category.get("skipped"):
            continue
        weight = CATEGORY_WEIGHTS.get(category["category"], 0.1)
        weighted += float(category["score"]) * weight
        total_weight += weight
    return weighted / total_weight if total_weight else 0.0


def counterfactual_score(result: dict[str, Any], flips: set[str], *, to_score: int) -> dict[str, Any]:
    categories = json.loads(json.dumps(result["categories"]))
    changed = []
    for category in categories:
        details = category.get("details", [])
        for row in details:
            if row.get("queryId") in flips:
                old = int(row.get("score", 0))
                if old == to_score:
                    continue
                row["score"] = to_score
                row["passed"] = bool(to_score)
                changed.append({"queryId": row["queryId"], "old": old, "new": to_score})
        total = len(details)
        if total:
            passed = sum(1 for row in details if row.get("passed"))
            category["passed"] = passed
            category["total"] = total
            category["score"] = passed / total * 100.0
    exact = exact_overall(categories)
    return {"changed": changed, "exact": exact, "rounded": round(exact), "categories": categories}


def same_id_reuse(result: dict[str, Any]) -> dict[str, Any]:
    seen: dict[str, dict[str, Any]] = {}
    rows = []
    query_index = 0
    all_prior_count = 0
    passing_all_prior = 0
    unique_reused: set[str] = set()
    for category in result.get("categories", []):
        for row in category.get("details", []):
            query_index += 1
            top = row.get("topResults", []) or []
            reused = []
            flags = []
            for item in top:
                rid = item.get("id")
                is_prior = bool(rid in seen and seen[rid]["testId"] != row.get("testId"))
                flags.append(is_prior)
                if is_prior:
                    unique_reused.add(rid)
                    reused.append({"id": rid, "first_seen": seen[rid], "content": item.get("content")})
                if rid and rid not in seen:
                    seen[rid] = {
                        "queryIndex": query_index,
                        "category": category.get("category"),
                        "testId": row.get("testId"),
                        "queryId": row.get("queryId"),
                    }
            if reused:
                rows.append({
                    "queryIndex": query_index,
                    "category": category.get("category"),
                    "testId": row.get("testId"),
                    "queryId": row.get("queryId"),
                    "passed": row.get("passed"),
                    "reused": reused,
                })
            if top and flags and all(flags):
                all_prior_count += 1
                if row.get("passed"):
                    passing_all_prior += 1
    return {
        "layer1_query_records": query_index,
        "queries_with_prior_test_id": len(rows),
        "queries_all_top_results_prior_test_ids": all_prior_count,
        "passing_queries_all_top_results_prior_test_ids": passing_all_prior,
        "unique_reused_ids": len(unique_reused),
        "rows": rows,
    }


def trace_substring_match(row: dict[str, Any], keywords: list[str]) -> dict[str, Any]:
    combined = " ".join(str(x.get("content", "")) for x in row.get("topResults", [])).lower()
    matches = {kw: kw.lower() in combined for kw in keywords}
    return {"combined": combined, "matches": matches, "passes": all(matches.values())}


def find_query(result: dict[str, Any], query_id: str) -> dict[str, Any]:
    for category in result.get("categories", []):
        for row in category.get("details", []):
            if row.get("queryId") == query_id:
                return row
    raise KeyError(query_id)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mem0-results", type=Path)
    parser.add_argument("--zep-results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report: dict[str, Any] = {"schema_version": "v33.1"}
    if args.mem0_results:
        mem0 = load(args.mem0_results)
        cf = counterfactual_score(mem0, MEM0_TRACE_FLIPS, to_score=1)
        report["mem0"] = {
            "reported": mem0.get("overallScore"),
            "exact": exact_overall(mem0["categories"]),
            "trace_restricted_counterfactual": {
                "changed": cf["changed"],
                "exact": cf["exact"],
                "rounded": cf["rounded"],
            },
        }
    if args.zep_results:
        zep = load(args.zep_results)
        reuse = same_id_reuse(zep)
        tr06 = find_query(zep, ZEP_FALSE_PASS)
        cf = counterfactual_score(zep, {ZEP_FALSE_PASS}, to_score=0)
        report["zep"] = {
            "reported": zep.get("overallScore"),
            "exact": exact_overall(zep["categories"]),
            "reuse": {k: v for k, v in reuse.items() if k != "rows"},
            "tr06": {
                "observed": {"passed": tr06.get("passed"), "score": tr06.get("score")},
                "substring": trace_substring_match(tr06, ["4"]),
                "trace_restricted_counterfactual": {
                    "changed": cf["changed"],
                    "exact": cf["exact"],
                    "rounded": cf["rounded"],
                },
            },
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
