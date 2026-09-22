# 项目状态

更新时间：2026-09-22

## 状态总览

| 项目 | 状态 |
|------|------|
| 自动单元测试 | PASS（30 passed） |
| 真实 FunASR 推理链路（公开短音频） | PASS（3/3） |
| 合成模拟会议 Demo（60~90s） | PASS（67.5s） |
| 合成会议 CER（演示级） | 4.91%（13/265 字符） |
| nanobot 安装 | PASS（v0.3.5，独立 venv） |
| nanobot Skill 发现 | PASS（meeting-asr 被加载） |
| nanobot Runtime 实际调用 | PASS（transcribe/search/locate/summarize 均真实调用 CLI） |
| GUI | PASS（人工最终验收通过） |
| GitHub CLI | 已安装（2.101.0）并登录（Simon-91-lxs） |
| GitHub 发布 | PASS（https://github.com/STAR-LAB-AI-Agent/meeting-transcription，public，main） |
| Demo 视频 | PASS（docs/demo/AI_Meeting_ASR_Demo.mp4，55.6s，1280×720 H.264） |

## 环境

- Python 3.12.10
- funasr 1.4.16 / torch 2.14.0(CPU) / torchaudio 2.11.0 / modelscope 1.40.1
- 模型：paraformer-zh（ASR）+ fsmn-vad（VAD）+ ct-punc（标点）
- 转写支持句级时间戳（`generate(..., sentence_timestamp=True)`）
- TTS 工具：edge-tts 7.2.8 + miniaudio（独立 venv `E:\tb\20260921\tts_tool\.venv`）
- nanobot 0.3.5（独立 venv `E:\tb\20260921\nanobot_runtime\.venv`）

## 三类语音验证（明确区分，未互相冒充）

### 1. FunASR 官方公开短音频（真实推理）

3/3 decode PASS，详情见 `docs/real_validation/audio_sources.md`：

| 文件 | 时长 | 识别文本 |
|------|------|----------|
| sample_01_clear_chinese.wav | 5.55s | 欢迎大家来体验达摩院推出的语音识别模型。 |
| sample_02_long_chinese.wav | 5.0s | 我认为跑步最重要的就是给我带来了身体健康。 |
| sample_03_challenging.wav | 2.23s | He tried to think how it could be.（英文） |

### 2. 合成模拟会议 Demo（60~90s，非真实会议）

- 音频：`data/input/synthetic_meeting_demo.wav`（67.5s，16kHz mono PCM16）
- 由 TTS 合成，明确标记为“合成模拟会议音频”，非真实会议录音。
- 生成脚本：`scripts/generate_synthetic_meeting.py`
- 人工原文：`examples/synthetic_meeting_ground_truth.txt`
- 转写输出：`data/output/synthetic_meeting_demo.json` / `.txt`（27 段，时间戳单调）
- 检索/定位/摘要结果：`docs/real_validation/synth_*.json`
- 演示级 CER：4.91%（合成会议识别结果，非模型 benchmark）

### 3. nanobot Runtime（已真实验证）

- 安装：nanobot 0.3.5（独立 venv）
- Skill：`skills/meeting-asr/SKILL.md`（canonical workspace skill）
- 发现：`SkillsLoader` 已识别 `meeting-asr`（证据见
  `docs/real_validation/nanobot_skill_discovery.txt`）
- 模型：deepseek-flash（provider/model 已配置，`nanobot status` 显示 ready）
- 实际调用 Script/CLI：**PASS**。四项均通过 `meeting-asr` Skill 触发真实
  `src/meeting_tool.py`（transcribe/search/locate/summarize），证据见
  `docs/real_validation/nanobot_runtime_*.txt`

> 说明：nanobot Agent 为完成 transcribe，自动在系统 Python 中安装了
> funasr/modelscope（torch 2.2.2+cu118），因此本次转写元数据记录为
> torch 2.2.2+cu118；项目 `.venv` 内仍为 torch 2.14.0(CPU)。两者均为真实
> 推理，仅运行环境不同。

## WER / CER 说明

- 公开短音频：未评估（无人工逐字 ground truth）。
- 合成会议：CER=4.91%，仅作为“合成会议 Demo 识别结果”演示，不是模型性能
  benchmark。

## GitHub 发布

- 组织：STAR-LAB-AI-Agent
- 仓库：meeting-transcription
- URL：https://github.com/STAR-LAB-AI-Agent/meeting-transcription
- 账号：Simon-91-lxs（外部合作者，viewerPermission = WRITE）
- 可见性：public；默认分支：main
- 提交数：19（作者为匿名 "Student"）
- 发布后数据（真实查询）：Star 0 / Fork 0 / Watch 0 / PR 0

## 待完成

无（GitHub 组织仓库发布已完成）。
