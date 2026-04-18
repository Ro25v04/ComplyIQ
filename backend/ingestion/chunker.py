from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.ingestion.parser import ParsedPage

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


@dataclass
class TextChunk:
    chunk_id: str
    document_id: str
    source_document: str
    page_number: int
    content: str


def chunk_pages(pages: list[ParsedPage], document_id: str, source_document: str) -> list[TextChunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for page in pages:
        splits = splitter.split_text(page.text)
        for i, split in enumerate(splits):
            chunk_id = f"{document_id}_p{page.page_number}_c{i}"
            chunks.append(TextChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                source_document=source_document,
                page_number=page.page_number,
                content=split,
            ))

    return chunks