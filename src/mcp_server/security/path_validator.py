from pathlib import Path


def validate_path(file_path: str, allowed_directories: list[str]) -> Path | None:
    """Resolve and validate that file_path is within allowed directories.

    Returns the resolved Path if valid, None if outside allowed dirs.
    Prevents symlink traversal and path traversal attacks.
    """
    try:
        resolved = Path(file_path).resolve(strict=True)
    except (OSError, ValueError):
        return None

    if not resolved.is_file():
        return None

    for allowed_dir in allowed_directories:
        allowed_resolved = Path(allowed_dir).resolve()
        if resolved == allowed_resolved or allowed_resolved in resolved.parents:
            return resolved

    return None
