from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORT = json.loads((ROOT / "redis_v42_cohort.json").read_text(encoding="utf-8"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_frozen_cohort_is_unchanged():
    cases = COHORT["cases"]
    assert len(cases) == 12
    digests = []
    for rank, case in enumerate(cases, start=1):
        expected = hashlib.sha256(
            ("C33-V34-REDIS|" + case["question_id"]).encode()
        ).hexdigest()
        assert case["rank"] == rank
        assert case["selection_sha256"] == expected
        assert case["session_count"] > 3
        digests.append(expected)
    assert digests == sorted(digests)


def test_v42_provider_config(monkeypatch, tmp_path: Path):
    mod = load_module("probe_v42", ROOT / "code" / "redis_v42_deepseek_paired_probe.py")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-key")
    config = mod.make_config(tmp_path)
    assert config["llm"]["config"]["model"] == "deepseek-flash"
    assert config["llm"]["config"]["openai_base_url"] == "https://api.deepseek.com"
    assert config["llm"]["config"]["reasoning_effort"] == "low"
    assert config["llm"]["config"]["is_reasoning_model"] is True
    assert config["embedder"]["provider"] == "fastembed"
    assert config["embedder"]["config"]["model"] == "BAAI/bge-small-en-v1.5"
    assert config["vector_store"]["config"]["embedding_model_dims"] == 384


def test_evidence_level_mapping():
    mod = load_module("validator_v42", ROOT / "code" / "validate_redis_v42_pilot.py")
    base = {
        "trigger_reached": True,
        "vector_receipts_consistent": True,
        "first_extraction_prompt_diff": True,
        "memory_equal": True,
        "retrieval_equal": True,
        "answer_equal": True,
        "judge_score_equal": None,
    }
    assert mod.level_for(base) == "E1"
    assert mod.level_for(dict(base, retrieval_equal=False)) == "E2"
    assert mod.level_for(dict(base, answer_equal=False)) == "E3"


def test_synthetic_12_case_aggregation(tmp_path: Path):
    results = tmp_path / "results"
    results.mkdir()
    for case in COHORT["cases"]:
        qid = case["question_id"]
        rank = case["rank"]
        effect = rank in {1, 5, 9}
        data = {
            "schema": "c33-v42-redis-deepseek-exact-paired",
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
            "judge_score_equal": None,
            "native": {"judge": None},
            "verified_clean": {"judge": None},
        }
        (results / f"case_{rank:02d}_{qid}.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
    output = tmp_path / "analysis.json"
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "code" / "validate_redis_v42_pilot.py"),
            "--results-dir",
            str(results),
            "--cohort-file",
            str(ROOT / "redis_v42_cohort.json"),
            "--output",
            str(output),
        ]
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["complete"] is True
    assert report["valid_cases"] == 12
    assert report["e2plus_count"] == 3
    assert report["judge_pairs"] == 0


def test_preflight_derives_frozen_hash_order():
    mod = load_module("preflight_v42", ROOT / "code" / "preflight_redis_v42.py")
    rows = [
        {
            "question_id": f"q{i:02d}",
            "question_type": "synthetic",
            "haystack_sessions": [[], [], [], []],
        }
        for i in range(30)
    ]
    got = mod.derive_cohort(rows)
    expected = sorted(
        [f"q{i:02d}" for i in range(30)],
        key=lambda q: hashlib.sha256(("C33-V34-REDIS|" + q).encode()).hexdigest(),
    )[:12]
    assert [item["question_id"] for item in got] == expected
