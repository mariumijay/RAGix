"""
Dense FAISS Retriever
Searches the FAISS index with a query embedding and returns top-k results.
"""

import logging
import numpy as np
from typing import Optional

import faiss

from ingestion.embedder import embed_query, load_faiss_index, load_metadata, get_dataset_paths

logger = logging.getLogger(__name__)


class FAISSRetriever:
    def __init__(self, dataset: str = "urdu_A"):
        self._dataset  = dataset
        self._index:    Optional[faiss.IndexFlatIP] = None
        self._metadata: Optional[list[dict]] = None

    def load(self) -> bool:
        paths = get_dataset_paths(self._dataset)
        if not paths["faiss"].exists() or not paths["metadata"].exists():
            logger.warning("FAISS index or metadata not found for dataset '%s'.", self._dataset)
            return False
        self._index    = faiss.read_index(str(paths["faiss"]))
        self._metadata = load_metadata(self._dataset)
        logger.info("FAISSRetriever[%s] ready: %d vectors", self._dataset, self._index.ntotal)
        return True

    @property
    def is_ready(self) -> bool:
        return self._index is not None and bool(self._metadata)

    @property
    def index(self):
        return self._index

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        if not self.is_ready:
            raise RuntimeError(f"FAISSRetriever[{self._dataset}] not loaded. Call load() first.")

        query_vec = embed_query(query)
        scores, indices = self._index.search(query_vec, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:
                continue
            meta = self._metadata[idx].copy()
            meta["score"]   = float(score)
            meta["rank"]    = rank
            meta["source"]  = "faiss"
            meta["dataset"] = self._dataset
            results.append(meta)
        return results
