from langchain_core.tools import tool
from backend.llm.generator import get_client

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an Australian compliance query specialist.
Rewrite the user's vague question into a precise, technical compliance query.
Use correct Australian regulatory terminology (Privacy Act 1988, APP, NDB, OAIC, Fair Work Act 2009, etc.).
Return ONLY the rewritten query — no explanation, no preamble."""


@tool
def query_reformulator(query: str) -> str:
    """Rewrite a vague or unclear compliance question into a precise, technical query
    using correct Australian regulatory terminology.
    Use this tool FIRST when the user's question is ambiguous or uses
    plain language instead of legal or regulatory terms."""
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Rewrite this query: {query}"},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()