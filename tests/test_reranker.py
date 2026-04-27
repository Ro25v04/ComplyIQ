import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.retrieval.vector_search import vector_search
from backend.retrieval.bm25_search import bm25_search
from backend.retrieval.rrf import reciprocal_rank_fusion
from backend.retrieval.reranker import rerank

TEST_QUERIES = [
    "What is our data breach notification policy?",
    "How long do we retain customer records?",
    "What security measures are in place?",
]


def test_reranker():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)

        vector_results = vector_search(query)
        bm25_results = bm25_search(query)
        fused = reciprocal_rank_fusion(vector_results, bm25_results)
        final = rerank(query, fused)

        print(f"Top {len(final)} chunks after reranking:")
        for i, r in enumerate(final, start=1):
            print(f"  [{i}] rerank_score: {r['rerank_score']:.4f} | page {r['page_number']} | {r['content'][:60]}...")


if __name__ == "__main__":
    test_reranker()
