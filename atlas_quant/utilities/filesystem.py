"""File system utilities."""

import os
from pathlib import Path
from typing import Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path.

    Returns:
        Path object of the directory.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(path: Union[str, Path]) -> int:
    """Get file size in bytes.

    Args:
        path: File path.

    Returns:
        Size in bytes, or 0 if file does not exist.
    """
    path = Path(path)
    if path.is_file():
        return path.stat().st_size
    return 0


def list_files(directory: Union[str, Path], pattern: str = "*") -> list:
    """List files in a directory matching a pattern.

    Args:
        directory: Directory to search.
        pattern: Glob pattern (default: "*").

    Returns:
        List of Path objects.
    """
    directory = Path(directory)
    return list(directory.glob(pattern))
