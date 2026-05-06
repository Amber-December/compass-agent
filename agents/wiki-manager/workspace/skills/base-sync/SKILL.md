---
name: base-sync
description: "base-sync"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 飞书 Base 增量同步 Skill — 检测变更并拉取新增/修改的多维表格数据

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/base-sync/`
- **执行脚本**: `tools/base_sync.py`、`tools/base_sync_all.py`

## 触发条件

- 定时：每周一 8:30 全量同步，每 6 小时增量检查
- 手动：用户说 "同步 Base" / "刷新数据" 时触发
- 被 wiki-sync 联动触发（Wiki 同步完成后自动检查 Base）

## 核心能力

1. **读取配置** — 从 `config/sources.yaml` 获取：
   - 7 个 Base 的 token 和表格列表
   - mcn: SZ1Cb3RbbabNJLsr6TpcJPEfn2g
   - brand-ops: J99JbkE9eaEK97sMGfEcSG8UnLd
   - kol-incubation: LTLNbBlGTaB4mNs6by0cvhPhnib
   - live-commerce: KFnUbyA0jaSXcrsHuENcY9gBnJe
   - private-domain: WKOXb2zm7a1XIFseYMmcYl4znJn
   - short-video: X8o0b9M9ZaSk0asVcr4ceF16neg
   - virtual-ip: FeyIbsjrNa7pPksOqXmcE7ZMnff

2. **检测变更** — 对比 sync_state.json 中的 content_hash：
   - hash 相同 → 跳过
   - hash 不同 / 新表 → 拉取

3. **拉取数据** — 通过 lark-cli 调用飞书 Base API：
   ```bash
   lark-cli base +record-list --base-token <token> --table-id <table_name> --as user --profile compass
   ```

4. **规范化处理** — 展平嵌套字段、统一日期格式、空值处理

5. **保存数据** — 写入 `workspace/knowledge/data/`（项目根目录下的共享知识目录）：
   - `<table>.json` — 数组对象格式 [{field: value, ...}, ...]
   - `<table>_meta.json` — 元数据（table_token, synced_at, record_count, content_hash）

## 输出

```
workspace/knowledge/data/
├── mcn/                    # 部门级汇总
│   ├── project_list.json
│   ├── project_weekly_kpi.json
│   └── department_health.json
├── brand-ops/              # 品牌代运营
│   ├── client_profile.json
│   ├── client_weekly_snapshot.json
│   ├── project_kpi.json
│   ├── service_record.json
│   └── team_profile.json
├── kol-incubation/         # 垂类达人孵化
│   ├── brand_cooperation.json
│   ├── content_production.json
│   ├── kol_profile.json
│   ├── kol_weekly_snapshot.json
│   ├── project_kpi.json
│   └── team_profile.json
├── live-commerce/          # 直播电商
│   ├── anchor_profile.json
│   ├── anchor_weekly_snapshot.json
│   ├── live_session.json
│   ├── product_selection.json
│   ├── project_kpi.json
│   └── team_profile.json
├── private-domain/         # 达人私域运营
│   ├── activity_record.json
│   ├── community_profile.json
│   ├── community_weekly_snapshot.json
│   ├── member_profile.json
│   ├── project_kpi.json
│   └── team_profile.json
├── short-video/            # 短视频内容矩阵
│   ├── account_profile.json
│   ├── account_weekly_snapshot.json
│   ├── content_production.json
│   ├── project_kpi.json
│   └── team_profile.json
└── virtual-ip/             # 虚拟IP孵化
    ├── ip_profile.json
    ├── ip_weekly_snapshot.json
    ├── live_session.json
    ├── project_kpi.json
    ├── team_profile.json
    └── tech_issue.json
```

## 与 wiki-ingest 的关系

```
base-sync（拉取结构化数据）
    └── 数据供
        ├── weekly-reporter（生成周报）
        └── qa-bot（回答数据查询）
```

**Base 数据不进入 workspace/knowledge/wiki/ 目录**，与知识文档物理隔离。

## 红线

- 不修改已存在的本地数据（除非检测到变更）
- 使用司南应用身份 `--profile compass --as user` 访问
- 权限不足时明确告知缺失的 scope
- 所有 Base 数据必须保存元数据（synced_at, record_count, content_hash）
