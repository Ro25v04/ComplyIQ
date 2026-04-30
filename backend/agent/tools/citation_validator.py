from langchain_core.tools import Tool
from backend.database import get_db


def validate_citation(citation: str) -> str:
    citation_lower = citation.lower()

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source_document, page_number, content
                FROM chunks
                WHERE LOWER(source_document) LIKE %s
                   OR LOWER(content) LIKE %s
                LIMIT 3;
            """, (f"%{citation_lower}%", f"%{citation_lower}%"))
            rows = cur.fetchall()

    if not rows:
        return f"Citation not found in database: '{citation}'. This citation could not be verified - treat as unconfirmed."

    results = [f"Citation verified in database:"]
    for row in rows:
        results.append(
            f"  Source: {row['source_document']} p.{row['page_number']}\n"
            f"  Text: {row['content'][:200]}"
        )

    return "\n".join(results)


citation_validator_tool = Tool(
    name="citation_validator",
    func=validate_citation,
    description=(
        "Validate whether a citation exists in the uploaded compliance documents. "
        "Use this tool to fact-check a source before including it in a compliance report. "
        "Input should be a document name, page number, or key phrase from the citation. "
        "Returns the matching text if found, or flags it as unverified if not found."
    ),
)