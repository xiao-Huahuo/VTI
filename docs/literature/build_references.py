#!/usr/bin/env python3
"""Build the C33 starter bibliography from cached DataCite/Crossref metadata."""
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
META = HERE / 'metadata'
OUTPUT = HERE / 'references.bib'
ARXIV = {
    'LongMemEval2024': '2410.10813',
    'AgenticChecklist2025': '2507.02825',
    'CrossUnitSeparation2026': '2608.14940',
    'MemSecBench2026': '2607.27080',
    'InteractiveDesignScience2026': '2605.17829',
    'ExecutionUnlearning2026': '2609.04875',
    'MemDelta2026': '2606.29914',
    'AutomatedBenchmarkAudit2026': '2605.26079',
    'ForgetEval2026': '2606.15903',
    'TemporalIntervention2026': '2607.21635',
    'TaskOrderFragility2026': '2608.18066',
    'ATMA2026': '2607.01935',
    'ScopeBeforePersist2026': '2609.29144',
    'DolphinBench2026': '2609.24971',
    'MemArena2026': '2608.02613',
}
CROSSREF = {
    'BenjaminiHeller2008PartialConjunction': '10.1111/j.1541-0420.2007.00984.x',
    'SzekelyRizzo2013Energy': '10.1016/j.jspi.2013.03.018',
    'RandomizationWeakNull2021': '10.1080/01621459.2020.1750415',
}


def fetch_one(kind: str, key: str, identifier: str):
    if kind == 'arxiv':
        url = 'https://api.datacite.org/dois/10.48550/arxiv.' + identifier
        attributes = 'data.attributes'
    else:
        url = 'https://api.crossref.org/works/' + urllib.parse.quote(identifier, safe='')
        attributes = 'message'
    request = urllib.request.Request(url, headers={'User-Agent': 'C33-literature-audit/1.0'})
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    value = payload
    for part in attributes.split('.'):
        value = value[part]
    path = META / f'{key}.json'
    path.write_text(json.dumps({'kind': kind, 'identifier': identifier, 'url': url,
                                'attributes': value}, ensure_ascii=False, indent=2) + '\n')
    return key


def safe(value: str) -> str:
    return str(value).replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')


def bib_entry(key: str) -> str:
    record = json.loads((META / f'{key}.json').read_text())
    value = record['attributes']
    if record['kind'] == 'arxiv':
        title = value['titles'][0]['title']
        authors = ' and '.join((p.get('givenName', '') + ' ' + p.get('familyName', '')).strip()
                               or p['name'] for p in value['creators'])
        year = str(value['publicationYear'])
        fields = {'author': authors, 'title': title, 'year': year,
                  'eprint': record['identifier'], 'archivePrefix': 'arXiv',
                  'doi': value['doi'], 'url': 'https://arxiv.org/abs/' + record['identifier']}
        category = 'misc'
    else:
        title = value['title'][0]
        authors = ' and '.join((p.get('given', '') + ' ' + p.get('family', '')).strip()
                               for p in value['author'])
        print_date = value.get('published-print') or value['published']
        year = str(print_date['date-parts'][0][0])
        fields = {'author': authors, 'title': title,
                  'journal': value.get('container-title', [''])[0], 'year': year,
                  'volume': str(value.get('volume', '')), 'number': str(value.get('issue', '')),
                  'pages': str(value.get('page', '')),
                  'doi': record['identifier'], 'url': value.get('URL', 'https://doi.org/' + record['identifier'])}
        category = 'article'
    if not title or not authors or not year:
        raise ValueError(f'Incomplete bibliographic metadata for {key}')
    body = ',\n'.join(f'  {name} = {{{safe(content)}}}' for name, content in fields.items() if content)
    return f'@{category}{{{key},\n{body}\n}}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true', help='fetch official registry snapshots')
    args = parser.parse_args()
    META.mkdir(parents=True, exist_ok=True)
    records = [('arxiv', key, identifier) for key, identifier in ARXIV.items()]
    records += [('crossref', key, identifier) for key, identifier in CROSSREF.items()]
    if args.fetch:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(fetch_one, *record) for record in records]
            for future in as_completed(futures):
                print('fetched', future.result(), flush=True)
    missing = [key for _, key, _ in records if not (META / f'{key}.json').is_file()]
    if missing:
        raise RuntimeError(f'Missing metadata snapshots: {missing}')
    text = '% C33 starter bibliography, generated from cached DOI-registry records.\n'
    text += '% Full-text claim verification remains tracked in RELATED_WORK_CURRENT.md.\n\n'
    entries = [bib_entry(key) for _, key, _ in records]
    entries += [
        '''@misc{RedisMemoryHarness2026,
  author = {Redis Applied AI Research},
  title = {Agent Memory Benchmark: Public Harness and Provider Recipes},
  year = {2026},
  howpublished = {GitHub repository, pinned project commit 94192c39e2a4a154f441a5411e3d73c4f54974a6},
  url = {https://github.com/redis/agent-memory-server/tree/94192c39e2a4a154f441a5411e3d73c4f54974a6/agent-memory-benchmark},
  note = {Accessed 2026-09-27}
}''',
        '''@misc{Mem0QdrantResetIssue2026,
  author = {Mem0 community},
  title = {Memory.reset() silently keeps memories on affected local Qdrant configurations},
  year = {2026},
  howpublished = {GitHub issue 6411},
  url = {https://github.com/mem0ai/mem0/issues/6411},
  note = {Issue correction limits reproduction to affected platforms and storage semantics; not a universal local-Qdrant defect}
}''',
    ]
    text += '\n\n'.join(entries) + '\n'
    OUTPUT.write_text(text, encoding='utf-8')
    print(f'wrote {OUTPUT} ({len(entries)} entries)')


if __name__ == '__main__':
    main()
