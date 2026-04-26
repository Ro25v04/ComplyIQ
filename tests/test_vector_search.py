import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.retrieval.vector_search import vector_search

TEST_QUERIES = [
    "What is our data breach notification policy?",
    "How long do we retain customer records?",
    "What security measures are in place?",
]

def test_vector_search():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)

        results = vector_search(query)

        print(f"Results found: {len(results)}")
        for i, r in enumerate(results, start=1):
            print(f"  [{i}] score: {r['score']:.3f} | page {r['page_number']} | {r['source_document']}")
            print(f"       {r['content'][:80].strip()}...")

if __name__ == "__main__":
    test_vector_search()
