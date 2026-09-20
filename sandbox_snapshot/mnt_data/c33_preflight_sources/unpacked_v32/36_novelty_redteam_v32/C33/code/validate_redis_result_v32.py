#!/usr/bin/env python3
"""Conservative claim-gate validator for a V32 exact Redis paired result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("result", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    data=json.loads(args.result.read_text())

    trigger=bool(data.get("trigger_reached"))
    receipts=bool(data.get("vector_receipts_consistent"))
    prompt=bool(data.get("first_extraction_prompt_diff"))
    mem_diff=data.get("memory_equal") is False
    ret_diff=data.get("retrieval_equal") is False
    ans_diff=data.get("answer_equal") is False
    judge_diff=data.get("judge_score_equal") is False

    if not (trigger and receipts):
        level="MECHANISM_NOT_CLOSED"
    elif not prompt:
        level="RESET_MISMATCH_ONLY"
    elif mem_diff or ret_diff or ans_diff or judge_diff:
        level="DOWNSTREAM_EFFECT_OBSERVED"
    else:
        level="PROMPT_EFFECT_DOWNSTREAM_NULL_FOR_THIS_CASE"

    allowed_claims=[]
    if trigger and receipts:
        allowed_claims.append("native scoped reset left behaviorally active message state while vector state attested clean")
    if trigger and receipts and prompt:
        allowed_claims.append("surviving sidecar state changed the next extraction prompt in the frozen runtime")
    if level == "DOWNSTREAM_EFFECT_OBSERVED":
        allowed_claims.append("the paired arms diverged at one or more downstream observable levels for this executed case")

    forbidden_claims=[
        "published Redis benchmark scores are broadly invalid",
        "field prevalence of reset contamination",
        "generic verified-reset or cross-run-isolation principles are novel",
    ]
    out={
        "schema":"redis-result-claim-gate-v32",
        "level":level,
        "allowed_claims":allowed_claims,
        "forbidden_claims":forbidden_claims,
        "scale_unlock": level == "DOWNSTREAM_EFFECT_OBSERVED",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
