import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.retrieval.pipeline import retrieve
from backend.llm.generator import generate_report

TEST_QUERIES = [
    "What is the data retention policy and are we compliant?",
    "What security measures are in place?",
    "What are the data breach notification requirements?",
]


def test_generator():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)

        chunks = retrieve(query)
        report = generate_report(query, chunks)

        print(json.dumps(report, indent=2))
        print("=" * 60)


if __name__ == "__main__":
    test_generator()
