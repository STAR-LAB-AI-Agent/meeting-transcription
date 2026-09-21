"""FunASR transcription integration.

FunASR is imported lazily so that search / locate / summarize and the unit
tests all work even before the heavy FunASR + Torch stack is installed.
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import time
from pathlib import Path

from . import audio_utils, logger, security

#: Real ASR has been executed on public Chinese speech samples via FunASR.
REAL_ASR_TEST = "PASS"

#: Pipeline-level validation status (public speech, not necessarily meetings).
REAL_ASR_PIPELINE_TEST = "PASS"

#: Meeting-scene demo still needs a (simulated) multi-speaker meeting recording.
MEETING_SCENE_TEST = "WAITING_FOR_MEETING_AUDIO"

FUNASR_MODEL = "paraformer-zh"
FUNASR_VAD_MODEL = "fsmn-vad"
FUNASR_PUNC_MODEL = "ct-punc"

_MODEL_CACHE = None


def _get_model():
    """Instantiate (and cache) the FunASR model pipeline."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    try:
        from funasr import AutoModel
    except ImportError as exc:
        raise RuntimeError(
            "FunASR 未安装，无法执行真实转写。\n"
            "请先运行 scripts/setup_windows.bat（或 pip install funasr），\n"
            "模型首次加载会自动从 ModelScope 下载并缓存。"
        ) from exc
    _MODEL_CACHE = AutoModel(
        model=FUNASR_MODEL,
        vad_model=FUNASR_VAD_MODEL,
        punc_model=FUNASR_PUNC_MODEL,
    )
    return _MODEL_CACHE


def _parse_result(result) -> list[dict]:
    """Convert FunASR output into the canonical segments format."""
    segments: list[dict] = []
    if not result:
        return segments
    item = result[0] if isinstance(result, list) else result

    # Preferred: VAD-split sentences with per-sentence timestamps.
    sentence_info = item.get("sentence_info") or []
    for sent in sentence_info:
        text = (sent.get("text") or "").strip()
        if not text:
            continue
        start = sent.get("start")
        end = sent.get("end")
        if start is None or end is None:
            ts = sent.get("timestamp") or []
            if ts:
                start = ts[0][0]
                end = ts[-1][1]
        segments.append(
            {
                "start_ms": int(start or 0),
                "end_ms": int(end or 0),
                "text": text,
            }
        )
    if segments:
        return segments

    # Fallback: single text with top-level character-level timestamps.
    text = (item.get("text") or "").strip()
    if not text:
        return segments
    ts = item.get("timestamp") or []
    start = ts[0][0] if ts else 0
    end = ts[-1][1] if ts else 0
    segments.append({"start_ms": int(start), "end_ms": int(end), "text": text})
    return segments


def _environment_info() -> dict:
    info = {
        "python_version": platform.python_version(),
        "model": FUNASR_MODEL,
        "vad_model": FUNASR_VAD_MODEL,
        "punc_model": FUNASR_PUNC_MODEL,
    }
    for pkg in ("funasr", "torch", "torchaudio", "modelscope"):
        try:
            info[f"{pkg}_version"] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            info[f"{pkg}_version"] = None
    return info


def transcribe(
    audio_path: str | Path,
    output_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict:
    """Transcribe an audio file with FunASR and write a JSON transcript."""
    start = time.time()
    audio = security.validate_path(audio_path, write=False, must_exist=True)
    audio_utils.validate_audio_file(audio)

    if not audio_utils.check_ffmpeg() and audio.suffix.lower() != ".wav":
        hint = audio_utils.ffmpeg_status()["hint"]
        raise RuntimeError(
            f"转写 {audio.suffix} 需要 ffmpeg，但系统未检测到 ffmpeg。\n{hint}"
        )

    if output_path is None:
        output_path = security.PROJECT_ROOT / "data" / "output" / (audio.stem + ".json")
    else:
        output_path = security.validate_path(output_path, write=True)

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"输出文件已存在：{output_path.name}（使用 --overwrite 覆盖）"
        )

    model = _get_model()
    result = model.generate(input=str(audio), batch_size_s=300)
    segments = _parse_result(result)

    payload = {
        "audio_file": audio.name,
        "model": FUNASR_MODEL,
        "segments": segments,
        "metadata": _environment_info(),
        "transcribed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    txt_path = output_path.with_suffix(".txt")
    txt_path.write_text(transcript_to_markdown(payload), encoding="utf-8")

    duration_ms = int((time.time() - start) * 1000)
    logger.log(
        "transcribe",
        audio,
        status="ok",
        duration_ms=duration_ms,
        extra={
            "output": output_path.name,
            "txt": txt_path.name,
            "segments": len(segments),
        },
    )
    return payload


def transcript_to_markdown(payload: dict) -> str:
    """Render a transcript payload as human-readable Markdown."""
    from .search import format_ms

    lines = [
        "# 会议转写结果",
        "",
        f"- 音频文件：{payload.get('audio_file')}",
        f"- 模型：{payload.get('model')}",
        "",
    ]
    for seg in payload.get("segments", []):
        start = format_ms(seg["start_ms"])
        end = format_ms(seg["end_ms"])
        lines.append(f"- **{start} - {end}** {seg.get('text', '')}")
    return "\n".join(lines) + "\n"
