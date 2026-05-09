from dotenv import load_dotenv
load_dotenv()

from retrieval.faiss_retriever import FAISSRetriever
from retrieval.bm25_retriever import BM25Retriever
from retrieval.hybrid import reciprocal_rank_fusion
from retrieval.reranker import rerank
from generation.llm import generate_answer
import asyncio

faiss_r = FAISSRetriever('urdu_A'); faiss_r.load()
bm25_r  = BM25Retriever('urdu_A');  bm25_r.load()

query = 'محبت کا مطلب کیا ہے'
fused = reciprocal_rank_fusion([
    faiss_r.search(query, top_k=5),
    bm25_r.search(query,  top_k=5),
])
chunks = rerank(query, fused, top_k=1)  # only 1 chunk
chunks[0]['text'] = ' '.join(chunks[0]['text'].split()[:100])  # 100 words max

result = asyncio.run(generate_answer(query, chunks))
print(result['answer'])