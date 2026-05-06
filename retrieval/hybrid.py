"""
Hybrid Retrieval via Reciprocal Rank Fusion (RRF)
Merges FAISS (dense) and BM25 (sparse) result lists into a single
ranked list using the RRF formula:
    RRF(d) = Σ  1 / (k + rank(d))    where k = 60
"""

import logging
from collections import defaultdict

from config.config import RAG_MODES

logger = logging.getLogger(__name__)

RRF_K     = 60    # standard constant from the original RRF paper
MIN_SCORE = 0.01  # ← drop weak matches below this RRF score threshold

def reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    mode: str = "short",
    genre: str | None = None,
) -> list[dict]:
    """
    Merge multiple ranked result lists using RRF.

    Args:
        result_lists: Each list is a ranked list of chunk dicts.
                      Each dict must have a "chunk_id" key and a "rank" key.
        top_n:        How many fused results to return.

    Returns:
        Sorted list of chunk dicts with added "rrf_score" key.
    """

    config = RAG_MODES.get(mode, RAG_MODES["short"])

    top_n = config.get("TOP_K", 5) * 5   # expand pool before final cut
    min_score = MIN_SCORE

    # Genre filter: discard chunks that don't match the requested genre
    # before scoring so non-matching chunks never influence RRF ranks.
    if genre is not None:
        result_lists = [
            [item for item in rl if item.get("dataset") != "urdu_B" or item.get("genre") == genre
            for rl in result_lists
            ]

    rrf_scores:  dict[str, float] = defaultdict(float)
    chunks_by_id: dict[str, dict] = {}

    for result_list in result_lists:
        for item in result_list:
            cid  = item["chunk_id"]
            rank = item.get("rank", 0)
            rrf_scores[cid]  += 1.0 / (RRF_K + rank + 1)
            chunks_by_id[cid] = item

    # Sort by descending RRF score
    sorted_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)

    fused: list[dict] = []
    for new_rank, cid in enumerate(sorted_ids[:top_n]):
        score = rrf_scores[cid]

        # ← Filter out weak/irrelevant chunks
        if score < min_score:
            logger.debug(f"Chunk {cid} dropped — rrf_score {score:.4f} < min_score {min_score}")
            continue

        chunk = chunks_by_id[cid].copy()
        chunk["rrf_score"]  = score
        chunk["fused_rank"] = new_rank
        fused.append(chunk)

    logger.info(
        f"RRF fusion: {sum(len(r) for r in result_lists)} candidates → {len(fused)} fused"
    )
    return fused