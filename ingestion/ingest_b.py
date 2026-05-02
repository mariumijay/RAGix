"""
ingestion/ingest_b.py — Ingest Urdu B source documents into embeddings/urdu_B/.

Saves to embeddings/urdu_B/{faiss.index, bm25.pkl, metadata.json}
Never touches the urdu_A dataset.

Usage:
    python -m ingestion.ingest_b <folder_path>

Supported folder layouts
------------------------
Layout A — genre subfolders (preferred):
    <folder>/
        application/
            leave_application.txt
        letter/
            informal_friend.txt
        essay/
            ...

Layout B — manifest file:
    <folder>/
        manifest.json   ← list of {file, genre, sub_type, topic,
                                    format_section, source, board, grade}
        leave_application.txt
        ...

Layout C — flat fallback:
    <folder>/
        any_file.txt    ← genre defaults to "essay"
"""

from __future__ import annotations

import argparse
import json
import logging
import pickle
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from ingestion.cleaner import clean_text, normalize_for_search
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_texts, get_dataset_paths

logger = logging.getLogger(__name__)

DATASET = "urdu_B"

VALID_GENRES = frozenset({
    "letter", "application", "story", "dialogue",
    "mcq", "tashreeh_ghazal", "tashreeh_nazam", "nasar_tashreeh",
    "khulasa", "markazi_khyal", "short_question",
    "zarbul_imsal", "sentence_correction",
})

GENRE_CHUNK_CONFIG: dict[str, dict] = {
    "mcq":                 {"chunk_size": 60,   "overlap": 10},
    "zarbul_imsal":        {"chunk_size": 70,   "overlap": 10},
    "sentence_correction": {"chunk_size": 70,   "overlap": 10},
    "tashreeh_ghazal":     {"chunk_size": 80,   "overlap": 0},
    "tashreeh_nazam":      {"chunk_size": 100,  "overlap": 20},
    "nasar_tashreeh":      {"chunk_size": 130,  "overlap": 30},
    "short_question":      {"chunk_size": 100,  "overlap": 20},
    "khulasa":             {"chunk_size": 220,  "overlap": 50},
    "markazi_khyal":       {"chunk_size": 170,  "overlap": 40},
    "letter":              {"chunk_size": 9999, "overlap": 0},
    "application":         {"chunk_size": 9999, "overlap": 0},
    "story":               {"chunk_size": 220,  "overlap": 40},
    "dialogue":            {"chunk_size": 180,  "overlap": 30},
}
_DEFAULT_CHUNK = {"chunk_size": 150, "overlap": 30}


def _tokenize(text: str) -> list[str]:
    return normalize_for_search(text).split()


def _load_folder(folder: Path) -> list[dict]:
    docs: list[dict] = []

    manifest_path = folder / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            manifest: list[dict] = json.load(f)
        for entry in manifest:
            file_path = folder / entry["file"]
            if not file_path.exists():
                logger.warning("Manifest references missing file: %s", file_path)
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "genre":          entry.get("genre",          "essay"),
                "sub_type":       entry.get("sub_type",       file_path.stem),
                "topic":          entry.get("topic",          file_path.stem.replace("_", " ")),
                "format_section": entry.get("format_section", "full"),
                "source":         entry.get("source",         folder.name),
                "board":          entry.get("board",          "lahore"),
                "grade":          entry.get("grade",          "9"),
                "text":           text,
            })
        return docs

    for sub in sorted(folder.iterdir()):
        if sub.is_dir() and sub.name in VALID_GENRES:
            for txt_file in sorted(sub.glob("*.txt")):
                text = txt_file.read_text(encoding="utf-8", errors="ignore")
                docs.append({
                    "genre":          sub.name,
                    "sub_type":       txt_file.stem,
                    "topic":          txt_file.stem.replace("_", " "),
                    "format_section": "full",
                    "source":         folder.name,
                    "board":          "lahore",
                    "grade":          "9",
                    "text":           text,
                })

    if not docs:
        for txt_file in sorted(folder.glob("*.txt")):
            text = txt_file.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "genre":          "essay",
                "sub_type":       txt_file.stem,
                "topic":          txt_file.stem.replace("_", " "),
                "format_section": "full",
                "source":         folder.name,
                "board":          "lahore",
                "grade":          "9",
                "text":           text,
            })

    return docs


def ingest_folder(folder_path: str) -> dict:
    """
    Full Urdu B ingestion pipeline.
    Saves indexes to embeddings/urdu_B/.
    """
    from pathlib import Path

    path = Path(folder_path)

    if not path.exists():
        raise ValueError(f"Path not found: {path}")

    # Case 1: single file
    if path.is_file():
        if path.suffix != ".txt":
            raise ValueError(f"Only .txt files supported: {path}")
        raw_docs = [path]   # treat single file as list

    # Case 2: folder
    elif path.is_dir():
        raw_docs = _load_folder(path)

    else:
        raise ValueError(f"Invalid path: {path}")

    if not raw_docs:
        raise ValueError(f"No .txt documents found in: {path}")

    paths = get_dataset_paths(DATASET)   # ← was missing
    all_meta: list[dict] = []            # ← was missing
    chunk_idx = 0                        # ← was missing

    for doc in raw_docs:                 # ← the loop that was missing
        cleaned = clean_text(doc["text"])
        _cfg = GENRE_CHUNK_CONFIG.get(doc["genre"], _DEFAULT_CHUNK)
        chunks = chunk_text(
            clean_text  = cleaned,
            book_title  = doc.get("source", ""),
            author      = "",
            chapter     = doc.get("genre", ""),
            page_number = 1,
            chunk_size  = _cfg["chunk_size"],
            overlap     = _cfg["overlap"],
        )
        for c in chunks:
            all_meta.append({
                "chunk_id":       f"urdu_b_{chunk_idx:04d}",
                "faiss_index":    chunk_idx,
                "genre":          doc["genre"],
                "sub_type":       doc["sub_type"],
                "topic":          doc["topic"],
                "format_section": doc["format_section"],
                "source":         doc["source"],
                "board":          doc["board"],
                "grade":          doc["grade"],
                "dataset":        DATASET,
                "text":           c.text,
                "token_count":    c.token_count,
            })
            chunk_idx += 1

    if not all_meta:
        raise ValueError("Chunking produced no output — check source documents.")

    logger.info("Produced %d chunks across genres: %s",
                len(all_meta), sorted({m["genre"] for m in all_meta}))

    texts = [m["text"] for m in all_meta]
    embeddings: np.ndarray = embed_texts(texts)
    dim = int(embeddings.shape[1])

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, str(paths["faiss"]))
    logger.info("Urdu B FAISS index saved → %s (%d vectors)", paths["faiss"], index.ntotal)

    tokenized = [_tokenize(t) for t in texts]
    bm25 = BM25Okapi(tokenized)
    with open(paths["bm25"], "wb") as f:
        pickle.dump(bm25, f)
    logger.info("Urdu B BM25 index saved → %s", paths["bm25"])

    with open(paths["metadata"], "w", encoding="utf-8") as f:
        json.dump(all_meta, f, ensure_ascii=False, indent=2)
    logger.info("Urdu B metadata saved → %s", paths["metadata"])

    return {
        "dataset":        DATASET,
        "chunks_indexed": len(all_meta),
        "embedding_dim":  dim,
        "faiss_total":    index.ntotal,
        "genres":         sorted({m["genre"] for m in all_meta}),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Ingest Urdu B documents into embeddings/urdu_B/")
    parser.add_argument("folder", help="Path to folder containing Urdu B source .txt files")
    args = parser.parse_args()

    stats = ingest_folder(args.folder)
    print(f"\n[OK] Ingestion complete:")
    print(f"     Dataset        : {stats['dataset']}")
    print(f"     Chunks indexed : {stats['chunks_indexed']}")
    print(f"     Embedding dim  : {stats['embedding_dim']}")
    print(f"     FAISS total    : {stats['faiss_total']}")
    print(f"     Genres found   : {stats['genres']}")
