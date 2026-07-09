"""Small cross-module utilities."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path


def package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def executable_available(name: str) -> bool:
    return shutil.which(name) is not None


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

