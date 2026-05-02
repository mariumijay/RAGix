"""
Embedder + FAISS Indexer
Embeds Urdu text chunks using a multilingual sentence-transformer
and stores them in a FAISS index alongside a JSON metadata sidecar.
"""

import os
import json
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import Optional

import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from ingestion.chunker import Chunk
from ingestion.cleaner import normalize_for_search

logger = logging.getLogger(__name__)

EMBEDDINGS_DIR = Path("embeddings")


def get_dataset_paths(dataset: str) -> dict[str, Path]:
    """Return paths dict for a named dataset. Creates the folder if needed."""
    base = EMBEDDINGS_DIR / dataset
    base.mkdir(parents=True, exist_ok=True)
    return {
        "faiss":    base / "faiss.index",
        "metadata": base / "metadata.json",
        "bm25":     base / "bm25.pkl",
        "config":   base / "index_config.json",
    }


# ---------------------------------------------------------------------------
# Singleton model loader
# ---------------------------------------------------------------------------
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
        logger.info(f"Loading embedding model: {model_name}")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    model = get_embedding_model()
    model_name = os.getenv("EMBEDDING_MODEL", "")
    prefixed = ["passage: " + t for t in texts] if "e5" in model_name.lower() else texts
    embeddings = model.encode(
        prefixed,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 50,
    )
    return np.array(embeddings, dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    model = get_embedding_model()
    model_name = os.getenv("EMBEDDING_MODEL", "")
    prefixed = "query: " + query if "e5" in model_name.lower() else query
    return np.array(model.encode([prefixed], normalize_embeddings=True), dtype=np.float32)


# ---------------------------------------------------------------------------
# FAISS index management
# ---------------------------------------------------------------------------

def build_indexes(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    logger.info(f"FAISS index built: {index.ntotal} vectors, dim={dim}")
    return index


def save_faiss_index(index: faiss.IndexFlatIP, dataset: str = "urdu_A") -> None:
    path = get_dataset_paths(dataset)["faiss"]
    faiss.write_index(index, str(path))
    logger.info(f"FAISS index saved → {path}")


def load_faiss_index(dataset: str = "urdu_A") -> Optional[faiss.IndexFlatIP]:
    path = get_dataset_paths(dataset)["faiss"]
    if not path.exists():
        return None
    index = faiss.read_index(str(path))
    logger.info(f"FAISS index loaded: {index.ntotal} vectors")
    return index


# ---------------------------------------------------------------------------
# Metadata sidecar (JSON)
# ---------------------------------------------------------------------------

def save_metadata(chunks: list[Chunk], dataset: str = "urdu_A") -> None:
    path = get_dataset_paths(dataset)["metadata"]
    data = [{"faiss_index": i, **c.to_dict()} for i, c in enumerate(chunks)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Metadata saved: {len(data)} chunks → {path}")


def load_metadata(dataset: str = "urdu_A") -> list[dict]:
    path = get_dataset_paths(dataset)["metadata"]
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# BM25 index
# ---------------------------------------------------------------------------

def _tokenize_urdu(text: str) -> list[str]:
    return normalize_for_search(text).split()


def build_bm25_index(chunks: list[Chunk]) -> BM25Okapi:
    tokenized = [_tokenize_urdu(c.text) for c in chunks]
    bm25 = BM25Okapi(tokenized)
    logger.info(f"BM25 index built: {len(tokenized)} documents")
    return bm25


def save_bm25_index(bm25: BM25Okapi, dataset: str = "urdu_A") -> None:
    path = get_dataset_paths(dataset)["bm25"]
    with open(path, "wb") as f:
        pickle.dump(bm25, f)
    logger.info(f"BM25 index saved → {path}")


def load_bm25_index(dataset: str = "urdu_A") -> Optional[BM25Okapi]:
    path = get_dataset_paths(dataset)["bm25"]
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------------------------
# Full ingestion pipeline
# ---------------------------------------------------------------------------

def ingest_chunks(chunks: list[Chunk], dataset: str = "urdu_A") -> dict:
    """
    Full ingestion pipeline for a named dataset.
    Saves to embeddings/<dataset>/{faiss.index, bm25.pkl, metadata.json}.
    """
    if not chunks:
        raise ValueError("No chunks provided for ingestion.")

    logger.info(f"Ingesting {len(chunks)} chunks into dataset '{dataset}'...")
    texts = [c.text for c in chunks]

    embeddings = embed_texts(texts)
    index = build_indexes(embeddings)
    save_faiss_index(index, dataset)

    bm25 = build_bm25_index(chunks)
    save_bm25_index(bm25, dataset)

    save_metadata(chunks, dataset)

    assert index.ntotal == len(chunks), (
        f"FAISS has {index.ntotal} vectors but {len(chunks)} chunks were provided"
    )

    embedding_model = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    config_path = get_dataset_paths(dataset)["config"]
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({
            "dataset":          dataset,
            "embedding_model":  embedding_model,
            "embedding_dim":    int(embeddings.shape[1]),
            "faiss_vectors":    index.ntotal,
            "metadata_entries": len(chunks),
        }, f, indent=2)
    logger.info(f"Index config saved → {config_path}")

    stats = {
        "dataset":         dataset,
        "chunks_indexed":  len(chunks),
        "embedding_dim":   int(embeddings.shape[1]),
        "embedding_model": embedding_model,
        "faiss_total":     index.ntotal,
    }
    logger.info(f"Ingestion complete: {stats}")
    return stats
