# To connect to the postgres database

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from backend.config import settings

# all-MiniLM-L6-v2 produces 384-dimensional vectors
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

            cur.execute("""
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                ON chunks
                USING hnsw (embedding vector_cosine_ops);
            """)

    print("Database initialised - chunks table and HNSW index ready.")


if __name__ == "__main__":
    init_db()
