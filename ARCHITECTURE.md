# Compass 多 Agent 架构说明

## 目录结构

```
~/lark-knowledge-agent/
├── .openclaw/                    # OpenClaw 状态目录（运行时）
│   └── agents/
│       ├── main/                 # 默认 Agent（当前活跃）
│       ├── qa-bot/               # 问答 Agent（待命）
│       └── wiki-manager/         # 同步 Agent（待命）
│
├── agents/                       # Agent 工作目录（代码+配置）
│   ├── qa-bot/                   # ✅ 已迁移完成
│   │   ├── workspace/            # 工作空间（OpenClaw 运行时 cwd）
│   │   │   ├── data -> ../../workspace/data
│   │   │   ├── graph -> ../../workspace/graph
│   │   │   ├── wiki -> ../../workspace/wiki
│   │   │   ├── tools -> ../tools        # 软链：工具脚本
│   │   │   └── skills -> ../skills      # 软链：OpenClaw Skills
│   │   ├── agent.json            # Agent 配置
│   │   ├── prompts/              # 提示词
│   │   ├── skills/               # OpenClaw Skills（实际目录）
│   │   │   ├── data-query/
│   │   │   ├── graph-query/
│   │   │   ├── intent/
│   │   │   ├── query/
│   │   │   └── route/
│   │   ├── tools/                # 可执行脚本（实际目录）
│   │   │   ├── data_query.py
│   │   │   ├── graph_query.py
│   │   │   └── wiki_query.py
│   │   └── README.md
│   │
│   └── wiki-manager/             # ✅ 已迁移完成
│       ├── workspace/            # 工作空间（OpenClaw 运行时 cwd）
│       │   ├── data -> ../../workspace/data
│       │   ├── graph -> ../../workspace/graph
│       │   ├── wiki -> ../../workspace/wiki
│       │   ├── tools -> ../tools        # 软链：工具脚本
│       │   ├── skills -> ../skills      # 软链：OpenClaw Skills
│       │   ├── config -> ../config      # 软链：配置文件
│       │   ├── raw_lark -> ../raw_lark  # 软链：原始文档
│       │   └── state -> ../state        # 软链：状态文件
│       ├── agent.json            # Agent 配置
│       ├── config/
│       ├── prompts/
│       ├── raw_lark/
│       ├── skills/
│       ├── state/
│       ├── tools/
│       └── workflow.json
│
└── workspace/                    # 全局共享资源
    ├── SOUL.md
    ├── AGENTS.md
    ├── MEMORY.md
    ├── wiki/                     # 知识底座（全局）
    ├── data/                     # 数据缓存（全局）
    └── graph/                    # 图谱数据（全局）
```

## 关键设计

### 1. Workspace 是运行时 CWD
- **OpenClaw 运行时**，Agent 的当前工作目录是 `workspace/`
- **工具脚本** 和 **Skills** 通过软链接在 workspace 内可访问
- **全局资源**（wiki/data/graph）也通过软链接共享

### 2. 实际目录 vs 软链接
- **实际目录**：`tools/`、`skills/`、`config/`、`raw_lark/`、`state/`
- **软链接**：workspace 内的 `tools -> ../tools`、`skills -> ../skills` 等

### 3. 为什么这样设计？
1. **职责分离**：代码/配置在 workspace 外，运行时数据在 workspace 内
2. **OpenClaw 兼容**：workspace 是 OpenClaw 的默认 cwd，工具需要从内部访问
3. **全局共享**：多个 Agent 共享 `workspace/wiki/`、`workspace/data/`、`workspace/graph/`
4. **独立运行**：每个 Agent 可以在自己的目录下独立运行工具

## 路径查找机制

### wiki-manager 工具
- **运行目录**：`agents/wiki-manager/workspace/`（通过软链接）
- **路径逻辑**：基于 `AGENT_DIR`（当前目录的父目录）
- **读取**：`config/sources.yaml`、`state/sync_state.json`

### qa-bot 工具
- **运行目录**：`agents/qa-bot/workspace/`（通过软链接）
- **路径逻辑**：向上查找包含 `openclaw.json` 的目录
- **读取**：`wiki/`、`data/`、`graph/`（通过软链接）

## 使用方式

### 1. 通过 OpenClaw 运行（推荐）
```bash
# OpenClaw 会自动切换到 workspace 目录
cd ~/lark-knowledge-agent
./start-gateway.sh
```

### 2. 直接调用工具（调试）
```bash
# 从 workspace 内部调用
cd ~/lark-knowledge-agent/agents/qa-bot/workspace
python tools/wiki_query.py "问题" --scope kol-incubation --json

# 或从 Agent 根目录调用
cd ~/lark-knowledge-agent/agents/qa-bot
python tools/wiki_query.py "问题" --scope kol-incubation --json
```

### 3. 在 OpenClaw Skill 中使用
```python
# Skill 运行时，当前目录是 workspace/
# 可以直接访问 tools/ 和 skills/
result = query_wiki("问题", scope="kol-incubation")
context = result["context"]
```

## 注意事项

1. **不要删除软链接**：workspace 内的软链接是运行时必需的
2. **修改实际目录**：编辑 `tools/`、`skills/` 等实际目录，软链接会自动同步
3. **全局资源在 workspace/**：`wiki/`、`data/`、`graph/` 是所有 Agent 共享的
4. **Agent 独立运行**：每个 Agent 可以在自己的 workspace 下独立运行工具

## 验证命令

```bash
# 验证 qa-bot 结构
ls -la ~/lark-knowledge-agent/agents/qa-bot/workspace/

# 验证 wiki-manager 结构
ls -la ~/lark-knowledge-agent/agents/wiki-manager/workspace/

# 测试从 workspace 内部运行工具
cd ~/lark-knowledge-agent/agents/qa-bot/workspace
python tools/wiki_query.py "垂类达人孵化的粉丝增长率" --scope kol-incubation --json
```
