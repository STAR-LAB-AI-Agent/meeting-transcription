# License Notice

本项目 `AI Meeting ASR Agent` 的代码采用 MIT License 发布（详见仓库
LICENSE 文件，如未单独提供则默认 MIT）。

本项目核心依赖并调用了以下开源项目，其版权归各自作者所有：

## FunASR

- 项目名称：FunASR（A Fundamental End-to-End Speech Recognition Toolkit）
- 官方仓库：https://github.com/modelscope/FunASR
- 使用版本：1.4.16
- License：MIT License（Copyright (c) 2025 FunASR）
- 本项目用途：通过 `AutoModel` 加载 `paraformer-zh`（ASR）、`fsmn-vad`
  （语音端点检测）与 `ct-punc`（标点恢复）模型，完成会议音频的带时间戳
  转写。本项目未修改、未重新训练 FunASR 模型，仅作为库调用。

## 其它主要依赖

- PyTorch（BSD-style License）
- torchaudio（BSD-style License）
- ModelScope（Apache License 2.0）
- Streamlit（Apache License 2.0）
- pytest（MIT License）

各依赖的完整许可证文本以其官方发布为准。
