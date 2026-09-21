"""Audio helpers: format validation and ffmpeg detection."""

from __future__ import annotations

import shutil
from pathlib import Path

SUPPORTED_FORMATS = (".wav", ".mp3", ".m4a", ".flac", ".aac", ".ogg", ".wma")

_WINDOWS_HINT = (
    "Windows 安装 ffmpeg 提示：\n"
    "  1) 下载: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip\n"
    "  2) 解压后把 bin 目录加入系统 PATH\n"
    "  3) 或执行: winget install Gyan.FFmpeg\n"
    "然后重新打开终端即可。"
)


def check_ffmpeg() -> bool:
    """Return True when the ``ffmpeg`` executable is on PATH."""
    return shutil.which("ffmpeg") is not None


def check_ffprobe() -> bool:
    """Return True when the ``ffprobe`` executable is on PATH."""
    return shutil.which("ffprobe") is not None


def ffmpeg_status() -> dict:
    has = check_ffmpeg()
    return {
        "ffmpeg_available": has,
        "ffprobe_available": check_ffprobe(),
        "hint": None if has else _WINDOWS_HINT,
    }


def validate_audio_file(path: str | Path) -> Path:
    """Validate existence and extension of an audio file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"音频文件不存在：{p}")
    if p.suffix.lower() not in SUPPORTED_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(f"不支持的音频格式：{p.suffix}（支持 {supported}）")
    return p
