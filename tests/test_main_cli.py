from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def test_main_help_includes_no_llm() -> None:
    result = subprocess.run(
        [sys.executable, str(_ROOT / "main.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0
    assert "--no-llm" in result.stdout
