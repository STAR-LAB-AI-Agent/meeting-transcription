---
name: meeting-asr
description: >-
  AI 会议语音转写与检索智能体。将会议音频（wav/mp3/m4a 等）转写为带时间戳
  的文字，支持关键词检索、时间点/时间段定位、自动会议摘要，并通过
  Script/CLI 接口供 Agent Runtime（如 nanobot）调用。
---

# AI 会议语音转写与检索智能体（meeting-asr）

## 使用场景

当用户需要对会议录音做以下任一件事时调用本 Skill：

1. 把会议音频转写成带时间戳的文字；
2. 按关键词检索会议内容并定位到对应时间点；
3. 查询某个时间点（或时间段）附近说了什么；
4. 自动生成会议摘要（主题、讨论点、决策、待办）。

## 何时调用 / 何时不调用

- 调用：指令中包含“转写 / 转录 / 识别 / 搜索 / 查询 / 查找 / 提到 /
  定位 / 附近 / 摘要 / 总结 / 纪要”等意图词，且对象是会议音频或转写结果。
- 不调用：与语音/会议无关的通用任务；处理非本项目目录内文件；要求删除文件；
  需要访问项目目录之外路径的操作。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audio` | path | 转写时必填 | 音频路径，需位于 `data/input/` |
| `transcript` | path | 检索/定位/摘要时必填 | 转写 JSON 路径 |
| `keyword` | string | 检索时必填 | 关键词 |
| `time` | string | 定位时必填 | `MM:SS` / `HH:MM:SS` / 秒 |
| `overwrite` | bool | 否 | 是否覆盖已有输出 |

## 输出格式

转写结果（JSON）：

```json
{
  "audio_file": "demo.wav",
  "model": "paraformer-zh",
  "segments": [
    {"start_ms": 1000, "end_ms": 5200, "text": "..."}
  ],
  "metadata": {}
}
```

检索结果包含 `keyword`、`hit_count` 与 `hits`（每条含 `start_ms`、
`end_ms`、`sentence`、`context_before`、`context_after`），并只返回命中
片段及其少量上下文，不返回整份长文本。

## Script/CLI 调用命令

本 Skill 通过真实 Script/CLI 执行，不依赖 Prompt 模板：

```bash
# 转写
python src/meeting_tool.py transcribe --audio data/input/demo.wav

# 检索
python src/meeting_tool.py search --transcript examples/demo_transcript.json --keyword "预算"

# 时间定位
python src/meeting_tool.py locate --transcript examples/demo_transcript.json --time "01:30"

# 摘要
python src/meeting_tool.py summarize --transcript examples/demo_transcript.json
```

自然语言入口：

```bash
python cli/meeting_cli.py "搜索预算"
```

成功时退出码为 0，失败时返回非 0 并在 stdout 输出包含 `error` 字段的 JSON。

## 失败处理

- FunASR 未安装：提示先运行 `scripts/setup_windows.bat` 或
  `pip install funasr`，返回非 0。
- 缺少 ffmpeg（mp3/m4a 等格式）：给出 Windows 安装说明，返回非 0。
- 输出文件已存在：提示使用 `--overwrite`，返回非 0。
- 越权路径：被安全层拒绝，返回非 0。

## 安全边界

- 仅允许读写 `data/input`、`data/output`、`logs`（以及只读 `examples`）。
- 拒绝目录穿越与项目外绝对路径。
- 日志脱敏，不记录 API Key / Token / 密码 / 音频内容。
- 不提供文件删除能力。

## 完整例子

### 例子 1：转写并检索

用户：“把 data/input/meeting.wav 转成带时间戳文字，然后搜索‘预算’。”

```bash
python src/meeting_tool.py transcribe --audio data/input/meeting.wav
python src/meeting_tool.py search --transcript data/output/meeting.json --keyword "预算"
```

### 例子 2：时间定位 + 摘要

用户：“01:30 附近说了什么？再给我一份会议摘要。”

```bash
python src/meeting_tool.py locate --transcript data/output/meeting.json --time "01:30"
python src/meeting_tool.py summarize --transcript data/output/meeting.json
```

更多说明见 [README.md](README.md) 与 [docs/nanobot接入.md](docs/nanobot接入.md)。
