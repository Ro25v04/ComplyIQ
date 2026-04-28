import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.agent.tools.query_reformulator import reformulate

TEST_QUERIES = [
    "are we ok with privacy stuff?",
    "what about the breach thing?",
    "is our data handling fine?",
    "do we need to tell people about their data?",
    "are we following the rules for employees?",
]


def test_query_reformulator():
    for query in TEST_QUERIES:
        print(f"\nOriginal:     {query}")
        reformulated = reformulate(query)
        print(f"Reformulated: {reformulated}")
        print("-" * 60)


if __name__ == "__main__":
    test_query_reformulator()
