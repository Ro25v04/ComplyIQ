# Document parser to parse pdf and docs

import pymupdf
import docx
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ParsedPage:
    page_number: int
    text: str


def parse_pdf(file_path: str) -> list[ParsedPage]:
    pages = []
    with pymupdf.open(file_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()  # Extract raw text and remove whitespaces
            if text:
                pages.append(ParsedPage(page_number=i, text=text))
    return pages


def parse_docx(file_path: str) -> list[ParsedPage]:
    doc = docx.Document(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [ParsedPage(page_number=1, text=full_text)]


def parse_document(file_path: str) -> list[ParsedPage]:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix in (".docx", ".doc"):
        return parse_docx(file_path)
    else:
        # reject any other file type
        raise ValueError(f"Unsupported file type: {suffix}")
