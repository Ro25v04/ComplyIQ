import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.agent.tools.static_retriever import retriever

TEST_QUERIES = [
    "What is the data retention policy?",
    "What are the data breach notification requirements?",
    "What security measures are in place?",
]


def test_static_retriever():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)
        result = retriever(query)
        print(result)
        print("=" * 60)


if __name__ == "__main__":
    test_static_retriever()
