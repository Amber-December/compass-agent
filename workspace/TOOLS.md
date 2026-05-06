# TOOLS.md - Compass 环境特定配置

## lark-cli 常用速查

### 身份切换
```bash
# 应用级操作（Bot）
lark-cli <cmd> --as bot

# 用户级操作
lark-cli <cmd> --as user
```

### Wiki 操作
```bash
# 获取节点信息
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}'

# 创建 Wiki 节点
lark-cli wiki +node-create --space <space_id> --parent <parent_token> --type docx --title "标题"

# 列出子节点
lark-cli wiki nodes list --params '{"space_id":"<space_id>"}'

# 读取文档
lark-cli docs +fetch --doc <obj_token> --format pretty

# 创建文档
lark-cli docs +create --title "标题" --content "内容"
```

### Base 操作
```bash
# 拉取记录
lark-cli base records list --params '{"app_token":"<app_token>"}'

# 查看表结构
lark-cli base tables list --params '{"app_token":"<app_token>"}'
```

### IM 操作
```bash
# 发送文本消息
lark-cli im messages create --data '{"receive_id":"<chat_id>","msg_type":"text","content":"{\"text\":\"hello\"}"}'

# 发送卡片消息
lark-cli im messages create --data '{"receive_id":"<chat_id>","msg_type":"interactive","content":"{\"card\":{...}}"}'
```

## 核心 Python 工具

```bash
# 知识编译
python tools/wiki_ingest.py workspace/raw_lark/wiki/项目\ OnePage.md
python tools/wiki_ingest.py --batch workspace/raw_lark/wiki/

# 知识检索
python tools/wiki_query.py "垂类达人孵化的粉丝增长率为什么下滑？"

# 图谱构建
python tools/build_graph.py
python tools/build_graph.py --no-infer   # 跳过语义推断（更快）
python tools/build_graph.py --open       # 构建后打开浏览器
```

## 环境变量

`.env` 中配置：
- `FEISHU_APP_ID` / `FEISHU_APP_SECRET` — 飞书应用凭证
- `WIKI_SPACE_ID` — MCN 知识库空间 ID
- `WIKI_MCN_NODE_TOKEN` — MCN 根节点 token
- `FEISHU_CHAT_ID` — 部门群 chat_id

## 项目群 chat_id 映射

| 项目 | chat_id |
|------|---------|
| 垂类达人孵化 | oc_d2f8a9f659fce3626572c2bd80083d23 |
| 短视频内容矩阵 | （待配置） |
| 品牌代运营 | （待配置） |
| 直播电商 | （待配置） |
| 达人私域运营 | （待配置） |
| 虚拟 IP 孵化 | （待配置） |
| 部门群 | （待配置） |

## Base 链接映射

| 项目 | Base 链接 |
|------|----------|
| 垂类达人孵化 | https://ncnkdep1f4r7.feishu.cn/wiki/Gogaw0Iz5ijHUmkjEhZcVGT6n7b |
| 短视频内容矩阵 | （待配置） |
| 品牌代运营 | （待配置） |
| 直播电商 | （待配置） |
| 达人私域运营 | （待配置） |
| 虚拟 IP 孵化 | （待配置） |

