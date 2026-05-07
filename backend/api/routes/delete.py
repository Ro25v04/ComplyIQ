import boto3
from fastapi import APIRouter, HTTPException
from backend.config import settings
from backend.database import delete_document_chunks

router = APIRouter()


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


@router.delete("/documents/{filename}")
def delete_document(filename: str):
    # Delete chunks from PostgreSQL
    deleted = delete_document_chunks(filename)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from R2 by listing and matching filename
    try:
        r2 = get_r2_client()
        response = r2.list_objects_v2(Bucket=settings.r2_bucket_name, Prefix="documents/")
        objects = response.get("Contents", [])
        for obj in objects:
            if obj["Key"].endswith(filename) or filename in obj["Key"]:
                r2.delete_object(Bucket=settings.r2_bucket_name, Key=obj["Key"])
                break
    except Exception:
        pass

    return {"deleted": filename, "chunks_removed": deleted}