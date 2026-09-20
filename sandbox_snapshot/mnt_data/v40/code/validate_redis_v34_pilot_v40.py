#!/usr/bin/env python3
"""Aggregate the frozen 12-case V34 Redis pilot without overclaiming."""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any, Callable

BOOTSTRAP_RESAMPLES = 5000
BOOTSTRAP_SEED = 20260919


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def bootstrap_ci(items: list[Any], stat: Callable[[list[Any]], float], rng: random.Random) -> dict[str, Any] | None:
    if not items:
        return None
    vals = []
    n = len(items)
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [items[rng.randrange(n)] for _ in range(n)]
        vals.append(float(stat(sample)))
    return {
        "estimate": float(stat(items)),
        "ci95_percentile": [quantile(vals, 0.025), quantile(vals, 0.975)],
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
    }


def exact_mcnemar_p(b: int, c: int) -> float | None:
    n = b + c
    if n == 0:
        return None
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def level_for(data: dict[str, Any]) -> str:
    if not (data.get("trigger_reached") and data.get("vector_receipts_consistent")):
        return "E0"
    if not data.get("first_extraction_prompt_diff"):
        return "E1_RESIDUAL_OBSERVED_CONSUMPTION_NOT_ATTESTED"
    if data.get("memory_equal") is False or data.get("retrieval_equal") is False:
        if data.get("answer_equal") is False:
            if data.get("judge_score_equal") is False:
                return "E4"
            return "E3"
        return "E2"
    if data.get("answer_equal") is False:
        if data.get("judge_score_equal") is False:
            return "E4"
        return "E3"
    # A judge disagreement on an identical answer is evaluator instability, not causal E4 evidence.
    return "E1"


def at_least_e2(level: str) -> bool:
    return level in {"E2", "E3", "E4"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", type=Path, required=True)
    p.add_argument("--cohort-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    cohort = json.loads(args.cohort_file.read_text(encoding="utf-8"))
    expected = [str(x["question_id"]) for x in cohort.get("cases", [])]
    if len(expected) != 12:
        raise RuntimeError("Frozen cohort must contain 12 cases")

    by_qid: dict[str, dict[str, Any]] = {}
    duplicates = []
    invalid_files = []
    for path in sorted(args.results_dir.glob("case_*.json")):
        if path.name.endswith("_error.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            invalid_files.append(str(path))
            continue
        if data.get("schema") != "c33-v34-redis-exact-paired-v40":
            invalid_files.append(str(path))
            continue
        qid = str(data.get("question_id"))
        if qid in by_qid:
            duplicates.append(qid)
        by_qid[qid] = data

    missing = [qid for qid in expected if qid not in by_qid]
    extra = sorted(set(by_qid) - set(expected))
    cases = []
    for qid in expected:
        if qid not in by_qid:
            continue
        d = by_qid[qid]
        level = level_for(d)
        cases.append({
            "question_id": qid,
            "question_type": d.get("question_type"),
            "level": level,
            "trigger_reached": bool(d.get("trigger_reached")),
            "first_extraction_prompt_diff": bool(d.get("first_extraction_prompt_diff")),
            "memory_equal": d.get("memory_equal"),
            "memory_jaccard": d.get("memory_jaccard"),
            "retrieval_equal": d.get("retrieval_equal"),
            "retrieval_jaccard": d.get("retrieval_jaccard"),
            "answer_equal": d.get("answer_equal"),
            "judge_score_equal": d.get("judge_score_equal"),
            "native_score": (d.get("native") or {}).get("judge", {}).get("score") if isinstance((d.get("native") or {}).get("judge"), dict) else None,
            "clean_score": (d.get("verified_clean") or {}).get("judge", {}).get("score") if isinstance((d.get("verified_clean") or {}).get("judge"), dict) else None,
        })

    e2_flags = [1.0 if at_least_e2(x["level"]) else 0.0 for x in cases]
    memory_j = [float(x["memory_jaccard"]) for x in cases if x["memory_jaccard"] is not None]
    retrieval_j = [float(x["retrieval_jaccard"]) for x in cases if x["retrieval_jaccard"] is not None]

    level_counts: dict[str, int] = {}
    for c in cases:
        level_counts[c["level"]] = level_counts.get(c["level"], 0) + 1

    judge_pairs = [(x["native_score"], x["clean_score"]) for x in cases if x["native_score"] is not None and x["clean_score"] is not None]
    b = sum(1 for n, c in judge_pairs if bool(n) and not bool(c))
    c = sum(1 for n, c in judge_pairs if not bool(n) and bool(c))

    complete = not missing and not extra and not duplicates and not invalid_files and len(cases) == 12
    e2plus_count = sum(1 for x in cases if at_least_e2(x["level"]))
    report = {
        "schema": "c33-v34-redis-pilot-analysis-v40",
        "protocol_freeze": "V34",
        "complete": complete,
        "expected_cases": 12,
        "valid_cases": len(cases),
        "missing_question_ids": missing,
        "extra_question_ids": extra,
        "duplicate_question_ids": duplicates,
        "invalid_files": invalid_files,
        "level_counts": level_counts,
        "e2plus_count": e2plus_count,
        "primary_endpoint": "E2_OR_HIGHER",
        "primary_endpoint_observed_in_at_least_one_case": e2plus_count > 0,
        "e2plus_fraction_bootstrap": bootstrap_ci(e2_flags, lambda xs: sum(xs) / len(xs), random.Random(BOOTSTRAP_SEED)) if e2_flags else None,
        "memory_jaccard_median_bootstrap": bootstrap_ci(memory_j, statistics.median, random.Random(BOOTSTRAP_SEED)) if memory_j else None,
        "retrieval_jaccard_median_bootstrap": bootstrap_ci(retrieval_j, statistics.median, random.Random(BOOTSTRAP_SEED)) if retrieval_j else None,
        "judge_pairs": len(judge_pairs),
        "same_answer_judge_disagreement_count": sum(1 for x in cases if x["answer_equal"] is True and x["judge_score_equal"] is False),
        "mcnemar_native_correct_clean_wrong_b": b,
        "mcnemar_native_wrong_clean_correct_c": c,
        "mcnemar_exact_two_sided_p": exact_mcnemar_p(b, c),
        "cases": cases,
        "interpretation_guardrails": [
            "An E2+ observation establishes downstream divergence for executed paired cases; it does not estimate field prevalence.",
            "A 12-case Redis null does not by itself kill C33; the frozen MemArena paired pilot remains an independent gate.",
            "Score direction is reported descriptively; no assumption is made that residual state must always inflate or always depress scores.",
            "Generic reset isolation and verified-reset principles remain prior art rather than novelty claims."
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"complete": complete, "valid_cases": len(cases), "e2plus_count": e2plus_count}, indent=2))
    if not complete:
        raise SystemExit(4)


if __name__ == "__main__":
    main()
