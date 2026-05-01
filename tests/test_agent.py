import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.agent.react_agent import run_agent

TEST_QUERIES = [
    "Are we compliant with the Privacy Act 1988 data breach notification requirements?",
    "What are the data retention gaps in our policy?",
    "Do we meet the Australian Privacy Principles for handling personal information?",
]


def test_agent():
    for query in TEST_QUERIES:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        result = run_agent(query)
        print(f"\nFinal Answer:\n{result}")
        print('='*60)


if __name__ == "__main__":
    test_agent()