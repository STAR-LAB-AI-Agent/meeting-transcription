"""JSONL structured logging with secret redaction.

Logs never contain audio content or sensitive credentials; only the file
basename, action, status, duration and an error type are recorded.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .security import PROJECT_ROOT, redact_secrets

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "meeting_asr.jsonl"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def log(
    action: str,
    input_file: str | Path | None = None,
    status: str = "ok",
    duration_ms: int | None = None,
    error_type: str | None = None,
    extra: dict | None = None,
) -> None:
    """Append a single redacted JSONL log line."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry: dict = {
        "timestamp": _now(),
        "action": action,
        "input_file": Path(input_file).name if input_file else None,
        "status": status,
        "duration_ms": duration_ms,
        "error_type": error_type,
    }
    if extra:
        entry["extra"] = json.dumps(extra, ensure_ascii=False, default=str)
    line = redact_secrets(json.dumps(entry, ensure_ascii=False))
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
