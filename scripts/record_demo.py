"""Record a real Streamlit demo walkthrough with Playwright (video output)."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "docs" / "demo"
RAW_WEBM = OUT_DIR / "recording_raw.webm"
TIMING_JSON = OUT_DIR / "recording_timings.json"

CHROME_EXE = Path(
    os.path.expandvars(
        r"%LOCALAPPDATA%\ms-playwright\chromium-1223\chrome-win64\chrome.exe"
    )
)

AUDIO = PROJECT_ROOT / "data" / "input" / "synthetic_meeting_demo.wav"
URL = "http://localhost:8501"


def _pause(page, seconds: float) -> None:
    page.wait_for_timeout(int(seconds * 1000))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CHROME_EXE.exists():
        print("chromium not found at", CHROME_EXE, file=sys.stderr)
        return 1
    if not AUDIO.exists():
        print("audio not found at", AUDIO, file=sys.stderr)
        return 1

    timings: dict[str, float] = {}
    t_start = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=str(CHROME_EXE))
        context = browser.new_context(
            record_video_dir=str(OUT_DIR),
            viewport={"width": 1280, "height": 720},
            record_video_size={"width": 1280, "height": 720},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle")

        # 0-5s: title
        page.get_by_text("AI 会议语音转写与检索智能体").first.wait_for()
        _pause(page, 3)

        # upload audio
        page.locator('input[type="file"]').set_input_files(str(AUDIO))
        page.get_by_text("已保存：synthetic_meeting_demo.wav").first.wait_for(timeout=30000)
        _pause(page, 1)

        # click transcribe
        timings["click_transcribe"] = round(time.time() - t_start, 2)
        page.get_by_role("button", name="开始转写").click()

        # wait for real FunASR completion
        page.get_by_text("转写完成").first.wait_for(timeout=240000)
        timings["transcribe_done"] = round(time.time() - t_start, 2)
        _pause(page, 2)

        # show timestamped transcript
        page.get_by_text("2. 转写结果").scroll_into_view_if_needed()
        _pause(page, 3)

        # search 预算
        page.get_by_text("3. 关键词检索").scroll_into_view_if_needed()
        page.get_by_placeholder("例如：预算").fill("预算")
        page.get_by_role("button", name="搜索").click()
        page.get_by_text("命中").first.wait_for(timeout=30000)
        _pause(page, 4)

        # locate 00:30
        page.get_by_text("4. 时间位置查询").scroll_into_view_if_needed()
        page.get_by_placeholder("例如：01:30").fill("00:30")
        page.get_by_role("button", name="定位").click()
        _pause(page, 4)

        # summary
        page.get_by_text("5. 会议摘要").scroll_into_view_if_needed()
        page.get_by_role("button", name="生成会议摘要").click()
        page.get_by_text("主题").first.wait_for(timeout=30000)
        _pause(page, 5)

        context.close()
        browser.close()

    # rename the produced webm
    produced = sorted(OUT_DIR.glob("*.webm"), key=lambda f: f.stat().st_mtime)
    if produced:
        produced[-1].replace(RAW_WEBM)

    timings["end"] = round(time.time() - t_start, 2)
    TIMING_JSON.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    print("recorded", RAW_WEBM)
    print("timings", timings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
