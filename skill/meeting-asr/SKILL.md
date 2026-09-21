---
name: meeting-asr
description: >-
  AI 会议语音转写与检索智能体。将会议音频（wav/mp3/m4a 等）转写为带时间戳
  的文字，支持关键词检索、时间点/时间段定位、自动会议摘要，并通过
  Script/CLI 接口供 Agent Runtime（如 nanobot）调用。
---

# AI 会议语音转写与检索智能体（meeting-asr）

这是可被 Agent Runtime 加载的 Skill 副本，与项目根目录 `SKILL.md` 内容一致。

## 使用场景

1. 把会议音频转写成带时间戳的文字；
2. 按关键词检索会议内容并定位到对应时间点；
3. 查询某个时间点（或时间段）附近说了什么；
4. 自动生成会议摘要。

## 何时调用 / 何时不调用

- 调用：指令含“转写 / 转录 / 识别 / 搜索 / 查询 / 查找 / 提到 / 定位 /
  附近 / 摘要 / 总结 / 纪要”等意图词，对象是会议音频或转写结果。
- 不调用：与语音/会议无关的任务；处理项目目录之外的文件；删除文件。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audio` | path | 转写时必填 | `data/input/` 下的音频 |
| `transcript` | path | 检索/定位/摘要时必填 | 转写 JSON |
| `keyword` | string | 检索时必填 | 关键词 |
| `time` | string | 定位时必填 | `MM:SS` / `HH:MM:SS` / 秒 |

## 输出格式

转写结果（JSON）：

```json
{
  "audio_file": "demo.wav",
  "model": "paraformer-zh",
  "segments": [{"start_ms": 1000, "end_ms": 5200, "text": "..."}],
  "metadata": {}
}
```

检索结果返回 `keyword`、`hit_count` 与 `hits`（含时间戳、句子、前后上下文）。

## Script/CLI 调用命令

```bash
python src/meeting_tool.py transcribe --audio data/input/demo.wav
python src/meeting_tool.py search --transcript examples/demo_transcript.json --keyword "预算"
python src/meeting_tool.py locate --transcript examples/demo_transcript.json --time "01:30"
python src/meeting_tool.py summarize --transcript examples/demo_transcript.json
```

自然语言入口：

```bash
python cli/meeting_cli.py "搜索预算"
```

成功退出码 0，失败非 0 并输出含 `error` 的 JSON。

## 失败处理

- FunASR 未安装：提示运行安装脚本。
- 缺少 ffmpeg：给出 Windows 安装说明。
- 输出文件已存在：提示 `--overwrite`。
- 越权路径：安全层拒绝。

## 安全边界

- 仅允许读写 `data/input`、`data/output`、`logs`（只读 `examples`）。
- 拒绝目录穿越与项目外绝对路径。
- 日志脱敏，不记录敏感凭据与音频内容。
- 不提供删除能力。

## 完整例子

### 例子 1

用户：“把 meeting.wav 转成文字，然后搜索‘预算’。”

```bash
python src/meeting_tool.py transcribe --audio data/input/meeting.wav
python src/meeting_tool.py search --transcript data/output/meeting.json --keyword "预算"
```

### 例子 2

用户：“01:30 附近说了什么？再生成摘要。”

```bash
python src/meeting_tool.py locate --transcript data/output/meeting.json --time "01:30"
python src/meeting_tool.py summarize --transcript data/output/meeting.json
```
