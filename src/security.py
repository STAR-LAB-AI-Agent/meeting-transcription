"""Path security and secret-redaction utilities.

This module enforces a minimal-privilege file-access policy:

* All paths must resolve inside the project root (no directory traversal).
* Reads are only allowed from ``data/input``, ``data/output``, ``examples``
  and ``logs``.
* Writes are only allowed to ``data/output`` and ``logs``.
* Secret-like strings (API keys, tokens, passwords) are redacted from logs.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_READ_DIRS: tuple[Path, ...] = (
    PROJECT_ROOT / "data" / "input",
    PROJECT_ROOT / "data" / "output",
    PROJECT_ROOT / "examples",
    PROJECT_ROOT / "logs",
)

ALLOWED_WRITE_DIRS: tuple[Path, ...] = (
    PROJECT_ROOT / "data" / "output",
    PROJECT_ROOT / "logs",
)

_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\b(sk-[A-Za-z0-9_\-]{16,})\b"),
    re.compile(r"(?i)\b(api[_-]?key\s*[:=]\s*\S+)"),
    re.compile(r"(?i)\b(access[_-]?token\s*[:=]\s*\S+)"),
    re.compile(r"(?i)\b(password\s*[:=]\s*\S+)"),
    re.compile(r"(?i)\b(bearer\s+[A-Za-z0-9._\-]{10,})"),
    re.compile(r"\b(ghp|gho|ghu|github_pat)_[A-Za-z0-9_]{10,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(xox[baprs]-[A-Za-z0-9\-]{10,})\b"),
    re.compile(r"(?i)\b(secret\s*[:=]\s*\S+)"),
)


class SecurityError(Exception):
    """Raised when a supplied path violates the access policy."""


def resolve_project_path(path: str | os.PathLike[str]) -> Path:
    """Resolve a possibly-relative path against the project root."""
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return Path(os.path.normpath(str(p))).resolve()


def _is_within(path: Path, dirs: tuple[Path, ...]) -> bool:
    for base in dirs:
        try:
            path.relative_to(base)
            return True
        except ValueError:
            continue
    return False


def ensure_within_project(path: Path) -> Path:
    """Reject paths that escape the project root (directory traversal)."""
    root = PROJECT_ROOT.resolve()
    try:
        rel = path.relative_to(root)
    except ValueError as exc:
        raise SecurityError(f"拒绝目录穿越：路径越出项目目录 {path}") from exc
    if ".." in rel.parts:
        raise SecurityError(f"拒绝目录穿越：检测到 '..' 组件 {path}")
    return path


def validate_path(
    path: str | os.PathLike[str],
    *,
    write: bool = False,
    must_exist: bool = False,
) -> Path:
    """Validate a path and return its resolved, policy-approved form."""
    resolved = ensure_within_project(resolve_project_path(path))
    allowed = ALLOWED_WRITE_DIRS if write else ALLOWED_READ_DIRS
    if not _is_within(resolved, allowed):
        mode = "写入" if write else "读取"
        raise SecurityError(f"安全策略：不允许{mode} {resolved}")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"文件不存在：{resolved}")
    return resolved


def redact_secrets(text: str) -> str:
    """Replace secret-like substrings with a placeholder."""
    out = text
    for pattern in _SECRET_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out
