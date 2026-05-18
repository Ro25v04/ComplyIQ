from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.ingestion.parser import ParsedPage

# 512 tokens fits comfortably within all-MiniLM-L6-v2's 256-word effective window
# while staying large enough to hold a complete legal clause
CHUNK_SIZE = 512
# ~30% overlap so clause boundaries don't fall on a split edge and lose context
CHUNK_OVERLAP = 150


@dataclass
class TextChunk:
    chunk_id: str
    document_id: str
    source_document: str
    page_number: int
    content: str


def chunk_pages(pages: list[ParsedPage], document_id: str, source_document: str) -> list[TextChunk]:
    # Separator order matters: try paragraph breaks before sentence breaks before
    # word breaks so splits land at natural boundaries when possible
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