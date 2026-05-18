import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from backend.config import settings

# Must match the output dimension of all-MiniLM-L6-v2 in embedder.py.
# Changing the embedding model requires dropping and recreating the chunks table.
VECTOR_DIMENSION = 384


def get_connection():
    return psycopg2.connect(settings.database_url, cursor_factory=RealDictCursor)


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    id          SERIAL PRIMARY KEY,
                    chunk_id    TEXT UNIQUE NOT NULL,
                    document_id TEXT NOT NULL,
                    source_document TEXT NOT NULL,
                    page_number INTEGER,
                    content     TEXT NOT NULL,
                    embedding   vector({VECTOR_DIMENSION}),
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # HNSW is an approximate nearest-neighbour index; much faster than exact
            # ivfflat for query-time lookups but takes more memory at build time
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                ON chunks
                USING hnsw (embedding vector_cosine_ops);
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id              SERIAL PRIMARY KEY,
                    filename        TEXT UNIQUE NOT NULL,
                    r2_key          TEXT NOT NULL,
                    created_at      TIMESTAMPTZ DEFAULT NOW()
                );
            """)

    print("Database initialised - chunks table and HNSW index ready.")




def save_document_r2_key(filename: str, r2_key: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (filename, r2_key)
                VALUES (%s, %s)
                ON CONFLICT (filename) DO UPDATE SET r2_key = EXCLUDED.r2_key;
            """, (filename, r2_key))


def get_document_r2_key(filename: str) -> str | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT r2_key FROM documents WHERE filename = %s", (filename,))
            row = cur.fetchone()
            return row["r2_key"] if row else None


def delete_document_record(filename: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE filename = %s", (filename,))


def delete_document_chunks(filename: str) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chunks WHERE source_document = %s", (filename,))
            return cur.rowcount


if __name__ == "__main__":
    init_db()
