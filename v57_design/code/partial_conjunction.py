#!/usr/bin/env python3
"""Draft V57 5+5 Fisher energy tests and 2-of-3 partial conjunction.

Statistical code only. The lifecycle experiment and 1925-D footprint remain
unfrozen; this module makes no model, benchmark or database calls.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

SLOTS = 10
GROUP = 5
FORMAL_DIMS = 1925
ASSIGNMENTS = tuple(itertools.combinations(range(SLOTS), GROUP))
ASSIGNMENT_INDEX = {assignment: index for index, assignment in enumerate(ASSIGNMENTS)}
TREATMENT_MASK = np.zeros((len(ASSIGNMENTS), SLOTS), dtype=np.float64)
for row, assignment in enumerate(ASSIGNMENTS):
    TREATMENT_MASK[row, list(assignment)] = 1.0
CONTROL_MASK = 1.0 - TREATMENT_MASK


def _validate(vectors, treated_slots, *, formal: bool) -> np.ndarray:
    data = np.asarray(vectors, dtype=np.float64)
    if data.ndim != 2 or data.shape[0] != SLOTS or data.shape[1] < 1:
        raise ValueError('Each target requires ten vectors with a shared dimension')
    if formal and data.shape[1] != FORMAL_DIMS:
        raise ValueError('Formal retrieval footprint requires exactly 1925 dimensions')
    if not np.isfinite(data).all():
        raise ValueError('Non-finite vector')
    if tuple(sorted(treated_slots)) not in ASSIGNMENT_INDEX:
        raise ValueError('Exactly five distinct treatment slots 0..9 required')
    return data


def energy_tables(vectors: np.ndarray) -> np.ndarray:
    """For B datasets of ten vectors, return B x 252 legal statistics."""
    rows = np.asarray(vectors, dtype=np.float64)
    if rows.ndim != 3 or rows.shape[1] != SLOTS or not np.isfinite(rows).all():
        raise ValueError('Expected a batch of B x 10 x D finite vectors')
    distances = np.linalg.norm(rows[:, :, None, :] - rows[:, None, :, :], axis=3)
    cross = np.einsum('ai,nij,aj->na', CONTROL_MASK, distances, TREATMENT_MASK, optimize=True)
    within_control = np.einsum('ai,nij,aj->na', CONTROL_MASK, distances, CONTROL_MASK, optimize=True)
    within_treatment = np.einsum('ai,nij,aj->na', TREATMENT_MASK, distances, TREATMENT_MASK, optimize=True)
    return (2 * cross - within_control - within_treatment) / (GROUP * GROUP)


def target_test(vectors, treated_slots, *, formal: bool = False) -> dict:
    treated = tuple(sorted(int(slot) for slot in treated_slots))
    rows = _validate(vectors, treated, formal=formal)
    table = energy_tables(rows[None, :, :])[0]
    observed = float(table[ASSIGNMENT_INDEX[treated]])
    tolerance = 1e-12 * max(1.0, abs(observed))
    extreme = int(np.count_nonzero(table >= observed - tolerance))
    return {'observed_energy': observed, 'extreme_or_tied_assignments': extreme,
            'total_assignments': len(ASSIGNMENTS), 'p_value': extreme / len(ASSIGNMENTS),
            'treated_slots': list(treated)}


def partial_conjunction(p_values: list[float], *, backend_alpha: float = 0.025) -> dict:
    if len(p_values) != 3 or any(not np.isfinite(p) or not 0 <= p <= 1 for p in p_values):
        raise ValueError('Exactly three finite target p-values in [0,1] required')
    ordered = sorted(float(p) for p in p_values)
    combined = min(1.0, 2 * ordered[1])
    return {'target_p_values': list(map(float, p_values)), 'ordered_p_values': ordered,
            'partial_conjunction_p_2_of_3': combined, 'backend_alpha': backend_alpha,
            'decision': 'REPLICATED_RETRIEVAL_INFLUENCE' if combined < backend_alpha else 'INFLUENCE_NOT_DETECTED',
            'null': 'At most one of three target sharp nulls is false'}


def backend_test(targets: list[dict], *, formal: bool = False) -> dict:
    if len(targets) != 3:
        raise ValueError('Exactly the three frozen targets required')
    tests = [target_test(item['vectors'], item['treated_slots'], formal=formal) for item in targets]
    return {'target_tests': tests, **partial_conjunction([test['p_value'] for test in tests])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--formal', action='store_true')
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    print(json.dumps(backend_test(data['targets'], formal=args.formal), indent=2))


if __name__ == '__main__':
    main()
