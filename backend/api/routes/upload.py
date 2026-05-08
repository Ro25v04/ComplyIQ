import os
import uuid
import tempfile
import boto3
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from backend.database import save_document_r2_key
from backend.ingestion.parser import parse_document
from backend.ingestion.chunker import chunk_pages
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.indexer import index_chunks
from backend.ingestion.classifier import is_compliance_document

router = APIRouter()


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_bytes = file.file.read()
    suffix = os.path.splitext(file.filename)[1]

    # Save to temp file so parser can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # Store original file in R2
        r2_key = f"documents/{uuid.uuid4()}{suffix}"
        r2 = get_r2_client()
        r2.put_object(
            Bucket=settings.r2_bucket_name,
            Key=r2_key,
            Body=file_bytes,
            ContentType=file.content_type or "application/octet-stream",
        )

        # Run ingestion pipeline
        pages = parse_document(tmp_path)

        # Reject non-compliance documents before indexing
        if not is_compliance_document(pages[0].text):
            raise HTTPException(
                status_code=400,
                detail="This does not appear to be a compliance or legal document. Please upload contracts, policies, or legal agreements."
            )

        # Save R2 key mapping for later deletion
        save_document_r2_key(file.filename, r2_key)
        doc_id = r2_key.split("/")[1].split(".")[0]
        chunks = chunk_pages(pages, document_id=doc_id, source_document=file.filename)
        embedded = embed_chunks(chunks)
        inserted = index_chunks(embedded)

    finally:
        os.unlink(tmp_path)

    return {
        "filename": file.filename,
        "r2_key": r2_key,
        "chunks_indexed": inserted,
    }
