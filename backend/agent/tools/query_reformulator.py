from langchain_core.tools import Tool
from backend.llm.generator import get_client

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an Australian compliance query specialist.
Rewrite the user's vague question into a precise, technical compliance query.
Use correct Australian regulatory terminology (Privacy Act 1988, APP, NDB, OAIC, Fair Work Act 2009, etc.).
Return ONLY the rewritten query — no explanation, no preamble."""


def reformulate(query: str) -> str:
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


query_reformulator_tool = Tool(
    name="query_reformulator",
    func=reformulate,
    description=(
        "Rewrite a vague or unclear compliance question into a precise, "
        "technical query using correct Australian regulatory terminology. "
        "Use this tool FIRST when the user's question is ambiguous or uses "
        "plain language instead of legal/regulatory terms."
    ),
)
