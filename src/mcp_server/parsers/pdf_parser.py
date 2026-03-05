from pathlib import Path

from pypdf import PdfReader


def parse(path: Path, max_pages: int | None = None) -> str:
    """Parse PDF files and extract text content."""
    reader = PdfReader(str(path))
    pages = reader.pages
    if max_pages is not None:
        pages = pages[:max_pages]

    parts: list[str] = []
    for i, page in enumerate(pages, 1):
        text = page.extract_text() or ""
        if text.strip():
            parts.append(f"--- Page {i} ---\n{text.strip()}")

    if not parts:
        return "(No text content could be extracted from this PDF)"

    return "\n\n".join(parts)
