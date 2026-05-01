# Compass（司南） — 团队效能助手
> 飞书原生的团队效能助手：把团队散落的知识（多维表格 / 妙记 / Wiki / 文档 / 群消息）自动编译成结构化“团队大脑”，在群聊中按需推送、回答与预警。**命名由来：** 司南意指“为团队找到方向”。Compass 不限定行业，适用于电商、研发等所有**项目制工作场景**。**首发场景：星澜传媒 MCN 事业部**下设6个并行项目，作为通用产品的 vertical验证。

---

## 一、通用场景定义

### 1.1 目标用户与痛点

<lark-table rows="4" cols="2" header-row="true" column-widths="128,490">

  <lark-tr>
    <lark-td>
      角色
    </lark-td>
    <lark-td>
      核心痛点
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **部门负责人**
    </lark-td>
    <lark-td>
      信息过载，难以**快速判断**不同项目进展/哪个项目要加资源/哪个项目有风险
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **项目负责人**
    </lark-td>
    <lark-td>
      每周写周报、汇总项目进展耗时长
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **项目团队成员**
    </lark-td>
    <lark-td>
      经验复用难，历史复盘藏在妙记/群消息里，新成员上手慢
    </lark-td>
  </lark-tr>
</lark-table>

### 1.2 核心使用场景

#### <text bgcolor="light-yellow">场景 A — 周一早晨主动推送 ⏰</text>
> 「周一早 9 点,司南把上周周报推送到项目群,把部门精选推给部门群。」

- **项目群** →**详细版周报：** 上周数据看板 + 任务完成情况 + 风险提醒 + 本周计划
- 生成项目周报飞书文档一篇——归档到对应项目下（PM 可以进行微调和修改）

<mention-doc token="Ur3fd7PSOogQQ5xEKhBcMrIMnAf" type="docx">[2026-04-13至2026-04-19] 静态感知项目周报</mention-doc>
```markdown
# 项目 metadata（title、type、date、status）
# 上周任务完成情况（根据文档和数据看板生成）——核心业务指标 KPI
# 本周计划
# ⚠️风险与阻塞 （数据规则匹配——推理概括）
# 详情链接: [完整周报飞书文档]
```

- **部门群** →**部门看板：** N 个项目状态(🟢🟡🔴) + Top3 知识精选
```markdown
# 项目进度/状态🟢🟡🔴/核心 kpi看板
# 本周部门知识精选 Top3
（wiki优秀文档：上周技术分享/资源分享/高频访问、点赞文档）
```

- 触发：定时
- **嵌入式风险提醒** ⚠️
  - **不做独立的实时告警系统**(误报代价大)
  - 数据规则 + 关键词匹配 + LLM 综合判断
  - **阈值由场景配置文件决定，各项目可定制**
- **Top3 知识精选 — 自动评分规则**
  - 候选源头: **部门 Wiki + 妙记 + 项目群文档**(本周新增/修改)
  - **优先类别**: 资源分享 / 培训文档(类型权重最高,即 SOP / 培训 / 复盘等)
  - 打分维度(由 LLM 一次性综合判断)

<lark-table rows="5" cols="3" header-row="true" column-widths="123,89,475">

  <lark-tr>
    <lark-td>
      维度
    </lark-td>
    <lark-td>
      权重
    </lark-td>
    <lark-td>
      信号
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      类型
    </lark-td>
    <lark-td>
      高
    </lark-td>
    <lark-td>
      SOP / 教程 / 培训 / 复盘 / 经验分享 → 高分;数据汇报 / 进度同步 → 低分
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      时效
    </lark-td>
    <lark-td>
      中
    </lark-td>
    <lark-td>
      本周新增 / 修改 → 高;3 周以前 → 低
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      跨项目价值
    </lark-td>
    <lark-td>
      中
    </lark-td>
    <lark-td>
      内容能被多项目复用 → 高;只对单项目 → 低
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      完整度
    </lark-td>
    <lark-td>
      低
    </lark-td>
    <lark-td>
      长度合理(200 字+) + 结构清晰 → 高;碎片消息 → 低
    </lark-td>
  </lark-tr>
</lark-table>

#### <text bgcolor="light-yellow">场景 B — 项目群内自然语言查询 💬</text>
> 「PM @ 司南问'上次复盘的整改项现在做完了吗?'司南秒答。」

- **项目群 @**：本项目数据/文档，跨周期聚合分析，跨项目则有权限限制（⚠️ 跨项目敏感数据未开放,如需详情请到 [项目名] 群内询问"）
- **意图识别与拒答意图**
- **答案规范**：**带飞书原始链接引用** + “数据中没有就明说，不外推”

### 1.3 产品核心能力

<lark-table rows="6" cols="4" header-row="true" column-widths="100,213,236,226">

  <lark-tr>
    <lark-td>
      能力
    </lark-td>
    <lark-td>
      输入
    </lark-td>
    <lark-td>
      输出
    </lark-td>
    <lark-td>
      用户感知
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **知识编译**
    </lark-td>
    <lark-td>
      Base + 妙记 + 飞书Wiki
    </lark-td>
    <lark-td>
      结构化 wiki(实体/概念/源页)
    </lark-td>
    <lark-td>
      后台不可见,Q&A 准确度的根基
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **周报合成**
    </lark-td>
    <lark-td>
      一周内的 Base 行 + 妙记 + 项目群文件 +飞书 wiki
    </lark-td>
    <lark-td>
      Markdown /html 卡片消息
    </lark-td>
    <lark-td>
      每周一上午自动推送
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **风险检测**
    </lark-td>
    <lark-td>
      数据规则 + 文本(嵌入式)
    </lark-td>
    <lark-td>
      周报中 ⚠️ section
    </lark-td>
    <lark-td>
      每周一上午自动推送
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **部门聚合**
    </lark-td>
    <lark-td>
      多项目周报 + ⭐ 精选标记
    </lark-td>
    <lark-td>
      部门看板卡片
    </lark-td>
    <lark-td>
      部门负责人一眼看完本周
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **自然查询**
    </lark-td>
    <lark-td>
      群内 @ 消息 + 项目 scope
    </lark-td>
    <lark-td>
      Markdown 答案 + 飞书链接引用
    </lark-td>
    <lark-td>
      跨周期检索,引用清晰
    </lark-td>
  </lark-tr>
</lark-table>

### 1.4 产品价值假设(——待数据验证)

<lark-table rows="5" cols="4" header-row="true" column-widths="110,183,183,183">

  <lark-tr>
    <lark-td>
      维度
    </lark-td>
    <lark-td>
      现状(估)
    </lark-td>
    <lark-td>
      司南介入后(目标)
    </lark-td>
    <lark-td>
      量化收益(假设)
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      PM 时间
    </lark-td>
    <lark-td>
      周报撰写 4h/周
    </lark-td>
    <lark-td>
      30min(审核)
    </lark-td>
    <lark-td>
      ~3.5h/PM/周
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      部门长时间
    </lark-td>
    <lark-td>
      周会同步 1.5h/周
    </lark-td>
    <lark-td>
      30min(只看异常)
    </lark-td>
    <lark-td>
      ~1h/周
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      历史复用
    </lark-td>
    <lark-td>
      复盘整改项靠记忆跟踪
    </lark-td>
    <lark-td>
      自动追问 + 进度透明
    </lark-td>
    <lark-td>
      关键事项落地率 ↑
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      决策时效
    </lark-td>
    <lark-td>
      风险事后追溯
    </lark-td>
    <lark-td>
      周报嵌入式预警
    </lark-td>
    <lark-td>
      降低补救成本
    </lark-td>
  </lark-tr>
</lark-table>

> 对部门规模 = 10 项目的部门: 每周节省约 36 人时,相当于多一个 0.5 FTE 的产出。**这些数字是产品价值假设,需要试点期验证。**

---

## 二、垂直场景验证：MCN 部门

### 2.1 用户与组织背景

- **公司：** 星澜传媒
- **部门**：MCN 事业部
- **规模**：6 个并行项目，每项目 1 个 PM + 内容/运营/商务/技术等多角色
- **节奏**：挖掘 → 孵化 → 内容生产 → 变现（周/双周循环）
- **数据基建**：飞书多维表格(Base)集中记录 KPI；妙记承载会议复盘；Wiki 沉淀 SOP

### 2.2 MCN 部门具体痛点

<lark-table rows="5" cols="3" header-row="true" column-widths="209,228,244">

  <lark-tr>
    <lark-td>
      痛点
    </lark-td>
    <lark-td>
      现状
    </lark-td>
    <lark-td>
      司南介入后
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      多平台数据散(抖音/快手/小红书/B站)
    </lark-td>
    <lark-td>
      各 PM 自己用 Excel 拼
    </lark-td>
    <lark-td>
      Base 集中 + 司南汇总
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      达人经验/内容方法论难复用
    </lark-td>
    <lark-td>
      妙记和 Wiki 越积越多没人翻看
    </lark-td>
    <lark-td>
      Q&A 跨项目知识聚合
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      内容合规/商务风险事后才发现
    </lark-td>
    <lark-td>
      出事后做总结
    </lark-td>
    <lark-td>
      周报嵌入式预警
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      部门负责人难判断项目优先级
    </lark-td>
    <lark-td>
      靠 PM 主动汇报
    </lark-td>
    <lark-td>
      部门看板红黄绿 + 异常突出
    </lark-td>
  </lark-tr>
</lark-table>

### 2.3 MCN 场景的核心 KPI 与数据流

**主数据源（飞书 Base 表字段）**:

- **达人侧**：达人数量 / 粉丝总量 / 粉丝增长率 / 达人活跃度 / 达人流失率
- **内容侧**：播放量 / 爆款率 / 更新频次 / 互动率 / 完播率
- **变现侧**：GMV / 品牌合作数 / 项目营收 / 私域转化 / ROI
- **风险侧**：合规事件 / 客诉率 / 达人违约 / 内容下架 / 技术故障率

**辅助数据源**:

- 妙记：选品会议、复盘会议、客户对接会、技术评审会
- 部门 Wiki：达人 SOP / 内容审核规范 / 商务谈判手册 / 合规指南
- 项目群文件：直播脚本、短视频分镜、品牌 brief、达人合同模板

### 2.4 具体项目设计（6 个项目）

<lark-table rows="7" cols="5" header-row="true" column-widths="50,120,230,230,230">

  <lark-tr>
    <lark-td>
      id
    </lark-td>
    <lark-td>
      项目
    </lark-td>
    <lark-td>
      核心 KPI(优先级↓)
    </lark-td>
    <lark-td>
      关键风险阈值
    </lark-td>
    <lark-td>
      知识库重点
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      1
    </lark-td>
    <lark-td>
      垂类达人孵化
    </lark-td>
    <lark-td>
      头部达人数量(≥8名); 月均粉丝增长率(≥12%); 商单转化率(≥15%); 达人月均变现(≥3万)
    </lark-td>
    <lark-td>
      孵化数量3个月未达目标50%; 粉丝增长率连续2月<5%; 商单转化率<8%
    </lark-td>
    <lark-td>
      素人筛选标准; "筛选-培训-扶持-变现"链路; 品牌绑定技巧; 垂类赛道分析
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      2
    </lark-td>
    <lark-td>
      短视频内容矩阵
    </lark-td>
    <lark-td>
      矩阵月播放量(≥3000万); 爆款占比(≥8%); 月均账号增量(≥30万); 日均更新(≥10条)
    </lark-td>
    <lark-td>
      播放量连续2月<1500万; 爆款占比<3%; 更新频次日均<5条持续1周
    </lark-td>
    <lark-td>
      多赛道内容策划; AI脚本/剪辑应用; 数据监测与迭代方法; 流量沉淀与引流
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      3
    </lark-td>
    <lark-td>
      品牌代运营
    </lark-td>
    <lark-td>
      月均新增品牌(≥2家); 客户满意度(≥90%); 单品牌月曝光(≥500万); 项目月营收(≥50万)
    </lark-td>
    <lark-td>
      月新增品牌<1家; 满意度<80%且出现投诉; 月营收<25万
    </lark-td>
    <lark-td>
      品牌筛选与洽谈; 达人匹配方案; 效果监测与优化; 客户汇报模板
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      4
    </lark-td>
    <lark-td>
      直播电商
    </lark-td>
    <lark-td>
      月GMV(≥80万); 直播转化率(≥5%); 场均观看(≥2万); ROI(≥1:3)
    </lark-td>
    <lark-td>
      GMV连续2月<40万; 转化率连续3场<2%; ROI<1:1.5
    </lark-td>
    <lark-td>
      直播间搭建; 选品与排期SOP; 主播话术与中控协作; 流量投放策略
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      5
    </lark-td>
    <lark-td>
      达人私域运营
    </lark-td>
    <lark-td>
      月均私域沉淀(≥1万); 粉丝活跃度(≥25%); 私域转化(≥10%); 复购率(≥20%)
    </lark-td>
    <lark-td>
      月沉淀<4000人; 活跃度连续2周<10%; 复购率<10%
    </lark-td>
    <lark-td>
      私域流量池搭建; 激活活动策划; 转化闭环技巧; 粉丝留存策略
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      6
    </lark-td>
    <lark-td>
      虚拟IP孵化与运营
    </lark-td>
    <lark-td>
      上线虚拟IP数量(≥2个); 虚拟IP粉丝总量(≥30万); 月商业化营收(≥15万); 直播/短视频互动率(≥8%); 技术故障率(≤2%)
    </lark-td>
    <lark-td>
      孵化周期超4个月未上线; 粉丝总量3个月<10万; 月营收<5万; 技术故障率>5%
    </lark-td>
    <lark-td>
      虚拟人技术栈选型; IP人设与世界观打造; AIGC内容生产流程; 虚拟直播/短视频运营技巧; 粉丝互动与变现路径
    </lark-td>
  </lark-tr>
</lark-table>

### 2.5 司南在 MCN 部门的产品形态

#### 周一 9:00 — 项目群推送(详细版周报)
```plaintext
【📊 司南 · 上周战报 — 垂类达人孵化】
👤 新增签约达人 2 名，累计孵化中 8 名
📈 头部达人平均粉丝增长率 15%(↑ 3% vs 上周)
💰 商单转化 18%(目标 15% ✓)
✅ 任务完成 6/8(品牌绑定 ✓ / 内容定位 ⏳ 延期)
⚠️ 风险点: 美妆赛道达人「小A」连续2周粉丝负增长
🎯 本周计划: 素人面试 ×5 / 内容复盘会 ×1
📎 详情: [完整周报飞书文档]

```

#### 周一 9:05 — 部门群推送(部门看板)
```plaintext
【📌 司南 · 部门看板 — MCN 事业部】
6 个项目: 🟢 4  🟡 1  🔴 1
🔴 「虚拟IP孵化」技术故障率 6% — @ 技术 PM 同步进展
🟡 「直播电商」GMV 连续2周下滑

📚 本周精选(部门 lead ⭐ 标记):
1. 妙记 · 垂类达人筛选标准会 → 跨项目复用
2. 文档 · 虚拟IP人设打造指南 → 世界观方法论
3. 妙记 · 品牌代运营复盘 → 客户满意度提升技巧

```

#### 工作中随时 — 群内 Q&A
```plaintext
PM:    上次虚拟IP「星瞳」直播卡顿那次是什么原因?

司南:  根据 [4/20 技术复盘妙记],问题 3 个:
       1. 动捕设备延迟 200ms，导致口型不同步
       2. 推流码率设置过高，带宽不足
       3. 备用方案未触发，缺乏容灾机制

       复盘行动项进度:
        ✓ 动捕设备升级(已落实)
        ✓ 推流码率分级策略(已落实)
        ⏳ 容灾演练(本周待推进)

```


<lark-table rows="4" cols="2" column-widths="367,401">

  <lark-tr>
    <lark-td>
      **可以回答** {align="center"}
    </lark-td>
    <lark-td>
      **拒答** {align="center"}
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      - 部门级聚合:部门总营收、本周达标项目数、红黄绿灯分布
    </lark-td>
    <lark-td>
      - 其他项目 KPI 具体数值(GMV、ROI、复购率明细)
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      - 知识沉淀:Top3 复盘要点(这本来就是部门共享资产)
    </lark-td>
    <lark-td>
      - 其他项目的达人个人绩效、违规记录
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      - 元信息:有哪几个项目、各项目品类、各项目 PM 是谁
    </lark-td>
    <lark-td>
      - 其他项目的整改进度细节
    </lark-td>
  </lark-tr>
</lark-table>

## 三、通用性证明 — 司南可服务的其他部门 {folded="true"}
> 直播电商只是首发场景。司南的核心能力(知识编译 / 周报 / Q&A / 嵌入式预警)对所有项目制部门都有效——只需要更换"场景配置"。

<lark-table rows="6" cols="3" header-row="true" column-widths="131,244,244">

  <lark-tr>
    <lark-td>
      部门
    </lark-td>
    <lark-td>
      KPI 替换
    </lark-td>
    <lark-td>
      工作流类比
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      内容创作部
    </lark-td>
    <lark-td>
      播放量 / 完播率 / 粉丝增量
    </lark-td>
    <lark-td>
      选题 → 脚本 → 拍摄 → 剪辑 → 发布
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      商务/招商部
    </lark-td>
    <lark-td>
      合作金额 / 品牌数 / 续约率
    </lark-td>
    <lark-td>
      线索 → 沟通 → 提案 → 签约 → 交付
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      运营增长部
    </lark-td>
    <lark-td>
      DAU / 留存 / 投放 ROI
    </lark-td>
    <lark-td>
      活动策划 → 投放 → 复盘
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      软件研发部
    </lark-td>
    <lark-td>
      需求完成数 / 线上 BUG / 发布质量
    </lark-td>
    <lark-td>
      需求 → 设计 → 编码 →测试 → 发布
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      教育/培训部
    </lark-td>
    <lark-td>
      学员完课率 / 满意度 / 续费率
    </lark-td>
    <lark-td>
      备课 → 开课 → 反馈 → 迭代
    </lark-td>
  </lark-tr>
</lark-table>

**通用化机制**:

- `config/scenarios/<name>.yaml` — 场景配置(KPI 字段、风险阈值、数据源 token)
- `prompts/<scenario>/*.md` — 周报 / Q&A / 部门看板的 prompt 模板
- 代码 0 改动,**换场景 = 换配置 + 换模板****决赛验证计划**: 复赛通过后,接入第二个真实场景(候选: 内容创作部 / 软件研发部),展示同一份代码跑两个完全不同的业务领域。——待商榷，也可以细化现在场景的能力

---

## 五、初赛排期 (10 天 × 2 人)

### 5.1 角色定义

- <text bgcolor="light-purple">**P1**</text><text bgcolor="light-purple">: 负责业务场景 / skill workflow / 飞书数据库和 wiki知识库构建 / Q&A评测 / Demo 制作</text> <mention-user id="ou_8a7701391f39a4edc34e17372c76b992"/>
- <text bgcolor="light-blue">**P2**</text><text bgcolor="light-blue">: 主负责 Lark API / AI Agent 架构 / 卡片前端&prompt、skill 细化 / Demo 制作</text><mention-user id="ou_fa91bb8d77e80f1620c06640574585aa"/>

<lark-table rows="5" cols="3" header-row="true" column-widths="105,253,280">

  <lark-tr>
    <lark-td>
      维度
    </lark-td>
    <lark-td>
      P1
    </lark-td>
    <lark-td>
      P2
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      主战场
    </lark-td>
    <lark-td>
      业务场景 / 飞书数据库 + wiki 知识库 / Q&A 评测 / Demo 制作
    </lark-td>
    <lark-td>
      Lark API / AI Agent 架构 / 卡片前端 + prompt / skill 细化 / Demo 制作
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      节奏
    </lark-td>
    <lark-td>
      业务 + 数据 + Q&A 评测,产出可视化
    </lark-td>
    <lark-td>
      工程攻坚多,每日代码可见
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      高耦合点
    </lark-td>
    <lark-td>
      Day 1 联调、Day 6 联调
    </lark-td>
    <lark-td>
      同 P1
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      独立点
    </lark-td>
    <lark-td>
      Day 2-5 模块开发
    </lark-td>
    <lark-td>
      同 P1
    </lark-td>
  </lark-tr>
</lark-table>

### 5.2 时间表
> **基准日期**: 2026-04-28 (周二) Kickoff → 2026-05-07 12:00(周四) 初赛提交 → 2026-05-14 (周四) 复赛节点

#### 4.28 (周二) 晚 — Kickoff ★ (本晚开)

- [一起] 30-60 min 会议: 锁定 demo 故事板 / 10 项目名 / SKU 命名 / mock 数据 schema / Top3 评分维度
- [一起] 确认 §七 分工、Day-by-Day 任务依赖、五一假期安排
- <text bgcolor="light-purple">**</text><text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] 整理 demo 场景，落地为**</text><text bgcolor="light-purple">`**docs/story-board.md**`</text>
- <text bgcolor="light-blue">**[P2] 完成企业机器人部署，确定 agent 架构**</text>

#### 4.29 (周三) — Day 1: 数据 + API 联调

- <text bgcolor="light-purple">**[P1] 在飞书 Base 里造 mock 数据: 10 项目 × 4 周(GMV / 转化率 / 场次 / 任务列表 / 状态)**</text>
- <text bgcolor="light-blue">**[P2] Lark API 4 个最小 demo: 拉 Base / 拉妙记 / 拉文档 / 定时发群消息**</text>
- ⚠️ **当晚必须完成数据填充**, 后续所有功能依赖 ——P1 外出调研了尽量完成😭

#### 4.30 (周四) — Day 2: 知识底座

- <text bgcolor="light-purple">**[P1] 在飞书造妙记内容(10 份: 选品 / 复盘 / 对接) + 部门 Wiki(5 份: SOP / 培训 / 经验) → 喂入 wiki 知识库——ingest**</text>
- <text bgcolor="light-blue">**[P2] 写**tools/lark_ingest.py**: 飞书拉 →**raw/lark/** → 触发现有 ingest →**wiki/sources/**(skill 细化：adapter 层)**</text>

#### 5.1 (周五,劳动节) — Day 3:  阶段汇总★

- [一起] 把周三、周四的任务完成，晚上开会，总结阶段成果，定后面方向

#### 5.2 (周六) — Day 4: 周报合成 + 通用化层落地

- <text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] </text><text bgcolor="light-purple">**第一次落地通用化层**</text><text bgcolor="light-purple"> — KPI 字段 / 阈值 / prompt 路径抽到 </text><text bgcolor="light-purple">`config/scenarios/livestream.yaml`</text><text bgcolor="light-purple">(业务侧设计,P2 协助接代码);</text><text bgcolor="light-purple">**Q&A 评测集准备**</text><text bgcolor="light-purple">(40-50 条问题 + 期望答案,覆盖本项目深问 / 跨项目浅问 / 边界外推 三类)+ mock 数据细节增强</text>
- <text bgcolor="light-blue">[</text><text bgcolor="light-blue">P2] 周报 prompt 模板 + 项目级生成脚本 + 部门聚合脚本; </text><text bgcolor="light-blue">**Top3 自动评分实现**</text><text bgcolor="light-blue">(LLM 打分,候选池筛选)</text>

#### 5.3 (周日) — Day 5: IM 推送 + Q&A 雏形

- <text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] Q&A 答案规范 prompt(业务边界 / 拒答规则)+ 评测集跑分(用 Day 3 准备的 40-50 条 case)+ Demo 故事板细化</text>
- <text bgcolor="light-blue">[</text><text bgcolor="light-blue">P2] Lark IM 卡片消息推送(无审批,直接推到测试群)+ </text><text bgcolor="light-blue">**lark-event 长连接框架搭建**</text><text bgcolor="light-blue"> + Q&A bot 雏形(收 @ 消息 → 调 Claude → 简单回复跑通链路)+ 视觉 polish(emoji / 分隔线 / 卡片样式)</text>

#### 5.4 (周一) — Day 6: Q&A 检索 + 风险嵌入★

- <text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] </text><text bgcolor="light-purple">**风险检测业务规则定义(哪些数据组合算风险 / 哪些关键词触发警报)**</text><text bgcolor="light-purple">+ 跨项目浅查规则细化 + Q&A 边界 case 复测</text>
- <text bgcolor="light-blue">[</text><text bgcolor="light-blue">P2] Q&A bot 接 wiki/ 检索 + Markdown 答案 + 飞书链接引用 + 边界 prompt(不外推);</text><text bgcolor="light-blue">**周报嵌入式风险检测段**</text><text bgcolor="light-blue">(LLM 综合判断: 数据阈值 + 关键词 + 综合)</text>

#### 5.5 (周二) — Day 7: 联调 + Polish ★

- <text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] 业务规则优化/数据结构优化/调试效果/前面的遗留工作</text>
- <text bgcolor="light-blue">[</text><text bgcolor="light-blue">P2] badcase 优化/调试效果/界面优化/ 前面的遗留工作</text>

#### 5.6 (周三) — Day 8: Demo 与代码调试★

- <text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] </text><text bgcolor="light-purple">**README 写作**</text><text bgcolor="light-purple">(痛点 / 方案 / 价值 / 路线图)+ </text><text bgcolor="light-purple">**1 页产品文档 PDF**</text><text bgcolor="light-purple"> + Demo 故事板录稿</text>
- <text bgcolor="light-blue">[</text><text bgcolor="light-blue">P2] 代码仓整理(架构图 / 目录干净 / commit history)+ </text><text bgcolor="light-blue">**录 demo 视频**</text>
- [一起] 线下冲刺代码和 demo

#### 5.7 (周四) — 初赛提交日 🏁

- <text bgcolor="light-purple">[</text><text bgcolor="light-purple">P1] 终审 README  / 产品文档PDF  / 代码仓库维护</text>
- <text bgcolor="light-blue">[</text><text bgcolor="light-blue">P2] 代码仓库维护  / demo 视频优化</text>

### 5.3 提交清单

<lark-table rows="4" cols="3" header-row="true" column-widths="180,303,156">

  <lark-tr>
    <lark-td>
      项
    </lark-td>
    <lark-td>
      形式
    </lark-td>
    <lark-td>
      完成时点
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      Demo 视频
    </lark-td>
    <lark-td>
      5 min mp4,带字幕
    </lark-td>
    <lark-td>
      5.5 (周三) 下午
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      GitHub repo
    </lark-td>
    <lark-td>
      README 完整、架构图、运行步骤
    </lark-td>
    <lark-td>
      5.5 (周三) 下午
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      1 页产品文档
    </lark-td>
    <lark-td>
      PDF: 痛点/方案/价值/路线图
    </lark-td>
    <lark-td>
      5.7 (周四) 上午
    </lark-td>
  </lark-tr>
</lark-table>

## 六、复赛预案 (7 天 × 2 人,条件触发) {folded="true"} {folded="true"}
> 复赛具体场景暂不锁定,等初赛 judges 反馈后调整重点。

### 6.1 候选方向(初赛后视反馈选 1-2 个)

<lark-table rows="6" cols="3" header-row="true" column-widths="120,332,80">

  <lark-tr>
    <lark-td>
      选项
    </lark-td>
    <lark-td>
      说明
    </lark-td>
    <lark-td>
      工作量
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      A. 跨场景验证
    </lark-td>
    <lark-td>
      接入第二场景(候选: 内容创作部),证明通用化机制
    </lark-td>
    <lark-td>
      中
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      B. 实时增量
    </lark-td>
    <lark-td>
      接入 lark-event,doc 修改后秒级 ingest(完成 Phase 2)
    </lark-td>
    <lark-td>
      中
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      C. 周报审核流
    </lark-td>
    <lark-td>
      飞书交互卡片 + 长连接回调,V2 完整审核闭环
    </lark-td>
    <lark-td>
      中
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      D. 可视化看板
    </lark-td>
    <lark-td>
      周报除文字外生成 HTML/飞书画板看板(ECharts)
    </lark-td>
    <lark-td>
      中-高
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      E. 跨周期深度分析
    </lark-td>
    <lark-td>
      Q&A 中加趋势图、对比表、归因分析
    </lark-td>
    <lark-td>
      高
    </lark-td>
  </lark-tr>
</lark-table>

### 6.2 推荐组合: **A + C**

- **A** 直接展示通用性叙事(决赛 demo 杀手锏)
- **C** 把"审核流"从 V1 缺口变成完整 V2 体验

#### 6.3  复赛阶段简描 (5.7 - 5.14,若入选)

- **5.7 (四) 晚 ~ 5.8 (五)** — 反馈消化:整理 judges 评语,锁定复赛重点方向
- **5.9 (六) ~ 5.10 (日)** — Sprint 1:跨场景验证 (方向 A) — 配置层接入第二场景(候选: 内容创作部 / HR 部),证明通用化机制
- **5.11 (一) ~ 5.12 (二)** — Sprint 2:周报审核流 (方向 C) — 飞书交互卡片 + 长连接回调,V2 完整审核闭环
- **5.13 (三)** — 联调 + 录复赛 demo 视频(5 min)+ Polish
- **5.14 (四)** — 决赛提交 / 现场 Q&A

---

## 七、技术架构与风险预案

### 7.1 架构层次
```plaintext
┌────────────────────────────────────────────────────────┐
│ 应用层  │ 周报合成    │ Q&A bot     │ 部门聚合 + Top3   │
├────────────────────────────────────────────────────────┤
│ 分发层  │ Lark IM 卡片消息推送 (V1 无审批)              │
├────────────────────────────────────────────────────────┤
│ 知识底座 │ wiki/sources/ + entities/ + concepts/ (本地) │
├────────────────────────────────────────────────────────┤
│ 适配层  │ tools/lark_ingest.py (Base/妙记/Wiki/文档拉取)│
├────────────────────────────────────────────────────────┤
│ 配置层  │ config/scenarios/<name>.yaml + prompts/...   │
├────────────────────────────────────────────────────────┤
│ 数据源  │ Lark Base / 妙记 / Wiki / 文档               │
└────────────────────────────────────────────────────────┘


```

### 7.2 关键风险与 fallback

<lark-table rows="5" cols="3" header-row="true" column-widths="211,80,272">

  <lark-tr>
    <lark-td>
      风险
    </lark-td>
    <lark-td>
      概率
    </lark-td>
    <lark-td>
      fallback
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      LLM 输出冗长 / 格式乱
    </lark-td>
    <lark-td>
      中
    </lark-td>
    <lark-td>
      prompt cache 固化模板,output schema 严格
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      Mock 数据被 judge 看出假
    </lark-td>
    <lark-td>
      低-中
    </lark-td>
    <lark-td>
      数据量足够 + 找 1 名 MCN 朋友 30 min 把关合理性
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      Demo 时 Q&A 被问数据外的
    </lark-td>
    <lark-td>
      中
    </lark-td>
    <lark-td>
      bot 明确"数据中无此信息"(展示边界感,反而加分)
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      Top3 评分翻车(选错文档)
    </lark-td>
    <lark-td>
      中
    </lark-td>
    <lark-td>
      mock 数据预先标记几篇优质文档,demo 时优先抽这几篇
    </lark-td>
  </lark-tr>
</lark-table>

---

## 📍 文档版本

- v0.1 (2026-04-28): 场景定义初版
- v0.2 (2026-04-28): 7 项产品决策落地 + 初赛/复赛排期 + 团队分工 + 技术架构*维护: Claude Code via lark-cli*
