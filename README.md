# AI Meeting ASR Agent

中文名称：**AI 会议语音转写与检索智能体**

《智能体开发实战》第 15 题：**AI 会议语音转写与检索**

本项目将一个会议音频文件通过 **FunASR** 转写为带时间戳的文字，并在此基础
上提供关键词检索、时间定位、自动会议摘要，最后以 **Skill + Script/CLI** 的
统一接口对外暴露，可被 nanobot 等 Agent Runtime 加载调用。

## 1. 项目简介

- 音频转写：调用 FunASR（`paraformer-zh` + `fsmn-vad` + `ct-punc`）把
  wav / mp3 / m4a 等会议录音转为带 `start_ms` / `end_ms` / `text` 的片段。
- 关键词检索：返回命中关键词、时间戳、对应句子及前后少量上下文。
- 时间定位：解析 `MM:SS`、`HH:MM:SS`、秒，支持“01:30 附近”与“5 分钟到 6 分钟”。
- 自动会议摘要：主题、概要、主要讨论点、决策事项、待办事项；无外部 LLM
  时使用本地抽取式 fallback，保证基础项目可运行。
- 自然语言 Router：规则式意图识别（transcribe / search / locate / summarize）。

## 2. 对应课程

《智能体开发实战》第 15 题“AI 会议语音转写与检索”，基础任务 4 项 + 可选
功能“自动会议摘要”均已实现。

## 3. 功能

| 功能 | 入口 | 说明 |
|------|------|------|
| 音频转写 | `transcribe` | FunASR 带时间戳转写 |
| 关键词检索 | `search` | 命中 + 时间戳 + 上下文 |
| 时间定位 | `locate` | 时间点 / 时间段 |
| 会议摘要 | `summarize` | 抽取式 fallback + 可选 LLM |
| 意图识别 | `route` | 自然语言规则路由 |

## 4. 系统架构

```
用户自然语言
    ↓
Agent / Router        (src/agent_router.py)
    ↓
SKILL.md              (统一 Skill 接口)
    ↓
meeting_tool CLI      (src/meeting_tool.py / cli/meeting_cli.py)
    ↓
┌ FunASR 转写 ├ Search Engine ├ Time Locator └ Summary Module
    ↓
结构化 JSON 输出
```

详见 [docs/系统架构.md](docs/系统架构.md)。

## 5. 目录结构

```
AI_Meeting_ASR_Project/
├─ README.md
├─ LICENSE_NOTICE.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
├─ SKILL.md
├─ skill/meeting-asr/SKILL.md
├─ src/                 # 核心实现
├─ cli/meeting_cli.py   # 自然语言入口
├─ app/streamlit_app.py # GUI
├─ tests/               # pytest 用例
├─ examples/            # 示例转写与命令
├─ data/input/          # 放置会议音频
├─ data/output/         # 转写结果输出
├─ logs/                # JSONL 运行日志
├─ docs/                # 课程文档
└─ scripts/             # 安装/运行脚本
```

## 6. 环境要求

- Python 3.10 ~ 3.12（本机验证：3.12.10）
- Windows 或 Linux
- 转写 mp3/m4a 等格式需要 ffmpeg（wav 可无 ffmpeg）
- 首次转写会从 ModelScope 下载模型（默认缓存 `~/.cache/modelscope`）

## 7. 安装

```bash
# Windows
scripts\setup_windows.bat

# Linux
bash scripts/setup_linux.sh
```

手动安装：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 8. FunASR 模型说明

- ASR：`paraformer-zh`（中文高精度非自回归 Paraformer）
- VAD：`fsmn-vad`（语音端点检测）
- 标点：`ct-punc`（标点恢复）

模型在首次 `transcribe` 时自动从 ModelScope 下载并缓存；本项目不重新训练、
不修改模型，仅作为库调用。参考开源项目：https://github.com/modelscope/FunASR

## 9. CLI 使用

```bash
# 转写（输出 JSON 到 data/output/<name>.json）
python src/meeting_tool.py transcribe --audio data/input/meeting.wav
python src/meeting_tool.py transcribe --audio data/input/meeting.wav --overwrite

# 检索
python src/meeting_tool.py search --transcript data/output/meeting.json --keyword "预算"
python src/meeting_tool.py search --transcript examples/demo_transcript.json --keyword "深度学习" --stats

# 时间定位
python src/meeting_tool.py locate --transcript data/output/meeting.json --time "01:30"

# 摘要
python src/meeting_tool.py summarize --transcript data/output/meeting.json
```

自然语言入口：

```bash
python cli/meeting_cli.py "搜索预算"
python cli/meeting_cli.py "01:30 附近说了什么"
python cli/meeting_cli.py "生成这次会议摘要"
```

成功退出码为 0，失败非 0 并输出含 `error` 字段的 JSON。更多示例见
[examples/example_commands.md](examples/example_commands.md)。

## 10. Streamlit 使用

```bash
scripts\run_web.bat
# 或
.venv\Scripts\python -m streamlit run app\streamlit_app.py
```

界面提供：上传/选择音频、开始转写、转写结果、关键词搜索、时间位置查询、
生成会议摘要、状态/错误提示。

## 11. Skill 使用

Skill 定义见 [SKILL.md](SKILL.md) 与 [skill/meeting-asr/SKILL.md](skill/meeting-asr/SKILL.md)。
Skill 通过真实 CLI 执行，而非 Prompt 模板。加载方式见
[docs/nanobot接入.md](docs/nanobot接入.md)。

## 12. nanobot 接入

见 [docs/nanobot接入.md](docs/nanobot接入.md)。本机未安装 nanobot 时无需大规模
改环境，Skill 已按规范提供，可按文档加载。

## 13. 测试方法

```bash
scripts\run_tests.bat
# 或
.venv\Scripts\python -m pytest -q
```

结果见 [docs/测试报告.md](docs/测试报告.md)。

## 14. 安全设计

- 文件白名单：仅允许读写 `data/input`、`data/output`、`logs`（只读 `examples`）。
- 防目录穿越：拒绝 `../`、项目外绝对路径（如 `C:\Windows\...`）。
- 覆盖确认：输出文件已存在时需 `--overwrite`。
- 日志脱敏：不记录 API Key / Token / 密码 / 音频内容。
- 不提供文件删除能力。

## 15. Token / 性能优化

“大会议文本检索结果压缩”：先由 Python 搜索、排序、截取命中前后上下文、
去重，仅把命中片段交给模型。实测（`examples/demo_transcript.json`，关键词
“深度学习”）：

- 估算 Token：360 → 125
- 压缩比：0.3472
- 减少：65.28%

用 `search --stats` 可实时查看 `compression_ratio` / `estimated_token_before`
/ `estimated_token_after` / `reduction_percent`，不虚构数据。

## 16. 已知问题

- 真实 FunASR 推理链路已用 3 段公开中文/英文语音验证通过
  （`REAL_ASR_TEST = "PASS"`，见 `PROJECT_STATUS.md` 与
  `docs/real_validation/`）；但“多人会议场景”尚未验证，需一段真实/模拟
  会议录音放入 `data/input/` 后运行转写。
- 未安装 ffmpeg 时，非 wav 格式无法转写（wav 不受影响）。
- 规则式摘要为抽取式，语义理解有限；配置外部 LLM 可进一步提升。

## 17. 开源依赖

- [FunASR](https://github.com/modelscope/FunASR)（MIT）
- PyTorch / torchaudio
- ModelScope
- Streamlit
- jieba
- pytest

详见 [LICENSE_NOTICE.md](LICENSE_NOTICE.md) 与 [docs/开源项目报告.md](docs/开源项目报告.md)。

## 18. License

本项目代码采用 MIT License；依赖的开源项目各自保留其许可证。
