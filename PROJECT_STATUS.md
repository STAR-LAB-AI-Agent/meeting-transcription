# 项目状态

更新时间：2026-09-21

## 状态总览

| 项目 | 状态 |
|------|------|
| 自动单元测试 | PASS（30 passed） |
| 真实 FunASR 推理链路 | PASS（3 段公开语音） |
| 真实会议场景 Demo | 待验证（需模拟多人会议录音） |
| nanobot 实际加载 | 未执行（本机未安装） |
| GitHub 发布 | 未执行（本机未安装 gh） |

## 环境

- Python 3.12.10
- funasr 1.4.16
- torch 2.14.0（CPU）
- torchaudio 2.11.0
- modelscope 1.40.1
- 模型：paraformer-zh（ASR）+ fsmn-vad（VAD）+ ct-punc（标点）

## 真实 FunASR 测试

使用 3 段公开官方示例语音完成真实推理（详情见
`docs/real_validation/audio_sources.md`）：

| 文件（basename） | 时长 | 段数 | 识别文本（节选） | 结果 |
|------------------|------|------|------------------|------|
| sample_01_clear_chinese.wav | 5.55s | 1 | 欢迎大家来体验达摩院推出的语音识别模型。 | PASS |
| sample_02_long_chinese.wav | 5.0s | 1 | 我认为跑步最重要的就是给我带来了身体健康。 | PASS |
| sample_03_challenging.wav | 2.23s | 1 | He tried to think how it could be.（英文） | PASS |

- 模型下载：首次运行自动下载并缓存到 `~/.cache/modelscope`。
- 转写耗时：约 47 秒/段（含模型从缓存加载；实际推理 RTF ≈ 0.12）。
- 搜索耗时：< 1 毫秒。
- 摘要耗时：约 350 毫秒（含 jieba 首次加载）。
- 输出目录：`data/output/`（每个音频对应 `.json` 与 `.txt`）。

## 真实检索 / 定位 / 摘要验证（主素材 sample_01）

- 关键词“语音识别”：命中 1 次，时间戳 880–5195 ms，返回对应句子。
- 关键词“模型”：命中 1 次。
- 关键词“量子火箭测试”（不存在）：`hit_count: 0`，友好返回空结果。
- 时间定位“00:02”：定位到该片段，`out_of_range: false`。
- 摘要：输出 topic/summary/key_points；decisions 与 action_items 均为空，
  并明确标注“未识别到明确决策事项/待办”，未编造内容。

## Token 优化说明

真实短音频（单句、单 segment）无冗余文本，压缩比约为 1（因时间戳前缀甚至
略增），这是真实结果。有意义的“大会议文本检索结果压缩”演示使用多段示例
转写（14 段）：关键词“深度学习”估算 Token 360 → 125，减少 65.28%（真实
计算，见 `docs/测试报告.md`）。

## WER / CER

未评估。下载素材没有人工逐字标注的 ground truth，因此不伪造 WER/CER。

## 待完成

1. 会议场景 Demo：需一段真实/模拟多人会议录音（放入 `data/input/`）。
2. nanobot 实际加载：需用户安装 nanobot 后按 `docs/nanobot接入.md` 操作。
3. GitHub 发布：需用户安装并登录 gh CLI 后执行发布命令。
