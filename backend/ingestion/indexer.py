from backend.database import get_db
from backend.ingestion.chunker import TextChunk
from backend.security.presidio import anonymise


def index_chunks(embedded_chunks: list[tuple[TextChunk, list[float]]]) -> int:
    inserted = 0

    with get_db() as conn:
        with conn.cursor() as cur:
            for chunk, embedding in embedded_chunks:
                # anonymise PII before storing in PostgreSQL
                safe_content = anonymise(chunk.content)

                cur.execute("""
                    INSERT INTO chunks (chunk_id, document_id, source_document, page_number, content, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO NOTHING;
                """, (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.source_document,
                    chunk.page_number,
                    safe_content,
                    embedding,
                ))
                inserted += cur.rowcount

    return inserted