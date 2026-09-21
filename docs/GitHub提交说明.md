# GitHub 提交说明

本机已初始化本地 Git 仓库并完成若干逻辑清晰的 commit。以下说明后续公开发布
所需步骤。

## 1. 本地仓库状态

- 已执行 `git init`。
- 已配置 `.gitignore`，忽略 `.venv`、`__pycache__`、模型缓存、真实音频、
  转写产物、`.env`、日志等。
- 已按逻辑拆分 commit（结构初始化、FunASR 转写 CLI、检索与时间定位、
  Skill 与 Router、测试与安全、文档与 GUI）。

## 2. 公开发布前检查

确认仓库中**不包含**：

- API Key / 密码 / Token（`.env.example` 仅含空占位符）
- 私人音频（`data/input/` 已忽略）
- 私人路径或本机绝对路径
- 大模型缓存

## 3. 发布步骤（用户本人完成）

若本机 GitHub CLI 已登录：

```bash
gh repo create AI_Meeting_ASR_Project --public --source . --push
```

或手动：

```bash
git remote add origin https://github.com/<你的用户名>/AI_Meeting_ASR_Project.git
git branch -M main
git push -u origin main
```

> 公开发布前请再次确认账号登录状态与仓库内容，未经确认不擅自公开。
