# Generates structured compliance report using Groq/Llama3

import json
from groq import Groq
from backend.config import settings
from backend.llm.prompts import COMPLIANCE_SYSTEM_PROMPT

MODEL = "llama-3.3-70b-versatile"

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def _format_chunks(chunks: list[dict]) -> str:
    formatted = []
    for i, chunk in enumerate(chunks, start=1):
        formatted.append(
            f"[Chunk {i}]\n"
            f"Source: {chunk['source_document']} p.{chunk['page_number']}\n"
            f"Content: {chunk['content']}\n"
        )
    return "\n".join(formatted)


def generate_report(query: str, chunks: list[dict]) -> dict:
    client = get_client()

    context = _format_chunks(chunks)

    user_message = f"""
COMPLIANCE QUESTION:
{query}

CONTEXT CHUNKS:
{context}

Analyse the question using only the provided context and return a JSON compliance report.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": COMPLIANCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    return json.loads(raw)
