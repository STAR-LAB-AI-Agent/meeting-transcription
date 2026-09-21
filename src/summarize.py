"""Meeting summary: deterministic extractive fallback + optional LLM path."""

from __future__ import annotations

import json as _json
import os
import re
import urllib.request
from collections import Counter

from .search import format_ms

_DECISION_KEYWORDS = (
    "决定", "确定", "通过", "同意", "结论", "达成一致", "最终",
)
_ACTION_KEYWORDS = (
    "待办", "负责", "提交", "跟进", "完成", "todo", "牵头",
)
_STOPWORDS = set(
    "的 了 是 在 和 与 及 就 都 也 被 把 我们 大家 这个 那个 进行 一个 "
    "以及 如果 可以 会 还 有 说 表示 提出 提到 会议 今天 本次 关于 目前 "
    "请 由 先 中 到 为 对 从 上 下 后 前 里 内 外 让 向 这 那 他 她 它 "
    "项目 需要 增加 补充 执行 达到 总体 上限 相关 具体 优先 保障 部门 "
    "明细 接下来 工作 情况 进度 方向 重点 建议 采购 万元 十 二十 两百 "
    "大家 现在 然后 还是 已经 主要 讨论 介绍 参加 欢迎 月度 预算安排".split()
    + "王经理 张老师 李工 经理 老师 财务 同学 女士 先生".split()
    + "整体 进度 正常 达到 提升 提高 方面 进一步 部分 环节".split()
    + "决定 同意 确定 通过 结论 确认 下周 本月 本季度 下季度".split()
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?；;])\s*", text)
    return [p.strip() for p in parts if p.strip()]


def _keywords(text: str, top_n: int = 6) -> list[str]:
    try:
        import jieba

        for term in (
            "深度学习", "语音识别", "数据标注", "预算执行", "服务器采购",
            "标注数据", "财务部门", "预算明细", "预算上限",
        ):
            jieba.add_word(term)
        words = [w.strip() for w in jieba.cut(text) if len(w.strip()) >= 2]
    except ImportError:
        words = re.findall(
            r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9_-]{2,}", text
        )
    freq = Counter(w for w in words if w.lower() not in _STOPWORDS and len(w) >= 2)
    return [w for w, _ in freq.most_common(top_n)]


def _dedup(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def extractive_summary(segments: list[dict], top_n: int = 5) -> dict:
    """Build a rule-based extractive summary without inventing any facts."""
    texts = [seg.get("text", "") for seg in segments]
    full = "\n".join(texts)
    sentences = _split_sentences(" ".join(texts))
    keywords = _keywords(full, top_n=6)
    topic = "、".join(keywords[:3]) if keywords else "（未识别出主题）"

    scored = []
    for i, sent in enumerate(sentences):
        score = sum(1 for kw in keywords if kw in sent) + len(sent) * 0.0001
        scored.append((i, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    key_points = [sentences[i] for i, _ in scored[:top_n] if sentences[i]]

    decisions = [s for s in sentences if any(k in s for k in _DECISION_KEYWORDS)]
    action_items = [s for s in sentences if any(k in s for k in _ACTION_KEYWORDS)]

    summary_body = " ".join(key_points) if key_points else full[:200]
    return {
        "topic": topic,
        "summary": summary_body,
        "key_points": _dedup(key_points),
        "decisions": _dedup(decisions),
        "action_items": _dedup(action_items),
        "method": "extractive_fallback",
    }


def _llm_summary(
    segments: list[dict],
    base_url: str,
    api_key: str,
    model: str,
) -> dict:
    compact = "\n".join(
        f"[{format_ms(s.get('start_ms', 0))}] {s.get('text', '')}"
        for s in segments
    )
    prompt = (
        "你是会议助手。根据以下带时间戳的会议文本，输出严格 JSON，字段："
        "topic, summary, key_points(数组), decisions(数组), action_items(数组)。"
        "只依据文本，不要编造姓名、结论或行动项。\n\n" + compact
    )
    body = _json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "输出严格 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    parsed = _json.loads(content)
    parsed["method"] = "llm"
    return parsed


def summarize(transcript: dict, use_llm: bool = False) -> dict:
    """Produce a structured meeting summary.

    Defaults to a deterministic extractive fallback so the project always
    works; an external LLM is only used when explicitly enabled and
    configured via ``MEETING_ASR_LLM_API_KEY`` / ``MEETING_ASR_LLM_BASE_URL``.
    """
    segments = transcript.get("segments", [])
    if not use_llm:
        return extractive_summary(segments)

    api_key = os.environ.get("MEETING_ASR_LLM_API_KEY")
    base_url = os.environ.get("MEETING_ASR_LLM_BASE_URL")
    model = os.environ.get("MEETING_ASR_LLM_MODEL", "gpt-4o-mini")
    if not (api_key and base_url):
        result = extractive_summary(segments)
        result["note"] = (
            "未配置 LLM（MEETING_ASR_LLM_API_KEY / MEETING_ASR_LLM_BASE_URL），"
            "已使用本地抽取式摘要。"
        )
        return result
    return _llm_summary(segments, base_url, api_key, model)
