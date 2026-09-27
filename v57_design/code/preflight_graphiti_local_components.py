#!/usr/bin/env python3
"""Toy-only local BGE/reranker injection audit; no Neo4j or LLM inference."""
from __future__ import annotations

import os

if os.environ.get('OPENAI_API_KEY'):
    raise RuntimeError('Remote OpenAI key must be absent')
os.environ['GRAPHITI_TELEMETRY_ENABLED'] = 'false'
os.environ['EMBEDDING_DIM'] = '384'

import asyncio
import hashlib
import importlib.metadata
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

from graphiti_core import Graphiti
from graphiti_core.embedder.client import EMBEDDING_DIM
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.telemetry import is_telemetry_enabled

from local_graphiti_components import BGECosineReranker, FastEmbedBGE

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'v57_design/results/GRAPHITI_LOCAL_COMPONENT_AUDIT.json'
CACHE = ROOT / '.runtime/fastembed-cache'
BGE_REPO_CACHE = CACHE / 'models--Qdrant--bge-small-en-v1.5-onnx-Q'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def cache_digest() -> tuple[str, int]:
    asset = json.loads((ROOT / 'v57_design/DOWNLOADABLE_ASSETS.json').read_text())['measurement_embedding']
    snapshot = BGE_REPO_CACHE / 'snapshots' / asset['observed_hf_revision']
    files = sorted(p for p in snapshot.rglob('*') if p.is_file())
    h = hashlib.sha256()
    for path in files:
        h.update(path.relative_to(snapshot).as_posix().encode() + b'\0' + sha(path).encode() + b'\n')
    return h.hexdigest(), len(files)


async def probe():
    embedder = FastEmbedBGE()
    reranker = BGECosineReranker(embedder)
    vectors = await embedder.create_batch(['toy apple', 'toy banana'])
    ranked = await reranker.rank('toy apple', ['toy banana', 'toy apple', 'toy apple'])
    return embedder, reranker, vectors, ranked


def main():
    checks = {}
    def check(name, truth):
        checks[name] = bool(truth)

    embedder, reranker, vectors, ranked = asyncio.run(probe())
    digest, files = cache_digest()
    asset = json.loads((ROOT / 'v57_design/DOWNLOADABLE_ASSETS.json').read_text())['measurement_embedding']
    expected = asset['snapshot_tree_sha256']
    check('bge_snapshot_matches_active_manifest', digest == expected and files >= 1)
    check('toy_embeddings_are_384', len(vectors) == 2 and all(len(row) == 384 for row in vectors))
    check('toy_rerank_content_and_duplicates', len(ranked) == 3 and ranked[0][0] == 'toy apple' and
          sum(value == 'toy apple' for value, _ in ranked) == 2)
    config = LLMConfig(api_key='local-uninvoked', model='qwen3:14b-q4_K_M',
                       base_url='http://127.0.0.1:11434/v1', temperature=0)
    llm = OpenAIGenericClient(config=config, structured_output_mode='json_schema')
    graph = Graphiti(uri='bolt://127.0.0.1:17687', user='neo4j', password='constructor-only',
                     llm_client=llm, embedder=embedder, cross_encoder=reranker)
    check('real_local_clients_injected', graph.llm_client is llm and graph.embedder is embedder and graph.cross_encoder is reranker)
    check('dimension_384_before_import', EMBEDDING_DIM == 384)
    check('telemetry_and_openai_key_absent', not is_telemetry_enabled() and not os.environ.get('OPENAI_API_KEY'))
    check('graphiti_package_0_30_2', importlib.metadata.version('graphiti-core') == '0.30.2')
    asyncio.run(graph.close())
    report = {'schema': 'c33-v57-graphiti-local-components-toy-audit-v1',
              'at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS_TOY_COMPONENTS_ONLY' if all(checks.values()) else 'FAIL',
              'checks': checks, 'checks_passed': sum(checks.values()), 'checks_total': len(checks),
              'bge_cache_tree_sha256': digest, 'bge_cache_file_count': files,
              'graphiti_constructor_sha256': sha(Path(inspect.getfile(Graphiti))),
              'local_components_sha256': sha(Path(__file__).with_name('local_graphiti_components.py')),
              'llm_model_calls': 0, 'database_queries': 0,
              'boundary': 'Synthetic text embeddings only. Neo4j health/reset/teardown and real structured output remain untested.'}
    if OUT.exists():
        raise RuntimeError('Refusing to overwrite local component audit')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': f"{report['checks_passed']}/{report['checks_total']}"}))
    if not all(checks.values()):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
