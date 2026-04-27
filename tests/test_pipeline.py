import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.retrieval.pipeline import retrieve

TEST_QUERIES = [
    "What is our data breach notification policy?",
    "How long do we retain customer records?",
    "What security measures are in place?",
]


def test_pipeline():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)

        results = retrieve(query)

        print(f"Top {len(results)} chunks:")
        for i, r in enumerate(results, start=1):
            print(f"  [{i}] rerank_score: {r['rerank_score']:.4f} | page {r['page_number']} | {r['content'][:60]}...")


if __name__ == "__main__":
    test_pipeline()
