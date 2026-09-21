# nanobot 接入说明

## 1. 已完成的接入工作

- nanobot 已安装在独立环境，未污染 FunASR 环境：
  - 安装位置：`E:\tb\20260921\nanobot_runtime\.venv`
  - 版本：nanobot 0.3.5
  - Python：3.12.10
- 项目内 canonical workspace skill：`skills/meeting-asr/SKILL.md`
- 旧路径 `skill/meeting-asr/SKILL.md` 保留作为课程历史兼容。
- 已验证 nanobot 的 `SkillsLoader` 能发现 `meeting-asr`（证据见
  `docs/real_validation/nanobot_skill_discovery.txt`）。

## 2. nanobot Skill 发现机制

nanobot 从 `<workspace>/skills/<skill-name>/SKILL.md` 发现 workspace skill。
以本项目为 workspace（`E:\tb\20260921\AI_Meeting_ASR_Project`）时，发现路径为：

```text
E:\tb\20260921\AI_Meeting_ASR_Project\skills\meeting-asr\SKILL.md
```

SKILL.md 使用 YAML frontmatter，至少包含 `name` 与 `description`。本项目
`description` 覆盖四类意图（转写会议音频 / 搜索会议关键词 / 查找某时间点 /
生成会议摘要），并说明通过 `src/meeting_tool.py` 真实执行，而非 Prompt 模板。
Skill 不包含任何 API Key。

## 3. 模型配置（provider / model）

nanobot 需要 provider + model + API Key。支持多种 provider，通过环境变量注入
Key（示例，按你实际使用的 provider 选择其一）：

```powershell
$env:ANTHROPIC_API_KEY = "..."   # Anthropic
$env:OPENAI_API_KEY = "..."      # OpenAI / Azure / OpenRouter 等
$env:DEEPSEEK_API_KEY = "..."    # DeepSeek
$env:DASHSCOPE_API_KEY = "..."   # 阿里云百炼
$env:MOONSHOT_API_KEY = "..."    # Moonshot
```

初始化配置：

```powershell
E:\tb\20260921\nanobot_runtime\.venv\Scripts\nanobot.exe onboard --wizard `
  --workspace E:\tb\20260921\AI_Meeting_ASR_Project `
  --config C:\Users\<you>\.nanobot\config.json
```

或在 WebUI（`nanobot webui`）的 Settings → Models 中配置。

> 不要把 API Key 写入本项目、README、日志或 Git；Key 只放在环境变量或
> 个人配置文件中。

## 4. Runtime 调用验证（待模型配置后执行）

使用非交互式命令，让 Agent 自然语言 → 识别 Skill → 调用 Script/CLI：

```powershell
E:\tb\20260921\nanobot_runtime\.venv\Scripts\nanobot.exe agent `
  --message "请使用会议语音转写能力转写 data/input/synthetic_meeting_demo.wav" `
  --workspace E:\tb\20260921\AI_Meeting_ASR_Project `
  --config C:\Users\<you>\.nanobot\config.json
```

其余三条：搜索“预算”、查询“00:30 附近说了什么”、生成会议摘要。
验证目标：确认 nanobot 触发 `meeting-asr` Skill → 执行 `src/meeting_tool.py` →
返回真实脚本结果（退出码 0），而非 Agent 凭提示词编造答案。

## 5. 安全边界

- Skill 不包含、不索取任何 API Key / 密码 / Token。
- 通过 `src/security.py` 限制文件读写白名单与目录穿越。
- nanobot 独立 venv 与本项目 FunASR venv 隔离。
