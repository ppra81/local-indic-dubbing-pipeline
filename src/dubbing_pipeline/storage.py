"""Result persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, data: Any) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return output

