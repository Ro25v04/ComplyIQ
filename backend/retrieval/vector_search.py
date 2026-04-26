from backend.database import get_db
from backend.ingestion.embedder import embed_query

TOP_K = 20

def vector_search(query: str) -> list[dict]:
    query_embedding = embed_query(query)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    chunk_id,
                    document_id,
                    source_document,
                    page_number,
                    content,
                    1 - (embedding <=> %s::vector) AS score
                FROM chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, query_embedding, TOP_K))

            results = cur.fetchall()

    return [dict(row) for row in results]

