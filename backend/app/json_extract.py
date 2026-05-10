from __future__ import annotations

import json
import re
from typing import Any


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.MULTILINE)


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Crew outputs occasionally wrap JSON in fenced code blocks — strip and parse safely.
    """
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty model output")

    m = _FENCE_RE.search(raw)
    if m:
        raw = m.group(1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start : end + 1])
        else:
            raise

    if not isinstance(data, dict):
        raise TypeError("Expected JSON object")
    return data
