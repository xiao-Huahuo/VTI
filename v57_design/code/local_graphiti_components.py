#!/usr/bin/env python3
"""Candidate Graphiti-Local BGE provider components; engineering stage only."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from graphiti_core.embedder.client import EmbedderClient
from graphiti_core.cross_encoder.client import CrossEncoderClient

ROOT = Path(__file__).resolve().parents[2]
MODEL = 'BAAI/bge-small-en-v1.5'
DIMS = 384


class FastEmbedBGE(EmbedderClient):
    def __init__(self, cache_dir: Path = ROOT / '.runtime/fastembed-cache'):
        asset = json.loads((ROOT / 'v57_design/DOWNLOADABLE_ASSETS.json').read_text())['measurement_embedding']
        snapshot = cache_dir / 'models--Qdrant--bge-small-en-v1.5-onnx-Q' / 'snapshots' / asset['observed_hf_revision']
        if not snapshot.is_dir():
            raise FileNotFoundError(f'Pinned BGE snapshot missing: {snapshot}')
        self.model = TextEmbedding(model_name=MODEL, cache_dir=str(cache_dir),
                                   local_files_only=True, specific_model_path=str(snapshot))
        self._lock = asyncio.Lock()

    async def create(self, input_data):
        if not isinstance(input_data, str):
            raise TypeError('Graphiti-Local expects text-only BGE inputs')
        result = await self.create_batch([input_data])
        return result[0]

    async def create_batch(self, input_data_list: list[str]):
        if any(not isinstance(value, str) for value in input_data_list):
            raise TypeError('Graphiti-Local expects text-only BGE inputs')
        if not input_data_list:
            return []
        async with self._lock:
            rows = await asyncio.to_thread(lambda: [np.asarray(row, dtype=np.float32) for row in self.model.embed(input_data_list)])
        if len(rows) != len(input_data_list) or any(row.shape != (DIMS,) or not np.isfinite(row).all() for row in rows):
            raise RuntimeError('BGE embedding shape/non-finite drift')
        return [row.astype(float).tolist() for row in rows]


class BGECosineReranker(CrossEncoderClient):
    """Disclosed local reranker using BGE cosine, not stock OpenAI logprobs."""
    def __init__(self, embedder: FastEmbedBGE):
        self.embedder = embedder

    async def rank(self, query: str, passages: list[str]):
        if not passages:
            return []
        vectors = np.asarray(await self.embedder.create_batch([query, *passages]), dtype=np.float64)
        norms = np.linalg.norm(vectors, axis=1)
        if np.any(norms <= 0):
            raise RuntimeError('Zero BGE vector in local reranker')
        normalized = vectors / norms[:, None]
        similarities = normalized[1:] @ normalized[0]
        return [(passages[index], float(similarities[index])) for index in
                sorted(range(len(passages)), key=lambda i: (-similarities[i], i))]
