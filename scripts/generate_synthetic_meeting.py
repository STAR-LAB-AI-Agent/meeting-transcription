"""Generate a synthetic Chinese meeting audio file for course demo.

Uses edge-tts (two distinct voices) and miniaudio to decode/resample to
16 kHz mono PCM16, then concatenates the lines into one WAV.

This produces clearly-marked *synthetic* meeting audio, not real speech.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
import wave
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "data" / "input" / "synthetic_meeting_demo.wav"

SAMPLE_RATE = 16000
SILENCE_SEC = 0.35

HOST_VOICE = "zh-CN-YunjianNeural"   # 主持人（男声）
MEMBER_VOICE = "zh-CN-XiaoxiaoNeural"  # 成员（女声）

# (speaker_label, text)
LINES = [
    ("host", "大家好，今天我们讨论智能体开发课程项目，主要确认会议语音转写模块的进展。"),
    ("member", "好的，目前我们已经使用 FunASR 完成语音识别，整体效果不错，中文识别准确率也比较稳定。"),
    ("host", "很好，接下来请确认一下项目预算的情况。"),
    ("member", "项目预算目前控制在三千元以内，暂时没有超支的风险。"),
    ("host", "那数据集这块的进展怎么样呢？"),
    ("member", "数据集整理计划在下周三之前完成，标注工作也在按计划推进。"),
    ("host", "好的，接下来需要完成关键词检索、时间定位和自动会议摘要的测试。"),
    ("member", "测试用例已经准备好了，我们会用真实音频来验证转写和检索的结果。"),
    ("host", "实验部分大家要按时完成，最后把代码提交到 GitHub，并且录制验收视频。"),
    ("member", "好的，我这边会全力配合。今天的会议就到这里，谢谢大家。"),
]


async def _synth_mp3(text: str, voice: str, path: Path) -> None:
    import edge_tts

    await edge_tts.Communicate(text, voice).save(str(path))


def _decode_16k_mono(mp3_bytes: bytes) -> bytes:
    import miniaudio

    decoded = miniaudio.decode(
        mp3_bytes,
        nchannels=1,
        sample_rate=SAMPLE_RATE,
        output_format=miniaudio.SampleFormat.SIGNED16,
    )
    return bytes(decoded.samples)


def _write_wav(path: Path, pcm: bytes, sample_rate: int) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def main() -> int:
    try:
        import edge_tts  # noqa: F401
        import miniaudio  # noqa: F401
    except ImportError as exc:
        print(
            "缺少依赖：请先执行 "
            "py -3.12 -m pip install edge-tts miniaudio",
            file=sys.stderr,
        )
        return 1

    silence = b"\x00\x00" * int(SAMPLE_RATE * SILENCE_SEC)
    chunks: list[bytes] = []
    for label, text in LINES:
        voice = HOST_VOICE if label == "host" else MEMBER_VOICE
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        asyncio.run(_synth_mp3(text, voice, tmp_path))
        mp3_bytes = tmp_path.read_bytes()
        tmp_path.unlink(missing_ok=True)
        chunks.append(_decode_16k_mono(mp3_bytes))
        chunks.append(silence)

    pcm = b"".join(chunks)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _write_wav(OUTPUT, pcm, SAMPLE_RATE)
    print(f"written {OUTPUT} ({len(pcm) / 2 / SAMPLE_RATE:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
