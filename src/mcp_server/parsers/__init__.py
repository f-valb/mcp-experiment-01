import importlib
from pathlib import Path

EXTENSION_MAP = {
    ".txt": "text_parser",
    ".md": "text_parser",
    ".log": "text_parser",
    ".csv": "text_parser",
    ".json": "text_parser",
    ".xml": "text_parser",
    ".yaml": "text_parser",
    ".yml": "text_parser",
    ".pdf": "pdf_parser",
    ".docx": "docx_parser",
    ".xlsx": "xlsx_parser",
    ".pptx": "pptx_parser",
}

SUPPORTED_EXTENSIONS = set(EXTENSION_MAP.keys())


def parse_file(path: Path, max_pages: int | None = None) -> str:
    ext = path.suffix.lower()
    if ext not in EXTENSION_MAP:
        raise ValueError(f"Unsupported file type: {ext}")

    module = importlib.import_module(f"mcp_server.parsers.{EXTENSION_MAP[ext]}")
    return module.parse(path, max_pages=max_pages)
