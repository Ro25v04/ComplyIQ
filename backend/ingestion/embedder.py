# Converting chunks into embeddings

from sentence_transformers import SentenceTransformer
from backend.ingestion.chunker import TextChunk

MODEL_NAME = "all-MiniLM-L6-v2"

# Load once at module level so it's not reloaded on every request
_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_chunks(chunks: list[TextChunk]) -> list[tuple[TextChunk, list[float]]]:
    model = get_model()
    texts = [chunk.content for chunk in chunks]
    embeddings = model.encode(
        texts, show_progress_bar=True, convert_to_numpy=True)
    return list(zip(chunks, embeddings.tolist()))


def embed_query(query: str) -> list[float]:
    model = get_model()
    return model.encode(query, convert_to_numpy=True).tolist()
