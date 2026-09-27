#!/usr/bin/env python3
"""Synthetic dry-run audit of draft target tests and 2-of-3 decision."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from partial_conjunction import ASSIGNMENTS, energy_tables, backend_test, partial_conjunction, target_test

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'v57_design/results/PARTIAL_CONJUNCTION_DRY_RUN.json'
ALPHA = 0.025
SIMULATIONS = 10000


def main():
    checks = {}
    def check(name, result):
        checks[name] = bool(result)

    check('exact_assignments_252', len(ASSIGNMENTS) == 252)
    zero = np.zeros((10, 4), dtype=float)
    check('all_tied_p_one', target_test(zero, [5, 6, 7, 8, 9])['p_value'] == 1)
    check('formal_1925_dimension_supported', target_test(np.zeros((10, 1925)), [5, 6, 7, 8, 9], formal=True)['p_value'] == 1)
    rng = np.random.default_rng(20260927)
    fixed_table = energy_tables(rng.normal(size=(1, 10, 4)))[0]
    fixed_assignment_p = np.array([np.count_nonzero(fixed_table >= value - 1e-12) / 252 for value in fixed_table])
    check('exhaustive_fixed_outcomes_superuniform', all(
        np.mean(fixed_assignment_p <= level) <= level + 1e-12 for level in (0.01, ALPHA, 0.05, 0.1)))

    shifted = np.vstack((np.zeros((5, 4)), np.ones((5, 4))))
    labels = [5, 6, 7, 8, 9]
    two_shift = backend_test([{'vectors': shifted.tolist(), 'treated_slots': labels},
                              {'vectors': shifted.tolist(), 'treated_slots': labels},
                              {'vectors': zero.tolist(), 'treated_slots': labels}])
    one_shift = backend_test([{'vectors': shifted.tolist(), 'treated_slots': labels},
                              {'vectors': zero.tolist(), 'treated_slots': labels},
                              {'vectors': zero.tolist(), 'treated_slots': labels}])
    check('two_target_shift_detected', two_shift['decision'] == 'REPLICATED_RETRIEVAL_INFLUENCE')
    check('one_target_shift_not_detected', one_shift['decision'] == 'INFLUENCE_NOT_DETECTED')
    check('bonferroni_two_backend_boundary', partial_conjunction([0.01, 0.0125, 1])['decision'] == 'INFLUENCE_NOT_DETECTED'
          and partial_conjunction([0.01, 0.011, 1])['decision'] == 'REPLICATED_RETRIEVAL_INFLUENCE')

    all_null_positive = 0
    one_alt_positive = 0
    for start in range(0, SIMULATIONS, 250):
        batch = min(250, SIMULATIONS - start)
        null_p = np.empty((batch, 3), dtype=float)
        for target in range(3):
            vectors = rng.normal(size=(batch, 10, 4))
            table = energy_tables(vectors)
            assignment_indices = rng.integers(0, 252, size=batch)
            observed = table[np.arange(batch), assignment_indices]
            tolerances = 1e-12 * np.maximum(1.0, np.abs(observed))
            null_p[:, target] = np.count_nonzero(table >= observed[:, None] - tolerances[:, None], axis=1) / 252
        sorted_p = np.sort(null_p, axis=1)
        all_null_positive += int(np.count_nonzero(2 * sorted_p[:, 1] < ALPHA))
        # One target is truly affected: p=0 is the adversarial limiting case.
        one_alt_positive += int(np.count_nonzero(2 * np.minimum(null_p[:, 1], null_p[:, 2]) < ALPHA))
    all_null_rate = all_null_positive / SIMULATIONS
    one_alt_rate = one_alt_positive / SIMULATIONS
    check('synthetic_all_null_rate_bounded', all_null_rate <= 0.01)
    check('synthetic_one_alt_rate_near_nominal', one_alt_rate <= 0.035)

    report = {
        'schema': 'c33-v57-draft-partial-conjunction-statistical-audit-v1',
        'status': 'PASS' if all(checks.values()) else 'FAIL',
        'at_utc': datetime.now(timezone.utc).isoformat(),
        'checks': checks, 'checks_passed': sum(checks.values()), 'checks_total': len(checks),
        'synthetic_null_datasets': SIMULATIONS,
        'all_null_positive_count': all_null_positive, 'all_null_positive_rate': all_null_rate,
        'one_false_target_limit_positive_count': one_alt_positive,
        'one_false_target_limit_positive_rate': one_alt_rate,
        'alpha_per_backend': ALPHA,
        'two_shift_case': two_shift, 'one_shift_case': one_shift,
        'model_calls': 0,
        'boundary': 'Tests statistical implementation under synthetic nulls; does not establish independent runtime units or freeze a V57 causal protocol.',
    }
    if OUT.exists():
        raise RuntimeError('Refusing to overwrite synthetic statistical audit')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': f"{report['checks_passed']}/{report['checks_total']}",
                      'simulations': SIMULATIONS, 'all_null_rate': all_null_rate,
                      'one_false_target_limit_rate': one_alt_rate}))
    if report['status'] != 'PASS':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
