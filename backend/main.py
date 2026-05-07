from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import upload, query, documents, delete

app = FastAPI(title="ComplyIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(query.router)
app.include_router(documents.router)
app.include_router(delete.router)


@app.get("/health")
def health():
    return {"status": "ok"}
