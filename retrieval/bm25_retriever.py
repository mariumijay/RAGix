"""
Sparse BM25 Retriever
Keyword-based retrieval over tokenized Urdu chunks.
"""

import logging
import numpy as np
from typing import Optional

from rank_bm25 import BM25Okapi

from ingestion.embedder import load_bm25_index, load_metadata, get_dataset_paths
from ingestion.cleaner import normalize_for_search

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> list[str]:
    return normalize_for_search(text).split()


class BM25Retriever:
    def __init__(self, dataset: str = "urdu_A"):
        self._dataset  = dataset
        self._bm25:     Optional[BM25Okapi] = None
        self._metadata: Optional[list[dict]] = None

    def load(self) -> bool:
        paths = get_dataset_paths(self._dataset)
        if not paths["bm25"].exists() or not paths["metadata"].exists():
            logger.warning("BM25 index or metadata not found for dataset '%s'.", self._dataset)
            return False
        self._bm25     = load_bm25_index(self._dataset)
        self._metadata = load_metadata(self._dataset)
        logger.info("BM25Retriever[%s] ready", self._dataset)
        return True

    @property
    def is_ready(self) -> bool:
        return self._bm25 is not None and bool(self._metadata)

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        if not self.is_ready:
            raise RuntimeError(f"BM25Retriever[{self._dataset}] not loaded. Call load() first.")

        tokens = _tokenize(query)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices):
            score = float(scores[idx])
            if score <= 0:
                continue
            meta = self._metadata[idx].copy()
            meta["score"]   = score
            meta["rank"]    = rank
            meta["source"]  = "bm25"
            meta["dataset"] = self._dataset
            results.append(meta)
        return results
