#!/usr/bin/env python3
"""Lightweight audit of the generated starter BibTeX and cached registries."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from build_references import ARXIV, CROSSREF, bib_entry

HERE = Path(__file__).resolve().parent
BIB = HERE / 'references.bib'
OUT = HERE / 'REFERENCE_LIBRARY_AUDIT.json'


def main():
    text = BIB.read_text(encoding='utf-8')
    blocks = re.findall(r'@(?:misc|article)\{([^,]+),\n(.*?)\n\}', text, flags=re.S)
    keys = [key for key, _ in blocks]
    checks = {}
    checks['twenty_entries'] = len(blocks) == 20
    checks['unique_keys'] = len(keys) == len(set(keys))
    checks['mandatory_fields'] = all(all(re.search(rf'^  {field} = \{{.+\}},?$', body, flags=re.M)
                                         for field in ('author', 'title', 'year', 'url')) for _, body in blocks)
    checks['registry_snapshots'] = len(list((HERE / 'metadata').glob('*.json'))) == 18
    checks['registry_identifiers'] = all(
        json.loads((HERE / 'metadata' / f'{key}.json').read_text())['identifier'] == identifier
        for key, identifier in {**ARXIV, **CROSSREF}.items())
    checks['entries_match_registry_snapshots'] = all(
        bib_entry(key) in text for key in [*ARXIV, *CROSSREF])
    checks['arxiv_primary_links'] = sum('https://arxiv.org/abs/' in body for _, body in blocks) == 15
    checks['journal_doIs'] = all(f'  doi = {{{doi}}}' in text for doi in (
        '10.1111/j.1541-0420.2007.00984.x',
        '10.1016/j.jspi.2013.03.018',
        '10.1080/01621459.2020.1750415'))
    checks['publisher_year_for_wu_ding'] = bool(re.search(r'@article\{RandomizationWeakNull2021,.*?year = \{2021\}', text, re.S))
    checks['static_primary_artifacts'] = 'RedisMemoryHarness2026' in keys and 'Mem0QdrantResetIssue2026' in keys
    result = {'schema': 'c33-starter-bibliography-audit-v1',
              'at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS' if all(checks.values()) else 'FAIL',
              'checks': checks, 'checks_passed': sum(checks.values()), 'checks_total': len(checks),
              'keys': keys, 'bib_sha256': hashlib.sha256(BIB.read_bytes()).hexdigest(),
              'boundary': 'Metadata/structure audit only; final venue normalization and full-text claim verification remain pending.'}
    if OUT.exists():
        raise RuntimeError('Refusing to overwrite bibliography audit')
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': f"{result['checks_passed']}/{result['checks_total']}", 'entries': len(blocks)}))
    if result['status'] != 'PASS':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
