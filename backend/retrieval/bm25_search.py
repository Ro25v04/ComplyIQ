# Keyword search using BM25

from rank_bm25 import BM25Okapi
from backend.database import get_db
import numpy as np

TOP_K = 20


def bm25_search(query: str) -> list[dict]:
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT chunk_id, document_id, source_document, page_number, content
                FROM chunks;
            """)
            all_chunks = [dict(row) for row in cur.fetchall()]

    if not all_chunks:
        return []

    tokenized_chunks = [chunk["content"].lower().split() for chunk in all_chunks]

    bm25 = BM25Okapi(tokenized_chunks)

    # Calculates TF and IDF across all chunks
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    # Get top 20 indices 
    top_indices = np.argsort(scores)[::-1][:TOP_K]

    results = []
    for i in top_indices:
        chunk = all_chunks[i]
        chunk["score"] = float(scores[i])
        results.append(chunk)

    return results
