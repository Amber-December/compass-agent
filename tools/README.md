# 环境搭建工具（tools/）

本目录存放**比赛环境搭建相关的工具脚本**，不属于机器人核心功能代码，**不提交到 Git 仓库**。

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `generate_mock_env.py` | 模拟企业环境生成器：批量创建飞书文档、生成任务/日历/看板模拟数据 |

---

## 使用流程

### Step 1: 确认飞书应用权限

在飞书开发者后台开通以下权限：
- `docx:document:write` — 创建文档
- `wiki:space:write` — 创建知识空间（可选）
- `drive:drive:write` — 创建文件夹（可选）

然后**重新发布应用版本**。

### Step 2: 运行脚本

```bash
cd /Users/amber/lark-knowledge-agent
python tools/generate_mock_env.py
```

### Step 3: 验证数据

- 飞书 Wiki 知识库应出现「研发二部知识库」及下属文档
- `data/raw/` 目录应出现 JSON 文件

### Step 4: 开始开发机器人

环境搭建完成后，即可启动 OpenClaw Agent 进行效能分析。

---

## 注意

- 本脚本**一次性执行**，不需要重复运行
- 如需重置环境，手动删除飞书文档后重新运行
- 生成的 `data/raw/*.json` 也不进 git（已在 `.gitignore` 中排除）
