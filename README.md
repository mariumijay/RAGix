# Urdu RAG System (Urdu A & Urdu B Version)

## Overview

The Urdu RAG System is a Retrieval-Augmented Generation solution built for Urdu-language data. It integrates OCR ingestion, text preprocessing, embedding generation, multi-strategy retrieval, reranking, and LLM-based answer generation. The repository supports two parallel Urdu pipelines: **Urdu A** and **Urdu B**.

This system is designed to improve the quality of Urdu retrieval and generation by combining rule-based retrieval, semantic embedding search, and specialized prompt handling for both datasets.

## Problem Statement

Urdu OCR and retrieval face specific challenges:

- OCR output quality varies greatly across Urdu exam papers and scanned documents.
- Urdu is a low-resource language for many NLP pipelines compared to English.
- Text normalization, noisy character encoding, and inconsistent layout make retrieval difficult.
- Effective answers require a retrieval layer that can find relevant content from noisy Urdu data and a generation layer that can formulate responses reliably.

## System Architecture

The Urdu RAG System is structured into the following stages:

1. **Ingestion**
   - OCR ingestion of Urdu exam data.
   - Data cleaning and segmentation into smaller text chunks.
2. **Preprocessing**
   - Remove noise introduced by OCR.
   - Normalize Urdu text and prepare it for embedding.
3. **Embedding Generation**
   - Create vector representations for text chunks.
   - Store embeddings for both Urdu A and Urdu B datasets.
4. **Retrieval**
   - Use BM25 for lexical matching.
   - Use FAISS for semantic vector search.
   - Hybrid retrieval merges both approaches to maximize recall and precision.
5. **Reranking**
   - Refine retrieved candidate passages.
   - Prioritize the most contextually relevant Urdu content before generation.
6. **LLM Generation**
   - Feed reranked Urdu context into a language model.
   - Generate answers aligned with the query and retrieved documents.

### Data Flow

1. OCR input is collected from Urdu exam/paper images.
2. Text is cleaned and normalized.
3. Clean text is chunked into retrieval-ready passages.
4. Embeddings are generated and stored.
5. A query is normalized and routed through retrieval engines.
6. Retrieved passages are reranked and passed to the generator.
7. The final answer is produced by the LLM.

## Modules Explanation

### `ingestion/`

Handles the ingestion and preparation of Urdu text data.

- `cleaner.py` — cleans OCR output and normalizes Urdu text.
- `chunker.py` — splits long passages into fixed-size chunks for retrieval.
- `embedder.py` — generates embeddings for chunks and stores them.
- `ingest_b.py` — specialized ingestion logic for the Urdu B dataset.

### `retrieval/`

Contains retrieval logic and search orchestration.

- `bm25_retriever.py` — lexical retrieval using BM25 scoring.
- `faiss_retriever.py` — vector search using FAISS index.
- `hybrid.py` — combines BM25 and FAISS results for stronger retrieval.
- `reranker.py` — reranks candidate passages for relevance.
- `router.py` — decides which retrieval pipeline to use.
- `query_normalizer.py` — normalizes incoming queries for Urdu handling.
- `embedder.py` — generates query embeddings for semantic search.

### `generation/`

Manages generation logic and prompt construction.

- `llm.py` — the interface to the language model used for answer generation.
- `prompt.py` — prompt templates and instructions for Urdu A.
- `prompt_b.py` — prompt templates and instructions for Urdu B.

### `models/`

Defines structured data objects for the system.

- `schemas.py` — data models and schema definitions for ingestion, retrieval, and generation.

## Pipeline Workflow

The Urdu RAG pipeline follows these steps:

1. **OCR**
   - Capture Urdu text from scanned exam papers and images.
2. **Clean**
   - Remove noise, invalid symbols, and OCR artifacts.
3. **Chunk**
   - Divide text into smaller retrieval-friendly segments.
4. **Embed**
   - Generate semantic embeddings for each chunk.
5. **Store**
   - Save embeddings and metadata for retrieval.
6. **Retrieve**
   - Fetch candidates using BM25, FAISS, or hybrid retrieval.
7. **Rerank**
   - Sort candidates by relevance.
8. **Generate Answer**
   - Build prompts and generate the final Urdu response.

## Urdu A vs Urdu B System Design

This project supports two separate Urdu pipelines with distinct handling strategies:

- **Urdu A**
  - Standard ingestion and generation flow.
  - Uses `prompt.py` and general retrieval logic.
  - Suited for the primary Urdu dataset and classic exam content.

- **Urdu B**
  - Specialized ingestion and prompt handling.
  - Uses `ingestion/ingest_b.py` and `generation/prompt_b.py`.
  - Designed to process a second Urdu dataset with different formatting and task characteristics.

### Key differences

- Prompt templates differ between Urdu A and Urdu B to better match dataset semantics.
- Data ingestion and chunking may vary based on text layout and OCR output style.
- Queries are routed to the appropriate pipeline depending on dataset selection.

## Technologies Used

- Python
- FAISS for vector-based semantic retrieval
- BM25 for lexical matching
- OCR data ingestion pipeline
- LLM generation interface
- Modular pipeline architecture for ingestion, retrieval, and generation

## Key Features

- Hybrid retrieval with BM25 + FAISS
- Support for Urdu OCR data
- Dual pipeline design for Urdu A and Urdu B
- Modular architecture with clear separation of ingestion, retrieval, and generation
- Reranking layer for improved answer relevance
- Structured schemas for consistent data handling

## How to Run the Project

### Setup

1. Clone the repository.
2. Create a Python virtual environment.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Run

Use the main entry point:

```bash
python main.py
```

If your pipeline requires OCR ingestion first, run:

```bash
python ingest_ocr.py
```

### Notes

- Confirm that your Urdu dataset files are available and correctly referenced.
- Ensure any required model keys or environment variables are configured before running.

## Future Improvements

Possible enhancements for the Urdu RAG System include:

- Improve OCR accuracy and Urdu text normalization
- Fine-tune embeddings specifically for Urdu passages
- Add evaluation metrics for retrieval and generation quality
- Deploy the pipeline as an API using FastAPI or a user interface with Streamlit
- Add dataset versioning and more robust pipeline monitoring

## Conclusion

The Urdu RAG System is a modular Retrieval-Augmented Generation architecture built for Urdu data. It combines OCR handling, preprocessing, semantic embeddings, hybrid retrieval, reranking, and LLM generation. The dual Urdu A and Urdu B pipelines allow flexible handling of different dataset formats and query patterns, making the system suitable for Urdu exam content and low-resource language retrieval tasks.