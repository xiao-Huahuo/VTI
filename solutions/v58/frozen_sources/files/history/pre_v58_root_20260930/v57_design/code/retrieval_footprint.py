#!/usr/bin/env python3
"""Draft ordered Top-5 retrieval footprint (1925 float32 values)."""
from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Callable, Sequence

import numpy as np

TOP_K = 5
EMBED_DIMS = 384
OUTPUT_DIMS = TOP_K * (EMBED_DIMS + 1)
WEIGHTS = np.array([1 / math.log2(rank + 1) for rank in range(1, TOP_K + 1)], dtype=np.float32)


def normalize_text(text: str) -> str:
    value = unicodedata.normalize('NFC', text.replace('\r\n', '\n'))
    return re.sub(r'\s+', ' ', value).strip()


def footprint(retrieved_top10: Sequence[str], embed: Callable[[list[str]], Sequence[Sequence[float]]]) -> np.ndarray:
    if not isinstance(retrieved_top10, (tuple, list)) or len(retrieved_top10) > 10:
        raise ValueError('Expected an ordered Top-10-or-shorter retrieval sequence')
    if any(not isinstance(item, str) for item in retrieved_top10):
        raise TypeError('Retrieval items must be strings')
    texts = [normalize_text(value) for value in retrieved_top10[:TOP_K]]
    if any(not value for value in texts):
        raise ValueError('Present retrieval item may not normalize to empty text')
    raw = np.asarray(embed(texts), dtype=np.float32) if texts else np.empty((0, EMBED_DIMS), dtype=np.float32)
    if raw.shape != (len(texts), EMBED_DIMS) or not np.isfinite(raw).all():
        raise ValueError('Embedding shape/non-finite drift')
    vectors = np.zeros((TOP_K, EMBED_DIMS), dtype=np.float32)
    presence = np.zeros(TOP_K, dtype=np.float32)
    if len(texts):
        norms = np.linalg.norm(raw, axis=1)
        if not np.isfinite(norms).all() or np.any(norms <= 0):
            raise ValueError('Zero or non-finite embedding')
        vectors[:len(texts)] = (raw / norms[:, None]).astype(np.float32)
        presence[:len(texts)] = 1.0
    vectors *= WEIGHTS[:, None]
    presence *= WEIGHTS
    output = np.concatenate((vectors.reshape(-1), presence)).astype(np.float32)
    if output.shape != (OUTPUT_DIMS,) or not np.isfinite(output).all():
        raise RuntimeError('Footprint dimension/non-finite drift')
    return output
