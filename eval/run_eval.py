"""
Run Ragas evaluation against 10 Acme Corp test questions.
1. Indexes a synthetic Acme Corp privacy policy if not already present.
2. Runs Faithfulness, AnswerRelevancy, ContextPrecision via Ragas.
3. Saves results to eval/results.json and prints a score table.
"""
import sys
import os
import json
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.config import settings
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from openai import OpenAI
from backend.retrieval.pipeline import retrieve
from backend.database import get_db
from backend.ingestion.chunker import TextChunk, chunk_pages
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.indexer import index_chunks
from backend.ingestion.parser import ParsedPage

DATASET_PATH = os.path.join(os.path.dirname(__file__), "test_dataset.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")
DOC_NAME = "acme_corp_privacy_policy.txt"

# ── Synthetic Acme Corp Privacy Policy ───────────────────────────────────────

ACME_POLICY = """
ACME CORP PRIVACY AND DATA COMPLIANCE POLICY
Version 3.1 | Effective Date: 1 January 2024

1. PURPOSE
This policy outlines how Acme Corp collects, uses, stores, and protects personal
information in accordance with the Privacy Act 1988 (Cth) and the Australian Privacy
Principles (APPs). It applies to all employees, contractors, and third-party vendors
who handle personal information on behalf of Acme Corp.

2. SCOPE
This policy applies to all employees, contractors, and third-party vendors who handle
personal information. Compliance is mandatory across all business units.

3. DATA RETENTION
3.1 Customer Records: All customer records must be retained for a minimum of 7 years
    from the date of last transaction, in accordance with applicable Australian law.
3.2 Employee Records: Employee records, including payroll and performance data, must be
    retained for 7 years from the date of termination or resignation.
3.3 Marketing Data: Marketing and campaign data, including customer interaction logs,
    must be retained for 2 years from the date of collection, after which it must be
    securely deleted or de-identified.

4. DATA BREACH NOTIFICATION
In the event of an eligible data breach as defined under the Notifiable Data Breaches
(NDB) scheme, Acme Corp must notify the Office of the Australian Information Commissioner
(OAIC) within 30 days of becoming aware of the breach. Affected individuals must also
be notified as soon as practicable. A breach response plan must be activated immediately
upon detection.

5. DATA SECURITY
5.1 Encryption: Acme Corp implements AES-256 encryption for all data at rest. All data
    in transit is protected using TLS 1.3.
5.2 Access Controls: Multi-factor authentication (MFA) is mandatory for all systems
    that process personal information.
5.3 Audits: Annual security audits are conducted by an independent third party to
    assess compliance with this policy and applicable legislation.
5.4 Security protocols implemented: AES-256 encryption, TLS 1.3, MFA, and annual audits.

6. THIRD PARTY DISCLOSURE
Personal information collected by Acme Corp will not be disclosed to third parties
without the explicit written consent of the individual, except where required by law,
court order, or regulatory authority. Any third-party vendor with access to personal
data must sign a Data Processing Agreement (DPA) with Acme Corp.

7. INDIVIDUAL RIGHTS
Individuals whose personal information is held by Acme Corp have the right to:
- Access their personal information upon written request.
- Correct inaccurate or out-of-date information.
- Request deletion of their information where legally permissible.

8. COMPLIANCE AND REVIEW
This policy is reviewed annually by the Compliance Officer and updated to reflect
changes in legislation, regulatory guidance, or business operations.

For questions regarding this policy, contact: privacy@acmecorp.com.au
"""

# ─────────────────────────────────────────────────────────────────────────────

def is_indexed() -> bool:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM chunks WHERE source_document = %s", (DOC_NAME,))
            row = cur.fetchone()
            return (row["count"] if isinstance(row, dict) else list(row.values())[0]) > 0


def index_acme_policy():
    print("Indexing Acme Corp privacy policy...")
    doc_id = str(uuid.uuid4())
    page = ParsedPage(page_number=1, text=ACME_POLICY.strip())
    chunks = chunk_pages([page], document_id=doc_id, source_document=DOC_NAME)
    embedded = embed_chunks(chunks)
    count = index_chunks(embedded)
    print(f"  Indexed {count} chunks.")


def generate_answer(query: str, chunks: list[dict]) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    context = "\n\n".join(c["content"] for c in chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a compliance assistant. Answer the question using only the provided context. Be concise and factual."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def build_dataset(test_cases: list[dict]) -> Dataset:
    questions, answers, contexts, ground_truths = [], [], [], []

    for i, case in enumerate(test_cases):
        q = case["question"]
        print(f"  [{i+1}/{len(test_cases)}] {q[:70]}...")
        chunks = retrieve(q)
        context_texts = [c["content"] for c in chunks]
        answer = generate_answer(q, chunks) if chunks else "No relevant context found."
        questions.append(q)
        answers.append(answer)
        contexts.append(context_texts)
        ground_truths.append(case["ground_truth"])

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })


def run():
    # Step 1 — ensure document is indexed
    if not is_indexed():
        index_acme_policy()
    else:
        print("Acme Corp policy already indexed, skipping.")

    # Step 2 — load test cases
    with open(DATASET_PATH) as f:
        test_cases = json.load(f)

    print(f"\nBuilding eval dataset for {len(test_cases)} questions...")
    dataset = build_dataset(test_cases)

    # Step 3 — run Ragas
    lc_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(api_key=settings.openai_api_key))
    lc_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", api_key=settings.openai_api_key, temperature=0))

    metrics = [
        Faithfulness(llm=lc_llm),
        AnswerRelevancy(llm=lc_llm, embeddings=lc_embeddings),
        ContextPrecision(llm=lc_llm),
    ]

    print("\nRunning Ragas evaluation (this takes ~2 min)...")
    results = evaluate(dataset=dataset, metrics=metrics)
    df = results.to_pandas()
    df.insert(0, "question", dataset["question"])

    # Step 4 — print table
    cols = ["faithfulness", "answer_relevancy", "context_precision"]
    print("\n" + "=" * 75)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 75)
    print(f"{'Question':<50} {'Faith':>6} {'Relev':>6} {'Prec':>6}")
    print("-" * 75)
    for _, row in df.iterrows():
        q = str(row["question"])[:48]
        f = f"{row['faithfulness']:.3f}" if row["faithfulness"] == row["faithfulness"] else " N/A"
        r = f"{row['answer_relevancy']:.3f}" if row["answer_relevancy"] == row["answer_relevancy"] else " N/A"
        p = f"{row['context_precision']:.3f}" if row["context_precision"] == row["context_precision"] else " N/A"
        print(f"{q:<50} {f:>6} {r:>6} {p:>6}")
    print("-" * 75)
    print(f"{'AVERAGE':<50} {df['faithfulness'].mean():>6.3f} {df['answer_relevancy'].mean():>6.3f} {df['context_precision'].mean():>6.3f}")
    print("=" * 75)

    # Step 5 — save to JSON
    per_question = []
    for _, row in df.iterrows():
        per_question.append({
            "question": row["question"],
            "faithfulness": round(float(row["faithfulness"]), 4) if row["faithfulness"] == row["faithfulness"] else None,
            "answer_relevancy": round(float(row["answer_relevancy"]), 4) if row["answer_relevancy"] == row["answer_relevancy"] else None,
            "context_precision": round(float(row["context_precision"]), 4) if row["context_precision"] == row["context_precision"] else None,
        })

    output = {
        "averages": {
            "faithfulness": round(float(df["faithfulness"].mean()), 4),
            "answer_relevancy": round(float(df["answer_relevancy"].mean()), 4),
            "context_precision": round(float(df["context_precision"].mean()), 4),
        },
        "per_question": per_question,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    run()