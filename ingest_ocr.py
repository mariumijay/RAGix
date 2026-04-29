import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.chunker import chunk_text
from ingestion.embedder import ingest_chunks

text = open("data/ocr.txt", encoding="utf-8").read()
chunks = chunk_text(text, book_title="اردو", author="", chapter="", page_number=1, chunk_size=150, overlap=30)
print(f"Chunks: {len(chunks)}")
stats = ingest_chunks(chunks, dataset="urdu_A")
print(stats)
