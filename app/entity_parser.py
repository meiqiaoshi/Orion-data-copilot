from __future__ import annotations

import re


def parse_config_path(text: str) -> str | None:
    match = re.search(r"\b([\w\-/]+\.ya?ml)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def parse_pipeline_name(text: str) -> str | None:
    match = re.search(r"\bpipeline\s+([a-zA-Z0-9_\-]+)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None