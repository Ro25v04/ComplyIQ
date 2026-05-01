from langchain_core.tools import tool
from backend.retrieval.pipeline import retrieve


@tool
def static_retriever(query: str) -> str:
    """Search the uploaded compliance documents stored in the database.
    Use this tool when the question is about what the organisation's
    internal policies, procedures, or uploaded documents say.
    Input should be a clear compliance question or keyword."""
    chunks = retrieve(query)
    if not chunks:
        return "No relevant chunks found in the uploaded documents."

    lines = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(
            f"[{i}] Source: {chunk['source_document']} p.{chunk['page_number']}\n"
            f"    {chunk['content'][:300]}"
        )
    return "\n\n".join(lines)