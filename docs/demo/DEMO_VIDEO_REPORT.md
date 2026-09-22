# Demo 视频说明

## Video

- 文件：`docs/demo/AI_Meeting_ASR_Demo.mp4`
- 原始录制：`docs/demo/recording_raw.webm`（Playwright 原始 VP8）
- Duration：55.56 秒
- Resolution：1280×720
- Codec：H.264（yuv420p，+faststart，浏览器/手机可播放）
- File size：约 1.31 MB

## Recording method

使用 Playwright（Chromium headless，`scripts/record_demo.py`）自动打开本地
Streamlit（http://localhost:8501）并真实操作，同时录制浏览器 viewport；随后用
ffmpeg 将原始 webm 转为 H.264 MP4。全程为真实程序操作，非静态截图拼接。

## Demo audio

`data/input/synthetic_meeting_demo.wav`（67.5 秒，16kHz mono PCM16）。
注意：该文件是 TTS 合成的**模拟会议**素材，不是私人真实会议数据。

## 演示内容

- Transcription：真实调用 FunASR（paraformer-zh + fsmn-vad + ct-punc），
  产出带时间戳的 27 段 transcript。
- Keyword：搜索“预算”，展示真实命中与上下文。
- Time locate：定位“00:30”，展示 00:30 附近会议内容。
- Summary：真实生成会议摘要（topic/summary/key_points/decisions/action_items）。

## Validation

- 文件存在、大小 > 0。
- ffprobe 可读取：H.264 / 1280×720 / 25fps / 55.56s。
- 抽帧 5 张（10%/30%/50%/70%/90%）到 `docs/demo/frames/`：均非黑帧、均含文本
  （暗色文字像素 1.1w~2.1w，亮度标准差 24~32），覆盖标题/转写/检索/定位/摘要。

## 结论

`DEMO_VIDEO = PASS`
