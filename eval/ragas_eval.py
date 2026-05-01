import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.config import settings
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from backend.retrieval.pipeline import retrieve
from backend.llm.generator import _format_chunks
from backend.llm.prompts import COMPLIANCE_SYSTEM_PROMPT

DATASET_PATH = os.path.join(os.path.dirname(__file__), "test_dataset.json")

_openai_client = OpenAI(api_key=settings.openai_api_key)


def generate_report(query: str, chunks: list[dict]) -> dict:
    context = _format_chunks(chunks)
    user_message = (
        f"COMPLIANCE QUESTION:\n{query}\n\n"
        f"CONTEXT CHUNKS:\n{context}\n\n"
        f"Analyse the question using only the provided context and return a JSON compliance report."
    )
    response = _openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": COMPLIANCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def build_eval_dataset() -> Dataset:
    with open(DATASET_PATH) as f:
        test_cases = json.load(f)

    questions, answers, contexts, ground_truths = [], [], [], []

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

    lc_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(api_key=settings.openai_api_key))
    metrics = [
        Faithfulness(),
        AnswerRelevancy(embeddings=lc_embeddings),
        ContextPrecision(),
    ]

    print("\nRunning Ragas evaluation...")
    results = evaluate(dataset=dataset, metrics=metrics)

    df = results.to_pandas()
    df["question"] = dataset["question"]

    print("\n" + "="*50)
    print("RAGAS EVALUATION RESULTS")
    print("="*50)
    print(f"Faithfulness:      {df['faithfulness'].mean():.3f}")
    print(f"Answer Relevancy:  {df['answer_relevancy'].mean():.3f}")
    print(f"Context Precision: {df['context_precision'].mean():.3f}")
    print("="*50)
    print("\nPer-question scores:")
    print(df[["question", "faithfulness", "answer_relevancy", "context_precision"]].to_string(index=False))

    return results


if __name__ == "__main__":
    run_evaluation()
