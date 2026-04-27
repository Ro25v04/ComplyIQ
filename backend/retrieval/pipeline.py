# Orchestrates the full retrieval pipeline: vector search + BM25 + RRF + Cohere rerank

from backend.retrieval.vector_search import vector_search
from backend.retrieval.bm25_search import bm25_search
from backend.retrieval.rrf import reciprocal_rank_fusion
from backend.retrieval.reranker import rerank
from backend.security.presidio import anonymise


def retrieve(query: str) -> list[dict]:
    # Strip PII from query before hitting any external API
    query = anonymise(query)

    # Step 1 — parallel semantic and keyword search
    vector_results = vector_search(query)
    bm25_results = bm25_search(query)

    # Step 2 — merge both results with RRF
    fused = reciprocal_rank_fusion(vector_results, bm25_results)

    # Step 3 — rerank with Cohere, return top 6
    final = rerank(query, fused)

    return final
