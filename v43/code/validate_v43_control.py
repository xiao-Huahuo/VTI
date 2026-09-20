#!/usr/bin/env python3
"""Validate and summarize the V43 clean-clean stochastic negative control."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--cohort-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cohort = json.loads(args.cohort_file.read_text(encoding="utf-8"))
    expected = [str(item["question_id"]) for item in cohort["cases"][:3]]
    cases = []
    for rank, qid in enumerate(expected, start=1):
        path = args.results_dir / f"case_{rank:02d}_{qid}.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != "c33-v43-redis-deepseek-clean-clean-control":
            raise RuntimeError(f"Unexpected schema in {path}")
        cases.append(
            {
                "rank": rank,
                "question_id": qid,
                "decision": data.get("decision"),
                "control_preconditions_met": data.get("control_preconditions_met"),
                "first_extraction_prompt_equal": data.get("first_extraction_prompt_equal"),
                "memory_equal": data.get("memory_equal"),
                "memory_jaccard": data.get("memory_jaccard"),
                "retrieval_equal": data.get("retrieval_equal"),
                "retrieval_jaccard": data.get("retrieval_jaccard"),
                "answer_equal": data.get("answer_equal"),
            }
        )

    complete = len(cases) == 3 and all(
        item["control_preconditions_met"] and item["first_extraction_prompt_equal"]
        for item in cases
    )
    memory_j = [float(item["memory_jaccard"]) for item in cases]
    retrieval_j = [float(item["retrieval_jaccard"]) for item in cases]
    report = {
        "schema": "c33-v43-stochastic-negative-control-analysis",
        "complete": complete,
        "valid_cases": len(cases),
        "baseline_memory_divergence_count": sum(not item["memory_equal"] for item in cases),
        "baseline_retrieval_divergence_count": sum(not item["retrieval_equal"] for item in cases),
        "baseline_answer_divergence_count": sum(not item["answer_equal"] for item in cases),
        "memory_jaccard_median": statistics.median(memory_j) if memory_j else None,
        "retrieval_jaccard_median": statistics.median(retrieval_j) if retrieval_j else None,
        "cases": cases,
        "interpretation": (
            "Clean-clean divergence estimates the model/provider stochastic baseline. "
            "V42 native-clean differences require comparison against this baseline."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"complete": complete, "valid_cases": len(cases)}, indent=2))
    if not complete:
        raise SystemExit(4)


if __name__ == "__main__":
    main()
