import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.retrieval.vector_search import vector_search
from backend.retrieval.bm25_search import bm25_search
from backend.retrieval.rrf import reciprocal_rank_fusion

TEST_QUERIES = [
    "What is our data breach notification policy?",
    "How long do we retain customer records?",
    "What security measures are in place?",
]

def test_rrf():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)

        vector_results = vector_search(query)
        bm25_results = bm25_search(query)
        fused = reciprocal_rank_fusion(vector_results, bm25_results)

        print(f"Results after RRF: {len(fused)}")
        for i, r in enumerate(fused, start=1):
            print(f"  [{i}] rrf_score: {r['rrf_score']:.4f} | page {r['page_number']} | {r['content'][:60]}...")

if __name__ == "__main__":
    test_rrf()
