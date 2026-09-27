#!/usr/bin/env python3
"""Synthetic-only audit of retrieval normalization, rank, duplicates and padding."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from retrieval_footprint import EMBED_DIMS, OUTPUT_DIMS, WEIGHTS, footprint, normalize_text

OUT = Path(__file__).resolve().parents[1] / 'results/RETRIEVAL_FOOTPRINT_DRY_RUN.json'


def fake_embed(texts):
    rows = []
    for text in texts:
        vector = np.zeros(EMBED_DIMS, dtype=np.float32)
        vector[int.from_bytes(hashlib.sha256(text.encode()).digest()[:2], 'big') % EMBED_DIMS] = 1
        rows.append(vector)
    return rows


def main():
    checks = {}
    def check(name, truth):
        checks[name] = bool(truth)

    check('nfc_and_whitespace', normalize_text('  cafe\u0301\r\n   test  ') == 'café test')
    empty = footprint([], fake_embed)
    check('empty_is_1925_zeros', empty.shape == (OUTPUT_DIMS,) and empty.dtype == np.float32 and not empty.any())
    one = footprint(['alpha'], fake_embed)
    two = footprint(['alpha', 'beta'], fake_embed)
    swapped = footprint(['beta', 'alpha'], fake_embed)
    duplicate = footprint(['alpha', 'alpha'], fake_embed)
    check('count_mask', np.allclose(one[-5:], [WEIGHTS[0], 0, 0, 0, 0]) and
          np.allclose(two[-5:], [WEIGHTS[0], WEIGHTS[1], 0, 0, 0]))
    check('rank_order_matters', not np.array_equal(two, swapped))
    check('duplicate_preserved', np.array_equal(duplicate[:EMBED_DIMS],
                                               duplicate[EMBED_DIMS:2*EMBED_DIMS] / WEIGHTS[1]))
    check('top_five_only', np.array_equal(footprint(['a','b','c','d','e','f'],fake_embed),
                                         footprint(['a','b','c','d','e','other'],fake_embed)))
    check('normalization_equivalence', np.array_equal(footprint(['cafe\u0301  test'],fake_embed),
                                                      footprint(['café test'],fake_embed)))
    try:
        footprint(['  '], fake_embed)
    except ValueError:
        check('empty_present_item_rejected', True)
    else:
        check('empty_present_item_rejected', False)

    report = {'schema': 'c33-v57-draft-retrieval-footprint-audit-v1',
              'at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS' if all(checks.values()) else 'FAIL',
              'checks': checks, 'checks_passed': sum(checks.values()),
              'checks_total': len(checks), 'model_calls': 0,
              'note': 'Fake embeddings only; BGE runtime digest and real provider retrieval remain untested.'}
    if OUT.exists():
        raise RuntimeError('Refusing to overwrite footprint dry-run')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': f"{report['checks_passed']}/{report['checks_total']}"}))
    if report['status'] != 'PASS':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
