# 示例命令

> 以下命令在项目根目录执行。示例音频请放入 `data/input/`。

## 1. 音频转写

```bash
python src/meeting_tool.py transcribe --audio data/input/demo.wav
python src/meeting_tool.py transcribe --audio data/input/demo.wav --markdown
```

## 2. 关键词检索

```bash
python src/meeting_tool.py search --transcript examples/demo_transcript.json --keyword "预算"
python src/meeting_tool.py search --transcript examples/demo_transcript.json --keyword "深度学习" --stats
```

## 3. 时间定位

```bash
python src/meeting_tool.py locate --transcript examples/demo_transcript.json --time "01:30"
```

## 4. 会议摘要

```bash
python src/meeting_tool.py summarize --transcript examples/demo_transcript.json
```

## 5. 自然语言入口

```bash
python cli/meeting_cli.py "搜索预算"
python cli/meeting_cli.py "01:30 附近说了什么"
python cli/meeting_cli.py "生成这次会议摘要"
python cli/meeting_cli.py "帮我转写这个会议录音"
```
