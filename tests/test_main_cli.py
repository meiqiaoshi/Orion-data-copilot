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
    assert "--duckdb" in result.stdout
    assert "--query" in result.stdout
    assert "--plan-only" in result.stdout


def test_main_version() -> None:
    from app.version import __version__ as expected

    result = subprocess.run(
        [sys.executable, str(_ROOT / "main.py"), "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0
    assert "main.py" in result.stdout
    assert expected in result.stdout


def test_main_query_one_shot_rules_only() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(_ROOT / "main.py"),
            "--no-llm",
            "--query",
            "what is the weather",
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0
    assert "Query>" not in result.stdout
    assert "Intent: unknown" in result.stdout
    assert "Action: clarify_or_fallback" in result.stdout


def test_main_query_one_shot_plan_only_skips_execution() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(_ROOT / "main.py"),
            "--no-llm",
            "--plan-only",
            "--query",
            "what is the weather",
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0
    assert "Intent: unknown" in result.stdout
    assert "--- Execution ---" not in result.stdout
