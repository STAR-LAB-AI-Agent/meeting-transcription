"""Streamlit demo UI for the AI Meeting ASR Agent."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import agent_router, search, security, summarize, transcribe

st.set_page_config(page_title="AI 会议语音转写与检索智能体", page_icon="🎙️")
st.title("AI 会议语音转写与检索智能体")
st.caption("《智能体开发实战》第 15 题 · Agent → Skill → Script/CLI → FunASR")

INPUT_DIR = security.PROJECT_ROOT / "data" / "input"
INPUT_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_resource
def _transcript_cache(path: str) -> dict:
    p = security.validate_path(path, write=False, must_exist=True)
    return json.loads(p.read_text(encoding="utf-8"))


def _render_segments(segments: list[dict]) -> None:
    for seg in segments:
        start = search.format_ms(seg["start_ms"])
        end = search.format_ms(seg["end_ms"])
        st.markdown(f"**{start} - {end}**  {seg.get('text', '')}")


# ---- Sidebar: audio source ----
st.sidebar.header("1. 选择音频")
uploaded = st.sidebar.file_uploader(
    "上传会议音频（wav / mp3 / m4a）",
    type=["wav", "mp3", "m4a", "flac", "aac", "ogg"],
)
existing = sorted(
    p.name
    for p in INPUT_DIR.iterdir()
    if p.suffix.lower() in (".wav", ".mp3", ".m4a", ".flac", ".aac", ".ogg")
)
selected = st.sidebar.selectbox("或选择已有音频", [""] + existing)

audio_path: str | None = None
if uploaded is not None:
    safe_name = Path(uploaded.name).name
    dest = INPUT_DIR / safe_name
    dest.write_bytes(uploaded.getbuffer())
    audio_path = str(dest)
    st.sidebar.success(f"已保存：{safe_name}")
elif selected:
    audio_path = str(INPUT_DIR / selected)

if st.sidebar.button("开始转写", disabled=audio_path is None):
    try:
        with st.spinner("FunASR 转写中（首次会下载模型，请耐心等待）..."):
            payload = transcribe.transcribe(audio_path, overwrite=True)
        st.session_state["transcript"] = payload
        st.success("转写完成")
    except Exception as exc:  # noqa: BLE001 - surface any error to the UI
        st.error(f"转写失败：{exc}")

transcript = st.session_state.get("transcript")
if transcript is None and existing:
    transcript = _transcript_cache(str(INPUT_DIR / existing[0]))

st.header("2. 转写结果")
if transcript:
    _render_segments(transcript.get("segments", []))
    with st.expander("原始 JSON"):
        st.json(transcript)
else:
    st.info("尚无转写结果，请先转写音频。")

st.header("3. 关键词检索")
keyword = st.text_input("关键词", placeholder="例如：预算")
if st.button("搜索") and keyword:
    data = transcript or _transcript_cache(
        str(PROJECT_ROOT / "examples" / "demo_transcript.json")
    )
    hits = search.search_keyword(data.get("segments", []), keyword, context=1)
    if not hits:
        st.warning("未找到匹配片段")
    for h in hits:
        st.markdown(
            f"**命中 {search.format_ms(h['start_ms'])}**  {h['sentence']}"
        )
        for b in h["context_before"]:
            st.caption(f"上文：{b}")
        for a in h["context_after"]:
            st.caption(f"下文：{a}")

st.header("4. 时间位置查询")
time_query = st.text_input("时间点", placeholder="例如：01:30")
if st.button("定位") and time_query:
    data = transcript or _transcript_cache(
        str(PROJECT_ROOT / "examples" / "demo_transcript.json")
    )
    result = search.locate_time(data.get("segments", []), time_query, context=1)
    if result.get("out_of_range"):
        st.warning("该时间超出会议范围")
    _render_segments(result.get("segments", []))

st.header("5. 会议摘要")
if st.button("生成会议摘要"):
    data = transcript or _transcript_cache(
        str(PROJECT_ROOT / "examples" / "demo_transcript.json")
    )
    result = summarize.summarize(data)
    st.subheader("主题")
    st.write(result["topic"])
    st.subheader("概要")
    st.write(result["summary"])
    st.subheader("主要讨论点")
    for p in result["key_points"]:
        st.markdown(f"- {p}")
    st.subheader("决策事项")
    for d in result["decisions"]:
        st.markdown(f"- {d}")
    st.subheader("待办事项")
    for a in result["action_items"]:
        st.markdown(f"- {a}")
    st.caption(f"生成方式：{result['method']}")
