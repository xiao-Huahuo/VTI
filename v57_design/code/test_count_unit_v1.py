#!/usr/bin/env python3
"""Read-only source binding and synthetic scorer test audit."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from count_unit_v1 import HERE, score, source_bound_cases


def main():
    cases = source_bound_cases()
    vectors = json.loads((HERE / 'COUNT_UNIT_V1_TEST_VECTORS.json').read_text())['vectors']
    if len(cases) != 3 or len(vectors) < 30:
        raise RuntimeError('Development source or synthetic coverage incomplete')
    outcomes = []
    for item in vectors:
        found = score(item['case'], item['answer'], cases=cases)
        outcomes.append({'case': item['case'], 'answer': item['answer'],
                         'expected': item['expected'], 'actual': found['status'],
                         'passed': found['status'] == item['expected']})
    report = {'schema': 'c33-v57-count-unit-v1-test-audit',
              'at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS' if all(x['passed'] for x in outcomes) else 'FAIL',
              'passed': sum(x['passed'] for x in outcomes), 'total': len(outcomes),
              'source_bound_cases': sorted(cases), 'model_calls': 0,
              'outcomes': outcomes}
    path = HERE / 'results/COUNT_UNIT_V1_AUDIT.json'
    if path.exists():
        raise RuntimeError('Refusing to overwrite count scorer audit')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'passed': report['passed'], 'total': report['total'],
                      'failures': [x for x in outcomes if not x['passed']]}, ensure_ascii=False))
    if report['status'] != 'PASS':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
