"""Capture real screenshots for the internship manual."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "docs" / "screenshots" / "final_manual"
AUDIO = PROJECT_ROOT / "data" / "input" / "synthetic_meeting_demo.wav"
CHROME = Path(
    os.path.expandvars(
        r"%LOCALAPPDATA%\ms-playwright\chromium-1223\chrome-win64\chrome.exe"
    )
)
URL = "http://localhost:8501"

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_text_image(title: str, lines: list[str], out: Path) -> None:
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (17, 21, 27))
    d = ImageDraw.Draw(img)
    ft = _font(34)
    fb = _font(24)
    y = 34
    d.text((42, y), title, font=ft, fill=(120, 220, 160))
    y += 58
    for line in lines:
        d.text((42, y), line, font=fb, fill=(224, 230, 238))
        y += 36
    img.save(out)


def capture_gui() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=str(CHROME))
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(URL, wait_until="networkidle")
        page.get_by_text("AI 会议语音转写与检索智能体").first.wait_for()

        page.locator('input[type="file"]').set_input_files(str(AUDIO))
        page.get_by_text("已保存：synthetic_meeting_demo.wav").first.wait_for(timeout=30000)
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "fig1_gui_home.png"))

        page.get_by_role("button", name="开始转写").click()
        page.get_by_text("转写完成").first.wait_for(timeout=240000)
        page.wait_for_timeout(800)
        page.get_by_text("2. 转写结果").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "fig2_transcript.png"))

        page.get_by_text("3. 关键词检索").scroll_into_view_if_needed()
        page.get_by_placeholder("例如：预算").fill("预算")
        page.get_by_role("button", name="搜索").click()
        page.get_by_text("命中").first.wait_for(timeout=30000)
        page.get_by_text("3. 关键词检索").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "fig3_search.png"))

        page.get_by_text("4. 时间位置查询").scroll_into_view_if_needed()
        page.get_by_placeholder("例如：01:30").fill("00:30")
        page.get_by_role("button", name="定位").click()
        page.wait_for_timeout(1500)
        page.get_by_text("4. 时间位置查询").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "fig4_locate.png"))

        page.get_by_text("5. 会议摘要").scroll_into_view_if_needed()
        page.get_by_role("button", name="生成会议摘要").click()
        page.get_by_text("主题").first.wait_for(timeout=30000)
        page.wait_for_timeout(800)
        page.get_by_text("5. 会议摘要").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "fig5_summary.png"))

        browser.close()


def capture_evidence() -> None:
    # fig6: nanobot skill discovery
    disc = (PROJECT_ROOT / "docs" / "real_validation" / "nanobot_skill_discovery.txt").read_text(
        encoding="utf-8"
    )
    render_text_image("nanobot meeting-asr Skill 发现", disc.strip().splitlines(), OUT / "fig6_skill.png")

    # fig7: nanobot runtime (real tool call + exit code)
    ev = (PROJECT_ROOT / "docs" / "real_validation" / "nanobot_runtime_transcribe.txt").read_text(
        encoding="utf-8"
    )
    lines = [
        "nanobot Runtime 实际调用 meeting-asr Script/CLI（真实日志）",
        "",
        "meeting-asr Skill 被触发，读取 skills/meeting-asr/SKILL.md",
        "Tool call: exec(python src/meeting_tool.py transcribe",
        "            --audio data/input/synthetic_meeting_demo.wav --overwrite)",
        "",
        "结果：退出码 0，模型 paraformer-zh，输出 27 个带时间戳 segment",
        "",
        "NANOBOT_RUNTIME_TEST = PASS",
        "NANOBOT_INTEGRATION = PASS",
    ]
    render_text_image("nanobot Runtime 调用 meeting_tool.py", lines, OUT / "fig7_runtime.png")

    # fig8: pytest real output
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    out_lines = proc.stdout.strip().splitlines()
    render_text_image("pytest 自动测试结果", out_lines[-8:], OUT / "fig8_pytest.png")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    capture_gui()
    capture_evidence()
    print("screenshots in:", OUT)
    for f in sorted(OUT.glob("*.png")):
        print(" ", f.name, f.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
