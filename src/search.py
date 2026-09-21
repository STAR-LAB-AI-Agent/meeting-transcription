"""Keyword search, time-based location and token-compression helpers."""

from __future__ import annotations

import re
from typing import Any

_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


def format_ms(ms: float | int) -> str:
    """Format milliseconds as ``HH:MM:SS.ss``."""
    ms = int(round(ms))
    total = ms / 1000.0
    h = int(total // 3600)
    m = int((total % 3600) // 60)
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def parse_time_to_ms(value: str | int | float) -> int:
    """Parse seconds, ``MM:SS`` or ``HH:MM:SS`` into milliseconds."""
    if isinstance(value, (int, float)):
        return int(round(float(value) * 1000))
    s = str(value).strip()
    if not s:
        raise ValueError("时间不能为空")
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return int(round(float(s) * 1000))
    if re.fullmatch(r"\d{1,2}:\d{1,2}(\.\d+)?", s):
        m, sec = s.split(":")
        return int((int(m) * 60 + float(sec)) * 1000)
    if re.fullmatch(r"\d{1,3}:\d{1,2}:\d{1,2}(\.\d+)?", s):
        h, m, sec = s.split(":")
        return int((int(h) * 3600 + int(m) * 60 + float(sec)) * 1000)
    raise ValueError(f"无法解析时间：{value!r}（支持 秒 / MM:SS / HH:MM:SS）")


def search_keyword(
    segments: list[dict],
    keyword: str,
    context: int = 1,
    max_results: int | None = None,
) -> list[dict]:
    """Return keyword hits with timestamps and a little surrounding context."""
    kw = (keyword or "").strip()
    if not kw:
        return []
    kw_lower = kw.lower()
    hits: list[dict] = []
    for i, seg in enumerate(segments):
        text = seg.get("text", "")
        if kw_lower in text.lower():
            before = [
                segments[j].get("text", "")
                for j in range(max(0, i - context), i)
            ]
            after = [
                segments[j].get("text", "")
                for j in range(i + 1, min(len(segments), i + context + 1))
            ]
            hits.append(
                {
                    "keyword": kw,
                    "start_ms": int(seg.get("start_ms", 0)),
                    "end_ms": int(seg.get("end_ms", 0)),
                    "sentence": text,
                    "context_before": before,
                    "context_after": after,
                }
            )
    if max_results is not None:
        hits = hits[:max_results]
    return hits


def locate_time(
    segments: list[dict],
    time_value: str | int | float,
    context: int = 1,
) -> dict:
    """Locate the meeting content at (or nearest to) a point in time."""
    target_ms = parse_time_to_ms(time_value)
    if not segments:
        return {
            "target_ms": target_ms,
            "target_time": format_ms(target_ms),
            "out_of_range": True,
            "segments": [],
        }

    containing = None
    best_idx = 0
    best_dist = float("inf")
    for i, seg in enumerate(segments):
        start = int(seg.get("start_ms", 0))
        end = int(seg.get("end_ms", 0))
        if start <= target_ms <= end:
            containing = i
            break
        dist = min(abs(start - target_ms), abs(end - target_ms))
        if dist < best_dist:
            best_dist = dist
            best_idx = i

    center = containing if containing is not None else best_idx
    lo = max(0, center - context)
    hi = min(len(segments), center + context + 1)
    out_of_range = containing is None and (
        target_ms < segments[0].get("start_ms", 0)
        or target_ms > segments[-1].get("end_ms", 0)
    )
    return {
        "target_ms": target_ms,
        "target_time": format_ms(target_ms),
        "out_of_range": out_of_range,
        "segments": segments[lo:hi],
    }


def locate_range(
    segments: list[dict],
    start_value: str | int | float,
    end_value: str | int | float,
) -> dict:
    """Return all segments overlapping the inclusive time range."""
    start_ms = parse_time_to_ms(start_value)
    end_ms = parse_time_to_ms(end_value)
    matched = [
        seg
        for seg in segments
        if int(seg.get("end_ms", 0)) >= start_ms
        and int(seg.get("start_ms", 0)) <= end_ms
    ]
    return {
        "start_ms": start_ms,
        "end_ms": end_ms,
        "start_time": format_ms(start_ms),
        "end_time": format_ms(end_ms),
        "segments": matched,
    }


def estimate_tokens(text: str) -> int:
    """Cheap token estimate: CJK chars ~1 token, else ~4 chars/token."""
    if not text:
        return 0
    cjk = len(_CJK_RE.findall(text))
    other = len(text) - cjk
    return cjk + max(1, other // 4)


def compress_hits(hits: list[dict]) -> str:
    """Build a compact text block from hit segments only."""
    parts = []
    for h in hits:
        parts.append(f"[{format_ms(h['start_ms'])}] {h.get('sentence', '')}")
    return "\n".join(parts)


def compression_stats(before: str, after: str) -> dict:
    """Compare token cost of full transcript vs. only-hit fragments."""
    tb = estimate_tokens(before)
    ta = estimate_tokens(after)
    if tb <= 0:
        return {
            "compression_ratio": 1.0,
            "estimated_token_before": tb,
            "estimated_token_after": ta,
            "reduction_percent": 0.0,
        }
    ratio = ta / tb
    return {
        "compression_ratio": round(ratio, 4),
        "estimated_token_before": tb,
        "estimated_token_after": ta,
        "reduction_percent": round((1 - ratio) * 100, 2),
    }
