from fastapi import APIRouter
from backend.database import get_db

router = APIRouter()


@router.get("/documents")
def list_documents():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source_document, COUNT(*) as chunk_count
                FROM chunks
                GROUP BY source_document
                ORDER BY source_document;
            """)
            rows = cur.fetchall()

    return [
        {"filename": row["source_document"], "chunks": row["chunk_count"]}
        for row in rows
    ]
