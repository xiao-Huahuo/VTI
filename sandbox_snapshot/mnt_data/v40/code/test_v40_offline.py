from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORT = json.loads((ROOT / "redis_v34_cohort.json").read_text(encoding="utf-8"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_frozen_cohort_hashes_and_order():
    cases = COHORT["cases"]
    assert len(cases) == 12
    digests = []
    for rank, case in enumerate(cases, start=1):
        expected = hashlib.sha256(("C33-V34-REDIS|" + case["question_id"]).encode()).hexdigest()
        assert case["rank"] == rank
        assert case["selection_sha256"] == expected
        assert case["session_count"] > 3
        digests.append(expected)
    assert digests == sorted(digests)


def test_evidence_level_mapping():
    mod = load_module("validator_v40", ROOT / "code" / "validate_redis_v34_pilot_v40.py")
    base = {"trigger_reached": True, "vector_receipts_consistent": True, "first_extraction_prompt_diff": True,
            "memory_equal": True, "retrieval_equal": True, "answer_equal": True, "judge_score_equal": True}
    assert mod.level_for(base) == "E1"
    e2 = dict(base, retrieval_equal=False)
    assert mod.level_for(e2) == "E2"
    e3 = dict(base, answer_equal=False)
    assert mod.level_for(e3) == "E3"
    e4 = dict(base, answer_equal=False, judge_score_equal=False)
    assert mod.level_for(e4) == "E4"
    assert mod.exact_mcnemar_p(0, 0) is None
    assert mod.exact_mcnemar_p(0, 3) == 0.25


def test_synthetic_12_case_aggregation(tmp_path: Path):
    results = tmp_path / "results"; results.mkdir()
    for case in COHORT["cases"]:
        qid = case["question_id"]
        rank = case["rank"]
        effect = rank in {1, 5, 9}
        d = {
            "schema": "c33-v34-redis-exact-paired-v40",
            "question_id": qid,
            "question_type": case["question_type"],
            "trigger_reached": True,
            "vector_receipts_consistent": True,
            "first_extraction_prompt_diff": True,
            "memory_equal": not effect,
            "memory_jaccard": 0.8 if effect else 1.0,
            "retrieval_equal": not effect,
            "retrieval_jaccard": 0.7 if effect else 1.0,
            "answer_equal": True,
            "judge_score_equal": True,
            "native": {"judge": {"score": 1}},
            "verified_clean": {"judge": {"score": 1}},
        }
        (results / f"case_{rank:02d}_{qid}.json").write_text(json.dumps(d), encoding="utf-8")
    out = tmp_path / "analysis.json"
    subprocess.check_call([
        sys.executable, str(ROOT / "code" / "validate_redis_v34_pilot_v40.py"),
        "--results-dir", str(results), "--cohort-file", str(ROOT / "redis_v34_cohort.json"), "--output", str(out)
    ])
    report = json.loads(out.read_text())
    assert report["complete"] is True
    assert report["valid_cases"] == 12
    assert report["e2plus_count"] == 3
    assert report["primary_endpoint_observed_in_at_least_one_case"] is True

def test_preflight_derives_first_12_by_frozen_hash():
    mod = load_module("preflight_v40", ROOT / "code" / "preflight_redis_v34_v40.py")
    rows = []
    for i in range(30):
        rows.append({
            "question_id": f"q{i:02d}",
            "question_type": "synthetic",
            "haystack_sessions": [[], [], [], []],
        })
    got = mod.derive_cohort(rows)
    expected_ids = sorted(
        [f"q{i:02d}" for i in range(30)],
        key=lambda q: hashlib.sha256(("C33-V34-REDIS|" + q).encode()).hexdigest(),
    )[:12]
    assert [x["question_id"] for x in got] == expected_ids
