import json
from pathlib import Path

import yaml


def parse(path: Path, max_pages: int | None = None) -> str:
    """Parse plain text files (.txt, .md, .csv, .log, .json, .xml, .yaml)."""
    ext = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")

    if ext == ".json":
        try:
            data = json.loads(text)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return text

    if ext in (".yaml", ".yml"):
        try:
            data = yaml.safe_load(text)
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except yaml.YAMLError:
            return text

    return text
