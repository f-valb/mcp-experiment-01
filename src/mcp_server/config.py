import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ServerConfig:
    allowed_directories: list[str] = field(default_factory=lambda: [os.path.expanduser("~")])
    max_file_size_mb: int = 50
    max_content_chars: int = 100_000
    browser_timeout_ms: int = 30_000
    browser_headless: bool = True


_config: ServerConfig | None = None


def load_config(config_path: str | None = None) -> ServerConfig:
    global _config
    if _config is not None:
        return _config

    config = ServerConfig()

    # Try loading from config.yaml
    if config_path is None:
        config_path = os.environ.get(
            "MCP_CONFIG_PATH",
            str(Path(__file__).parent.parent.parent / "config.yaml"),
        )

    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}

        if "allowed_directories" in data:
            config.allowed_directories = [
                os.path.expanduser(d) for d in data["allowed_directories"]
            ]
        if "max_file_size_mb" in data:
            config.max_file_size_mb = int(data["max_file_size_mb"])
        if "max_content_chars" in data:
            config.max_content_chars = int(data["max_content_chars"])
        if "browser_timeout_ms" in data:
            config.browser_timeout_ms = int(data["browser_timeout_ms"])
        if "browser_headless" in data:
            config.browser_headless = bool(data["browser_headless"])

    # Environment variable overrides
    if env_dirs := os.environ.get("MCP_ALLOWED_DIRS"):
        config.allowed_directories = [
            os.path.expanduser(d.strip()) for d in env_dirs.split(",")
        ]

    _config = config
    return config
