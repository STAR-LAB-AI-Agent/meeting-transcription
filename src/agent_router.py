"""Lightweight rule-based natural-language intent router.

Deterministic dispatch happens here in Python; no LLM is required for the
core routing decision.
"""

from __future__ import annotations

import re

_TIME_RE = re.compile(r"\b(\d{1,3}):(\d{1,2})(?::(\d{1,2}))?\b")
_RANGE_RE = re.compile(
    r"(\d{1,3})\s*(?:分钟|分)\s*(?:到|至|~|-)\s*(\d{1,3})\s*(?:分钟|分)"
)
_TRANSCRIBE_KEYWORDS = (
    "转写", "转录", "识别", "转成文字", "文字稿", "asr", "transcribe",
)
_SEARCH_KEYWORDS = (
    "搜索", "查找", "查询", "查一下", "找一下", "哪里提到", "提到了",
    "提到", "提及", "search", "find",
)
_SUMMARY_KEYWORDS = ("摘要", "总结", "概括", "纪要", "summarize", "summary")


def _extract_search_keyword(query: str) -> str:
    q = query.strip()
    patterns = (
        r"搜索\s*[“\"']?(.+?)[”\"']?$",
        r"查找\s*[“\"']?(.+?)[”\"']?$",
        r"查询\s*[“\"']?(.+?)[”\"']?$",
        r"查一下\s*[“\"']?(.+?)[”\"']?$",
        r"找一下\s*[“\"']?(.+?)[”\"']?$",
        r"哪里提到(?:了)?\s*[“\"']?(.+?)[”\"']?$",
        r"(?:提到|提及)(?:了)?\s*[“\"']?(.+?)[”\"']?$",
    )
    for pat in patterns:
        m = re.search(pat, q)
        if m:
            kw = m.group(1).strip()
            kw = re.sub(
                r"(说的部分|说的内容|的部分|说的|相关内容|内容)$", "", kw
            ).strip()
            return kw
    for verb in _SEARCH_KEYWORDS:
        if q.lower().startswith(verb):
            rest = q[len(verb):].strip().lstrip("了：: “\"'").strip()
            if rest:
                return rest
    return q


def extract_time(query: str) -> str | None:
    """Extract an ``HH:MM`` / ``HH:MM:SS`` style time from a query."""
    m = _TIME_RE.search(query or "")
    return m.group(0) if m else None


def extract_range_minutes(query: str) -> tuple[int, int] | None:
    """Extract ``X分钟到Y分钟`` as (start_seconds, end_seconds)."""
    m = _RANGE_RE.search(query or "")
    if not m:
        return None
    return int(m.group(1)) * 60, int(m.group(2)) * 60


def route(query: str) -> dict:
    """Route a natural-language query to an intent and parameters."""
    q = (query or "").strip()
    low = q.lower()

    if any(k in low for k in _SEARCH_KEYWORDS):
        return {
            "intent": "search",
            "keyword": _extract_search_keyword(q),
            "query": q,
        }

    if _TIME_RE.search(q) or _RANGE_RE.search(q) or "附近" in low:
        return {"intent": "locate", "query": q}

    if any(k in low for k in _SUMMARY_KEYWORDS):
        return {"intent": "summarize", "query": q}

    if any(k in low for k in _TRANSCRIBE_KEYWORDS):
        return {"intent": "transcribe", "query": q}

    return {"intent": "unknown", "query": q}
