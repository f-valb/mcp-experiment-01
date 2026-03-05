# mcp-experiment-01

A Python MCP (Model Context Protocol) server that provides two tools to AI agents:

1. **`browse_web`** — Browse the internet using a headless Playwright browser
2. **`read_document`** — Read local documents with automatic PII/sensitive data filtering

## Features

### Web Browsing
- Navigate directly to URLs or perform Google searches
- Clean text extraction (strips scripts, styles, nav, etc.)
- Optional link extraction
- Custom CSS selector waiting

### Secure Document Reading
- Supports: `.txt`, `.md`, `.csv`, `.json`, `.log`, `.xml`, `.yaml`, `.pdf`, `.docx`, `.xlsx`, `.pptx`
- **PII detection** — files containing sensitive data are excluded automatically:
  - Email addresses, phone numbers, SSNs
  - Credit card numbers (Luhn-validated)
  - API keys, AWS credentials, GitHub/Slack tokens
  - Passwords, bearer tokens, private keys
- **Path restriction** — only reads from configured allowed directories
- Symlink/traversal attack prevention

## Setup

```bash
# Create virtual environment and install
uv venv && source .venv/bin/activate
uv pip install -e .

# Install Playwright browser
playwright install chromium
```

## Configuration

Edit `config.yaml` to set allowed directories and limits:

```yaml
allowed_directories:
  - ~/Documents
  - ~/Desktop

max_file_size_mb: 50
max_content_chars: 100000
browser_timeout_ms: 30000
```

Override with environment variables:
- `MCP_ALLOWED_DIRS` — comma-separated list of allowed directories
- `MCP_CONFIG_PATH` — path to config file

## Usage

### With Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-experiment-01": {
      "command": "/path/to/mcp-experiment-01/.venv/bin/python",
      "args": ["-m", "mcp_server.main"]
    }
  }
}
```

### With MCP Inspector

```bash
source .venv/bin/activate
mcp dev src/mcp_server/main.py
```

## Project Structure

```
src/mcp_server/
├── server.py              # FastMCP instance + Playwright lifecycle
├── main.py                # Entry point
├── config.py              # Configuration loading
├── tools/
│   ├── web_browser.py     # browse_web tool
│   └── document_reader.py # read_document tool
├── parsers/               # File format parsers
│   ├── text_parser.py     # .txt, .md, .csv, .json, .log, .xml, .yaml
│   ├── pdf_parser.py      # .pdf
│   ├── docx_parser.py     # .docx
│   ├── xlsx_parser.py     # .xlsx
│   └── pptx_parser.py     # .pptx
└── security/
    ├── pii_detector.py    # PII/secret regex scanning
    └── path_validator.py  # Directory allowlist enforcement
```
