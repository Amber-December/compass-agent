# data-collection

数据采集能力，负责从飞书各模块拉取原始数据。

## 能力

- 从飞书 Base 拉取表格数据
- 从飞书 Wiki 拉取文档列表和内容
- 从飞书妙记拉取会议记录
- 从项目群拉取文件和消息
- 数据清洗和格式化

## 数据源映射

| 数据源 | 采集内容 | 工具命令 |
|--------|----------|----------|
| 飞书 Base | KPI 数据、任务列表、项目状态 | `lark-cli base records list` |
| 飞书 Wiki | 文档内容、更新记录 | `lark-cli docs +fetch` |
| 飞书妙记 | 会议纪要、复盘要点 | `lark-cli minutes` |
| 项目群 | 文件、消息、@提及 | `lark-cli im messages list` |
| 本地缓存 | 上次采集的对比数据 | 读取 `data/raw/` |

## 采集策略

- **全量采集**：首次运行时拉取全部历史数据
- **增量采集**：后续只拉取上次采集后新增/修改的数据
- **定时触发**：通过 cron 或 heartbeat 定期执行

## 输出格式

采集的数据保存到 `data/raw/` 目录，按数据源分类：
```
data/raw/
├── base_YYYYMMDD.json
├── wiki_YYYYMMDD.json
├── minutes_YYYYMMDD.json
└── messages_YYYYMMDD.json
```
