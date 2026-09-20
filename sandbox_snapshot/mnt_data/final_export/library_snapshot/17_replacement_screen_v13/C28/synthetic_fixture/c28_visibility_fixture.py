#!/usr/bin/env python3
"""Deterministic feasibility fixture for the C28 metric pipeline.

Synthetic only. It validates V(t), T95, and ranking-sensitivity calculations.
It is not evidence that any real Agent Memory system exhibits the effect.
"""
import json
import numpy as np
from pathlib import Path

SEED = 28013
N = 500
DELAYS = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
PROVIDERS = {
    "fast_lower_ceiling": {"median_visibility_s": 0.35, "sigma": 0.7, "mature_recall": 0.78},
    "slow_higher_ceiling": {"median_visibility_s": 4.0, "sigma": 0.8, "mature_recall": 0.92},
}

rng = np.random.default_rng(SEED)
results = {"seed": SEED, "n": N, "delays_s": DELAYS, "providers": {}}

for name, cfg in PROVIDERS.items():
    visibility_time = rng.lognormal(
        mean=np.log(cfg["median_visibility_s"]), sigma=cfg["sigma"], size=N
    )
    mature_hit = rng.random(N) < cfg["mature_recall"]
    curve = []
    for delay in DELAYS:
        visible = visibility_time <= delay
        hit = visible & mature_hit
        curve.append({
            "delay_s": delay,
            "visibility_rate": float(visible.mean()),
            "retrieval_hit_rate": float(hit.mean()),
        })

    t95 = next((row["delay_s"] for row in curve if row["visibility_rate"] >= 0.95), None)
    results["providers"][name] = {
        "config": cfg,
        "curve": curve,
        "t95_grid_s": t95,
        "native_ready_visibility": 1.0,
        "native_ready_retrieval_hit_rate": float(mature_hit.mean()),
    }

a = results["providers"]["fast_lower_ceiling"]["curve"]
b = results["providers"]["slow_higher_ceiling"]["curve"]
rank = []
for ra, rb in zip(a, b):
    if ra["retrieval_hit_rate"] > rb["retrieval_hit_rate"]:
        winner = "fast_lower_ceiling"
    elif rb["retrieval_hit_rate"] > ra["retrieval_hit_rate"]:
        winner = "slow_higher_ceiling"
    else:
        winner = "tie"
    rank.append({"delay_s": ra["delay_s"], "winner": winner})
results["ranking_by_delay"] = rank

# Fixture invariants.
for p in results["providers"].values():
    vis = [r["visibility_rate"] for r in p["curve"]]
    assert all(x <= y for x, y in zip(vis, vis[1:])), "visibility must be monotonic"

assert any(x["winner"] == "fast_lower_ceiling" for x in rank[1:])
assert any(x["winner"] == "slow_higher_ceiling" for x in rank[1:])

Path(__file__).with_name("synthetic_results_v13.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print(json.dumps(results, indent=2))
