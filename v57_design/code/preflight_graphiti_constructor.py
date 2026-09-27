#!/usr/bin/env python3
"""Zero-model, zero-database Graphiti injection/identity preflight."""
from __future__ import annotations

import os

if os.environ.get('OPENAI_API_KEY'):
    raise RuntimeError('Remote OpenAI API key must be absent')
os.environ['GRAPHITI_TELEMETRY_ENABLED'] = 'false'
os.environ['EMBEDDING_DIM'] = '384'  # Graphiti reads this at import time.

import asyncio
import hashlib
import importlib.metadata
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

from graphiti_core import Graphiti
from graphiti_core.embedder.client import EMBEDDING_DIM, EmbedderClient
from graphiti_core.cross_encoder.client import CrossEncoderClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.telemetry import is_telemetry_enabled

OUT = Path(__file__).resolve().parents[1] / 'results/GRAPHITI_CONSTRUCTOR_AUDIT.json'


class StubEmbedder(EmbedderClient):
    async def create(self, input_data):
        return [0.0] * 384

    async def create_batch(self, input_data_list):
        return [[0.0] * 384 for _ in input_data_list]


class StubReranker(CrossEncoderClient):
    async def rank(self, query, passages):
        return [(value, 0.0) for value in passages]


def main():
    checks = {}
    def check(name, truth):
        checks[name] = bool(truth)

    config = LLMConfig(api_key='local-constructor-only', model='qwen3:14b-q4_K_M',
                       base_url='http://127.0.0.1:11434/v1', temperature=0)
    llm = OpenAIGenericClient(config=config, structured_output_mode='json_schema')
    embedder = StubEmbedder()
    reranker = StubReranker()
    graph = Graphiti(uri='bolt://127.0.0.1:17687', user='neo4j',
                     password='constructor-only-unused', llm_client=llm,
                     embedder=embedder, cross_encoder=reranker)
    check('graphiti_core_0_30_2', importlib.metadata.version('graphiti-core') == '0.30.2')
    check('local_llm_client_injected', graph.llm_client is llm and config.base_url.startswith('http://127.0.0.1:'))
    check('custom_embedder_injected', graph.embedder is embedder and EMBEDDING_DIM == 384)
    check('custom_reranker_injected', graph.cross_encoder is reranker)
    check('telemetry_disabled', not is_telemetry_enabled())
    check('no_openai_key', not bool(os.environ.get('OPENAI_API_KEY')))
    asyncio.run(graph.close())
    source = Path(inspect.getfile(Graphiti))
    report = {
        'schema': 'c33-v57-graphiti-constructor-only-audit-v1',
        'status': 'PASS_CONSTRUCTOR_ONLY' if all(checks.values()) else 'FAIL',
        'at_utc': datetime.now(timezone.utc).isoformat(),
        'checks': checks, 'checks_passed': sum(checks.values()), 'checks_total': len(checks),
        'graphiti_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'model_calls': 0, 'database_queries': 0,
        'not_tested': ['Neo4j health', 'stock native reset', 'real local BGE embedder',
                       'real reranker', 'Graphiti structured output', 'ephemeral teardown'],
    }
    if OUT.exists():
        raise RuntimeError('Refusing to overwrite constructor audit')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': f"{report['checks_passed']}/{report['checks_total']}"}))
    if not all(checks.values()):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
