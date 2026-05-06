# TOOLS.md — wiki-manager 工具速查

> Skills 定义工具的用法，这个文件记录 wiki-manager 专属的配置和速查。

---

## 本地工具脚本

工具位于 `tools/` 目录：

| 工具 | 用途 | 典型调用 |
|------|------|---------|
| `wiki_sync.py` | Wiki 文档拉取 | `python tools/wiki_sync.py` |
| `wiki_ingest.py` | 单篇知识编译 | `python tools/wiki_ingest.py <md_file>` |
| `wiki_ingest_batch.py` | 批量知识编译 | `python tools/wiki_ingest_batch.py <dir>` |
| `wiki_discover.py` | Wiki 文档发现 | `python tools/wiki_discover.py` |
| `base_sync.py` | Base 单表同步 | `python tools/base_sync.py <app_token> <table_id>` |
| `base_sync_all.py` | Base 全量同步 | `python tools/base_sync_all.py` |
| `build_graph.py` | 知识图谱构建 | `python tools/build_graph.py` |
| `clean_raw_lark.py` | 清理原始文档 | `python tools/clean_raw_lark.py` |
| `data_diff.py` | 数据变更检测 | `python tools/data_diff.py` |
| `scheduler.py` | 定时调度器 | `python tools/scheduler.py` |

### 知识编译链路速查

```bash
# 1. 拉取飞书 Wiki 文档
python tools/wiki_sync.py

# 2. 编译单篇文档
python tools/wiki_ingest.py workspace/raw_lark/wiki/项目\ OnePage.md

# 3. 批量编译
python tools/wiki_ingest_batch.py workspace/raw_lark/wiki/

# 4. 构建图谱
python tools/build_graph.py

# 5. 同步 Base 数据
python tools/base_sync_all.py
```

### 输出路径约定

```
项目根目录/
├── workspace/knowledge/wiki/                          # 全局知识底座
│   ├── index.md                   # 全局索引
│   ├── log.md                     # 同步日志
│   ├── public/                    # 公共知识
│   ├── dept/                      # 部门知识
│   ├── projects/                  # 项目知识
│   │   ├── kol-incubation/
│   │   ├── brand-ops/
│   │   └── ...
│   └── workspace/knowledge/graph/                     # 图谱相关
│       └── graph.json
├── workspace/knowledge/data/                          # 全局数据缓存
│   └── base_snapshot/
│       └── <项目>/
│           ├── <table>.json
│           └── <table>_meta.json
└── agents/wiki-manager/
    ├── workspace/raw_lark/        # 飞书原始文档
    ├── workspace/state/           # 状态文件
    │   └── sync_state.json
    └── workspace/config/          # 配置文件
        └── sources.yaml
```

---

## 环境路径

```
workspace/
├── workspace/knowledge/wiki/      → 知识库（全局共享，写入）
├── workspace/knowledge/data/      → 数据缓存（全局共享，写入）
├── workspace/knowledge/graph/     → 图谱数据（全局共享，写入）
├── tools/     → 工具脚本（软链接 → ../tools）
├── skills/    → OpenClaw Skills（软链接 → ../skills）
├── config/    → 配置文件（软链接 → ../config）
├── raw_lark/  → 原始文档（软链接 → ../raw_lark）
└── state/     → 状态文件（软链接 → ../state）
```

---

## 配置速查

### sources.yaml

定义 Wiki 拉取的 scope 和节点 token：

```yaml
scopes:
  public:
    node_token: xxx
  dept:
    node_token: xxx
  projects:
    kol-incubation:
      node_token: xxx
    brand-ops:
      node_token: xxx
```

### schema/*.yaml

定义 Base 同步的注册表：

```yaml
tables:
  - name: tasks
    app_token: xxx
    table_id: xxx
  - name: kpi
    app_token: xxx
    table_id: xxx
```
