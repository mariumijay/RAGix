"""
preprocess.py  —  ONE-TIME SETUP SCRIPT
========================================
Run this ONCE before starting the system:

    python preprocess.py --book path/to/your_book.txt \
                         --title "کتاب کا نام" \
                         --author "مصنف کا نام"

Saves indexes to embeddings/urdu_A/.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from ingestion.cleaner import clean_text
from ingestion.chunker import chunk_text
from ingestion.embedder import ingest_chunks


def preprocess(book_path: str, title: str = "Urdu", author: str = "Unknown") -> None:
    print(f"\n{'='*60}")
    print("  Urdu RAG — Preprocessing Pipeline  [dataset: urdu_A]")
    print(f"{'='*60}")
    print(f"  Book  : {book_path}")
    print(f"  Title : {title}")
    print(f"  Author: {author}")
    print(f"{'='*60}\n")

    print("[1/4] Loading book …")
    with open(book_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    print(f"      Loaded {len(raw_text):,} characters.\n")

    print("[2/4] Cleaning / normalising Urdu text …")
    t0 = time.time()
    clean = clean_text(raw_text)
    print(f"      Done in {time.time()-t0:.1f}s  ({len(clean):,} chars after cleaning)\n")

    print("[3/4] Chunking on sentence boundaries …")
    t0 = time.time()
    chunks = chunk_text(clean, book_title=title, author=author, chunk_size=300, overlap=60)
    print(f"      Done in {time.time()-t0:.1f}s  ({len(chunks):,} chunks created)\n")

    print("[4/4] Embedding chunks and building FAISS + BM25 indexes …")
    t0 = time.time()
    ingest_chunks(chunks, dataset="urdu_A")
    print(f"      Done in {time.time()-t0:.1f}s\n")

    manifest = {
        "book_title":        title,
        "author":            author,
        "source_file":       os.path.abspath(book_path),
        "total_chunks":      len(chunks),
        "preprocessed_at":   time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    os.makedirs("embeddings/urdu_A", exist_ok=True)
    with open("embeddings/urdu_A/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("="*60)
    print("  ✓  Preprocessing complete!")
    print(f"     {len(chunks)} chunks saved to embeddings/urdu_A/")
    print("="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess an Urdu book for RAG (dataset: urdu_A)")
    parser.add_argument("--book",   required=True,    help="Path to the .txt Urdu book file")
    parser.add_argument("--title",  default="Unknown", help="Book title (Urdu)")
    parser.add_argument("--author", default="Unknown", help="Author name (Urdu)")
    args = parser.parse_args()

    if not os.path.exists(args.book):
        print(f"ERROR: File not found: {args.book}")
        sys.exit(1)

    preprocess(args.book, args.title, args.author)
