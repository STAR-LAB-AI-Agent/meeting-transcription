---
name: meeting-asr
description: >-
  AI 会议语音转写与检索智能体。用于把会议音频转写为带时间戳文字、搜索会议
  关键词并返回时间戳与上下文、查找某个时间点附近的会议内容、以及生成会议
  摘要（主题/讨论点/决策/待办）。当用户要求“转写会议音频”“搜索会议关键词”
  “查找某时间点说了什么”“生成会议摘要”时调用本 Skill。通过真实 Script/CLI
  （src/meeting_tool.py）执行，不依赖 Prompt 模板。
---

# meeting-asr：AI 会议语音转写与检索智能体

## 何时调用

- 把会议音频转写为带时间戳文字；
- 按关键词搜索会议内容（返回命中时间戳与前后上下文）；
- 查找某个时间点/时间段附近的会议内容；
- 自动生成会议摘要。

## 何时不调用

- 与会议语音无关的任务；
- 访问项目目录之外的文件；
- 删除文件；
- 需要 API Key / 密码等敏感凭据的操作（本 Skill 不包含、也不索取任何凭据）。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| audio | path | 转写时 | 音频文件，需位于 data/input/ |
| transcript | path | 检索/定位/摘要时 | 转写 JSON，位于 data/output/ 或 examples/ |
| keyword | string | 检索时 | 关键词 |
| time | string | 定位时 | MM:SS / HH:MM:SS / 秒 |

## Script/CLI 调用命令

```bash
# 转写
python src/meeting_tool.py transcribe --audio data/input/synthetic_meeting_demo.wav

# 搜索关键词
python src/meeting_tool.py search --transcript data/output/synthetic_meeting_demo.json --keyword "预算"

# 查找时间点
python src/meeting_tool.py locate --transcript data/output/synthetic_meeting_demo.json --time "00:30"

# 生成摘要
python src/meeting_tool.py summarize --transcript data/output/synthetic_meeting_demo.json
```

成功时退出码为 0 并输出 JSON；失败时退出码非 0，输出含 `error` 字段的 JSON。

## 输出格式

- 转写：`{"audio_file", "model", "segments": [{"start_ms", "end_ms", "text"}]}`
- 搜索：`{"keyword", "hit_count", "hits": [{"start_ms", "end_ms", "sentence", "context_before", "context_after"}]}`
- 定位：`{"target_ms", "target_time", "out_of_range", "segments"}`
- 摘要：`{"topic", "summary", "key_points", "decisions", "action_items", "notes"}`

## 安全边界

- 仅读写 data/input、data/output、logs（只读 examples）。
- 拒绝目录穿越与项目外绝对路径。
- 日志脱敏，不记录敏感凭据与音频内容。

## 例子

### 例子 1：转写并搜索

用户：“把 data/input/synthetic_meeting_demo.wav 转写，然后搜索‘预算’。”

```bash
python src/meeting_tool.py transcribe --audio data/input/synthetic_meeting_demo.wav
python src/meeting_tool.py search --transcript data/output/synthetic_meeting_demo.json --keyword "预算"
```

### 例子 2：定位与摘要

用户：“00:30 附近说了什么？再生成会议摘要。”

```bash
python src/meeting_tool.py locate --transcript data/output/synthetic_meeting_demo.json --time "00:30"
python src/meeting_tool.py summarize --transcript data/output/synthetic_meeting_demo.json
```
