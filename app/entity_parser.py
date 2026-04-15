from __future__ import annotations

import re


def parse_config_path(text: str) -> str | None:
    match = re.search(r"\bconfig\s*[=:]\s*([\w\-/]+\.ya?ml)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"\b([\w\-/]+\.ya?ml)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def parse_pipeline_name(text: str) -> str | None:
    patterns = [
        r"\bpipeline\s*[=:]\s*([a-zA-Z0-9_\-]+)",
        r"\bpipeline\s+([a-zA-Z0-9_\-]+)\b",
        r"管道\s*[=:：]\s*([a-zA-Z0-9_\-]+)",
        r"管道\s+([a-zA-Z0-9_\-]+)",
        r"管道([a-zA-Z0-9_\-]+)",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_dataset_name(text: str) -> str | None:
    patterns = [
        r"\bdataset\s*[=:]\s*([a-zA-Z0-9_\-]+)",
        r"\bdataset\s+([a-zA-Z0-9_\-]+)\b",
        r"数据集\s*[=:：]\s*([a-zA-Z0-9_\-]+)",
        r"数据集\s+([a-zA-Z0-9_\-]+)",
        r"数据集([a-zA-Z0-9_\-]+)",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
