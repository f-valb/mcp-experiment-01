from pathlib import Path

from mcp_server.config import load_config
from mcp_server.parsers import SUPPORTED_EXTENSIONS, parse_file
from mcp_server.security.path_validator import validate_path
from mcp_server.security.pii_detector import scan_for_pii
from mcp_server.server import mcp


@mcp.tool()
async def read_document(file_path: str, max_pages: int | None = None) -> str:
    """Read a local document file. Supported formats: .txt, .md, .csv,
    .json, .log, .xml, .yaml, .pdf, .docx, .xlsx, .pptx.

    Files containing PII or sensitive data (emails, SSNs, credit cards,
    passwords, API keys) will be excluded and not returned.

    Args:
        file_path: Absolute path to the document to read.
        max_pages: For PDF/PPTX/XLSX, limit to this many pages/slides/sheets.
    """
    config = load_config()

    # Validate path is within allowed directories
    resolved = validate_path(file_path, config.allowed_directories)
    if resolved is None:
        return (
            f"Error: '{file_path}' is either outside allowed directories, "
            f"does not exist, or is not a regular file."
        )

    # Check file extension
    ext = resolved.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return (
            f"Error: Unsupported file type '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Check file size
    size_mb = resolved.stat().st_size / (1024 * 1024)
    if size_mb > config.max_file_size_mb:
        return (
            f"Error: File is {size_mb:.1f} MB, exceeds the "
            f"{config.max_file_size_mb} MB limit."
        )

    # Parse file content
    try:
        content = parse_file(resolved, max_pages=max_pages)
    except Exception as e:
        return f"Error parsing '{file_path}': {e}"

    # Scan for PII
    pii_findings = scan_for_pii(content)
    if pii_findings:
        categories = ", ".join(sorted(pii_findings.keys()))
        return (
            f"EXCLUDED: File '{file_path}' contains sensitive data "
            f"and cannot be returned.\nDetected: {categories}."
        )

    # Truncate if too long
    if len(content) > config.max_content_chars:
        content = (
            content[: config.max_content_chars]
            + f"\n\n... (truncated at {config.max_content_chars:,} characters)"
        )

    return content
