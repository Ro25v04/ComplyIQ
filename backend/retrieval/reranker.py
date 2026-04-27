# Reranks RRF results using Cohere cross-encoder model

import cohere
from backend.config import settings

TOP_K = 6
RERANK_MODEL = "rerank-english-v3.0"

# Load Cohere client once
_client = None


def get_client() -> cohere.Client:
    global _client
    if _client is None:
        _client = cohere.Client(settings.cohere_api_key)
    return _client


def rerank(query: str, chunks: list[dict]) -> list[dict]:
    if not chunks:
        return []

    client = get_client()

    # Extract just the text content from each chunk to send to Cohere
    documents = [chunk["content"] for chunk in chunks]

    # Send query + all documents to Cohere rerank API
    response = client.rerank(
        model=RERANK_MODEL,
        query=query,
        documents=documents,
        top_n=TOP_K,
    )

    # Use the returned indices to pick the top 6 chunks in the new order
    reranked = []
    for result in response.results:
        chunk = chunks[result.index]
        chunk["rerank_score"] = result.relevance_score
        reranked.append(chunk)

    return reranked
