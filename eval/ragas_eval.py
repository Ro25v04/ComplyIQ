import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from backend.retrieval.pipeline import retrieve
from backend.llm.generator import generate_report

DATASET_PATH = os.path.join(os.path.dirname(__file__), "test_dataset.json")


def build_eval_dataset() -> Dataset:
    with open(DATASET_PATH) as f:
        test_cases = json.load(f)

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for i, case in enumerate(test_cases):
        question = case["question"]
        ground_truth = case["ground_truth"]

        print(f"\n[{i+1}/{len(test_cases)}] Running: {question[:60]}...")

        chunks = retrieve(question)
        context_texts = [chunk["content"] for chunk in chunks]

        report = generate_report(question, chunks)
        answer = report.get("summary", "") + " " + " ".join(report.get("recommendations", []))

        questions.append(question)
        answers.append(answer)
        contexts.append(context_texts)
        ground_truths.append(ground_truth)

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })


def run_evaluation():
    print("Building evaluation dataset...")
    dataset = build_eval_dataset()

    print("\nRunning Ragas evaluation...")
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
        ],
    )

    print("\n" + "="*50)
    print("RAGAS EVALUATION RESULTS")
    print("="*50)
    print(f"Faithfulness:      {results['faithfulness']:.3f}")
    print(f"Answer Relevancy:  {results['answer_relevancy']:.3f}")
    print(f"Context Precision: {results['context_precision']:.3f}")
    print("="*50)

    return results


if __name__ == "__main__":
    run_evaluation()
