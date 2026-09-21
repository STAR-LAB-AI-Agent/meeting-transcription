# nanobot 接入说明

本机当前未安装 nanobot。为不破坏现有环境，本实验未大规模安装 nanobot，
而是保证 Skill 接口规范，并提供后续加载方式。

## 1. Skill 接口规范

本项目的 Skill 已按“元数据 + 指令 + CLI 调用”的规范编写：

- 根目录：`SKILL.md`
- 打包副本：`skill/meeting-asr/SKILL.md`

SKILL.md 包含 `name`、`description`、使用场景、输入参数、输出格式、CLI 命令、
失败处理、安全边界和 2 个完整例子。Skill 通过真实 CLI 执行：

```bash
python src/meeting_tool.py transcribe --audio data/input/demo.wav
python src/meeting_tool.py search --transcript examples/demo_transcript.json --keyword "预算"
python src/meeting_tool.py locate --transcript examples/demo_transcript.json --time "01:30"
python src/meeting_tool.py summarize --transcript examples/demo_transcript.json
```

## 2. 加载到 nanobot

若后续安装 nanobot，通常只需把 Skill 目录复制（或链接）到 nanobot 的 Skill
目录，例如：

```text
<nanobot_home>/skills/meeting-asr/SKILL.md
```

然后把 CLI 的可执行路径（`src/meeting_tool.py` 或 `cli/meeting_cli.py`）在
SKILL.md 中保持为项目内相对/绝对路径即可。Agent Runtime 读取 SKILL.md 后，
会按其中的命令调用本项目的 Script/CLI。

## 3. 实际接入检查（如本机已安装 nanobot）

1. 找到 nanobot 的 Skill 目录（例如 `$HOME/.nanobot/skills` 或类似位置）。
2. 查看其现有 SKILL.md 的字段格式，确认与本项目 `name` / `description` /
   `input` / `output` 字段对齐。
3. 复制 `skill/meeting-asr/` 到该目录，重载 nanobot。
4. 运行一条自然语言指令验证，例如“搜索预算”。

> 若 nanobot 使用 JSON/YAML 的 Skill 清单格式，则在其清单中登记
> `name=meeting-asr`，`command=python src/meeting_tool.py`，并把参数透传
> 给子命令即可。

## 4. 结论

本实验已提供规范 SKILL.md 与可独立运行的 Script/CLI，满足“可被 Agent
Runtime 加载调用”的接口要求。待用户安装 nanobot 后，按第 2、3 节即可真实
接入并测试。
