import { WeeklyReport, CreatorMetrics } from '@/types';

const topCreators: Record<string, CreatorMetrics> = {
  '虚拟偶像小萌': { id: 'creator-001', name: '虚拟偶像小萌', platform: 'douyin', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=xiaomeng', followers: 580000, weeklyGMV: 320000, weeklyOrders: 1200, avgViews: 2800000, topVideo: { title: '虚拟偶像出道首秀', views: 5200000, gmv: 180000 }, status: 'rising' },
  '虚拟达人阿酷': { id: 'creator-002', name: '虚拟达人阿酷', platform: 'kuaishou', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=akuku', followers: 280000, weeklyGMV: 180000, weeklyOrders: 680, avgViews: 1200000, topVideo: { title: '虚拟角色日常分享', views: 2200000, gmv: 120000 }, status: 'stable' },
  '虚拟博主小美': { id: 'creator-003', name: '虚拟博主小美', platform: 'redbook', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=xiaomei', followers: 180000, weeklyGMV: 85000, weeklyOrders: 320, avgViews: 520000, topVideo: { title: '虚拟穿搭分享', views: 980000, gmv: 65000 }, status: 'rising' },
  '虚拟UP主老王': { id: 'creator-004', name: '虚拟UP主老王', platform: 'bilibili', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=laowang', followers: 420000, weeklyGMV: 220000, weeklyOrders: 580, avgViews: 3800000, topVideo: { title: '虚拟世界观构建', views: 5800000, gmv: 150000 }, status: 'rising' },
};

export const demoReport: WeeklyReport = {
  heroSummary: {
    period: '2026-04-27 至 2026-05-03 (第9周)',
    lines: [
      { emoji: '🌟', label: 'IP孵化数', value: '12个', trend: 'up', status: 'normal', note: '较上周持平，暂无新增签约达人' },
      { emoji: '👥', label: '粉丝总量', value: '580万', trend: 'up', status: 'normal', note: '较上周+8.2%，虚拟偶像贡献主要增量' },
      { emoji: '💬', label: '互动率', value: '8.5%', trend: 'up', status: 'normal', note: '较上周+1.2pp，虚拟IP人设打造见效' },
      { emoji: '💰', label: '商业价值', value: '150分', trend: 'up', status: 'normal', note: '较上周+12分，品牌合作意向显著提升' },
      { emoji: '🎬', label: '内容产出', value: '48条', trend: 'up', status: 'normal', note: '较上周+15%，AIGC提效显著' },
    ],
  },

  platformData: [
    { platform: 'douyin', name: '抖音', color: '#6366F1', icon: '📱' },
    { platform: 'kuaishou', name: '快手', color: '#F59E0B', icon: '📹' },
    { platform: 'redbook', name: '小红书', color: '#EF4444', icon: '📖' },
    { platform: 'bilibili', name: '哔哩哔哩', color: '#06B6D4', icon: '📺' },
  ],

  projectKPI: [
    { label: '新增签约达人', thisWeek: '0', lastWeek: '1', change: '-100%', target: '-', status: 'yellow' },
    { label: '头部达人数量', thisWeek: '5', lastWeek: '5', change: '0%', target: '≥8', status: 'yellow' },
    { label: '周均粉丝增长率', thisWeek: '20%', lastWeek: '17%', change: '20%', target: '≥12%', status: 'green' },
    { label: '商单转化率', thisWeek: '20%', lastWeek: '10%', change: '100%', target: '≥15%', status: 'green' },
    { label: '达人周均变现', thisWeek: '2.72万', lastWeek: '2.43万', change: '12%', target: '≥0.7万', status: 'green' },
  ],

  kpiAnalysis: [
    {
      platform: 'douyin', status: 'normal',
      gmv: { value: 8500000, change: 28.5, reason: '虚拟偶像出道首秀带来爆发式曝光，新IP人设深受Z世代喜爱', insight: '虚拟偶像在抖音具有强大爆发力，建议持续深耕' },
      conversionRate: { value: 6.2, change: 1.8, reason: '虚拟偶像粉丝粘性强，互动意愿高，带动转化效率提升', insight: '虚拟偶像适合高互动场景，可进一步放大' },
      views: { value: 28000000, change: 35.2, reason: '虚拟偶像出道首秀播放量突破5000万，形成刷屏效应', insight: '虚拟IP在抖音具有强大传播势能' },
      fans: { value: 12500, change: 15.8, reason: '虚拟偶像出道吸引大量新用户关注，新增粉丝质量优', insight: '虚拟偶像粉丝增长仍有空间' },
      topCreator: topCreators['虚拟偶像小萌'],
      dailyData: [
        { date: '2026-04-21', gmv: 1200000, views: 3800000, conversionRate: 5.8, orders: 180, fans: 1800, engagement: 7.2 },
        { date: '2026-04-22', gmv: 1500000, views: 4500000, conversionRate: 6.2, orders: 220, fans: 2200, engagement: 8.5 },
        { date: '2026-04-23', gmv: 1800000, views: 5200000, conversionRate: 6.8, orders: 280, fans: 2600, engagement: 9.2 },
        { date: '2026-04-24', gmv: 1500000, views: 4800000, conversionRate: 6.5, orders: 220, fans: 2000, engagement: 8.8 },
        { date: '2026-04-25', gmv: 1200000, views: 3800000, conversionRate: 6.0, orders: 160, fans: 1500, engagement: 7.5 },
        { date: '2026-04-26', gmv: 800000, views: 3200000, conversionRate: 5.5, orders: 120, fans: 1200, engagement: 6.8 },
        { date: '2026-04-27', gmv: 500000, views: 2800000, conversionRate: 5.2, orders: 80, fans: 1200, engagement: 6.2 },
      ],
      followUps: [
        { id: 'fy-dy-1', question: '虚拟偶像如何保持人设一致性？' },
        { id: 'fy-dy-2', question: '618期间虚拟IP如何与大促联动？' },
        { id: 'fy-dy-3', question: '虚拟偶像商业变现路径如何优化？' },
      ],
    },
    {
      platform: 'kuaishou', status: 'normal',
      gmv: { value: 4200000, change: 18.5, reason: '虚拟达人阿酷表现稳定，老铁文化与虚拟IP融合良好', insight: '快手用户对虚拟IP接受度高，潜力被低估' },
      conversionRate: { value: 5.8, change: 1.2, reason: '老铁文化与虚拟IP产生化学反应，粉丝信任度高', insight: '虚拟达人适合快手老铁文化' },
      views: { value: 12000000, change: 22.8, reason: '虚拟内容在快手具有差异化优势，获得更多推荐流量', insight: '快手虚拟IP具有独特竞争力' },
      fans: { value: 8200, change: 12.5, reason: '虚拟内容差异化吸引新用户关注', insight: '快手虚拟IP用户增长空间大' },
      topCreator: topCreators['虚拟达人阿酷'],
      dailyData: [
        { date: '2026-04-21', gmv: 580000, views: 1600000, conversionRate: 5.2, orders: 85, fans: 1100, engagement: 6.5 },
        { date: '2026-04-22', gmv: 620000, views: 1750000, conversionRate: 5.5, orders: 95, fans: 1200, engagement: 7.2 },
        { date: '2026-04-23', gmv: 680000, views: 1850000, conversionRate: 5.8, orders: 105, fans: 1300, engagement: 7.8 },
        { date: '2026-04-24', gmv: 720000, views: 1950000, conversionRate: 6.0, orders: 115, fans: 1400, engagement: 8.2 },
        { date: '2026-04-25', gmv: 580000, views: 1650000, conversionRate: 5.6, orders: 90, fans: 1100, engagement: 7.0 },
        { date: '2026-04-26', gmv: 480000, views: 1450000, conversionRate: 5.4, orders: 75, fans: 950, engagement: 6.5 },
        { date: '2026-04-27', gmv: 380000, views: 1250000, conversionRate: 5.2, orders: 60, fans: 1150, engagement: 6.0 },
      ],
      followUps: [
        { id: 'fy-ks-1', question: '快手虚拟IP如何与老铁文化更好融合？' },
        { id: 'fy-ks-2', question: '虚拟达人人设如何本地化？' },
        { id: 'fy-ks-3', question: '618期间快手虚拟IP策略如何制定？' },
      ],
    },
    {
      platform: 'redbook', status: 'normal',
      gmv: { value: 1800000, change: 32.5, reason: '虚拟博主小美种草内容表现亮眼，精准触达带动转化', insight: '小红书是虚拟IP种草的理想平台' },
      conversionRate: { value: 4.8, change: 1.5, reason: '虚拟穿搭内容与小红书用户画像高度匹配', insight: '小红书虚拟IP适合高客单价产品' },
      views: { value: 3200000, change: 45.2, reason: '虚拟穿搭内容具有差异化优势，获得平台流量倾斜', insight: '小红书虚拟IP增长潜力巨大' },
      fans: { value: 5200, change: 18.8, reason: '种草内容带动新用户关注，质量高', insight: '小红书虚拟IP规模仍有增长空间' },
      topCreator: topCreators['虚拟博主小美'],
      dailyData: [
        { date: '2026-04-21', gmv: 240000, views: 420000, conversionRate: 4.2, orders: 42, fans: 680, engagement: 9.5 },
        { date: '2026-04-22', gmv: 280000, views: 480000, conversionRate: 4.5, orders: 48, fans: 780, engagement: 10.2 },
        { date: '2026-04-23', gmv: 320000, views: 550000, conversionRate: 4.8, orders: 55, fans: 900, engagement: 11.5 },
        { date: '2026-04-24', gmv: 350000, views: 600000, conversionRate: 5.2, orders: 62, fans: 980, engagement: 12.2 },
        { date: '2026-04-25', gmv: 280000, views: 480000, conversionRate: 4.8, orders: 48, fans: 720, engagement: 10.8 },
        { date: '2026-04-26', gmv: 200000, views: 380000, conversionRate: 4.5, orders: 35, fans: 580, engagement: 9.2 },
        { date: '2026-04-27', gmv: 130000, views: 290000, conversionRate: 4.2, orders: 22, fans: 560, engagement: 8.5 },
      ],
      followUps: [
        { id: 'fy-rb-1', question: '小红书虚拟IP种草策略如何优化？' },
        { id: 'fy-rb-2', question: '虚拟穿搭内容如何持续创新？' },
        { id: 'fy-rb-3', question: '618期间小红书虚拟IP如何为其他平台导流？' },
      ],
    },
    {
      platform: 'bilibili', status: 'normal',
      gmv: { value: 2800000, change: 25.8, reason: '虚拟UP主老王世界观构建内容深受B站用户喜爱', insight: 'B站是虚拟IP长线孵化的理想平台' },
      conversionRate: { value: 3.8, change: 0.6, reason: 'B站用户付费意愿强，对虚拟IP认可度高', insight: 'B站虚拟IP适合知识付费和会员订阅模式' },
      views: { value: 18500000, change: 32.5, reason: '虚拟世界观内容在B站引发讨论热潮，二创内容涌现', insight: 'B站是虚拟IP二创和UGC的天然土壤' },
      fans: { value: 9800, change: 15.2, reason: '虚拟世界观吸引大量B站核心用户关注', insight: 'B站虚拟IP粉丝价值高' },
      topCreator: topCreators['虚拟UP主老王'],
      dailyData: [
        { date: '2026-04-21', gmv: 380000, views: 2500000, conversionRate: 3.5, orders: 75, fans: 1350, engagement: 12.5 },
        { date: '2026-04-22', gmv: 420000, views: 2800000, conversionRate: 3.6, orders: 82, fans: 1500, engagement: 13.2 },
        { date: '2026-04-23', gmv: 480000, views: 3100000, conversionRate: 3.8, orders: 95, fans: 1700, engagement: 14.8 },
        { date: '2026-04-24', gmv: 520000, views: 3500000, conversionRate: 4.0, orders: 105, fans: 1850, engagement: 15.5 },
        { date: '2026-04-25', gmv: 420000, views: 2800000, conversionRate: 3.8, orders: 85, fans: 1400, engagement: 13.8 },
        { date: '2026-04-26', gmv: 320000, views: 2200000, conversionRate: 3.6, orders: 65, fans: 1150, engagement: 12.2 },
        { date: '2026-04-27', gmv: 260000, views: 2000000, conversionRate: 3.4, orders: 52, fans: 1850, engagement: 11.5 },
      ],
      followUps: [
        { id: 'fy-bb-1', question: 'B站虚拟IP如何激发用户二创热情？' },
        { id: 'fy-bb-2', question: '虚拟世界观如何持续扩展？' },
        { id: 'fy-bb-3', question: '618期间B站虚拟IP如何与大促联动？' },
      ],
    },
  ],

  taskRetro: {
    summary: { total: 6, completed: 3, delayed: 0, completionRate: 50 },
    tasks: [
      { id: 'task-001', title: '制定5月详细执行计划', assignee: '李小明', platform: 'douyin', status: 'completed', progress: 100, deadline: '2026-05-03', businessValue: '明确5月工作重点和里程碑', highlight: '计划已制定完成' },
      { id: 'task-002', title: '启动新一轮达人招募', assignee: '王五', platform: 'kuaishou', status: 'completed', progress: 100, deadline: '2026-05-02', businessValue: '扩大达人池，提升签约数量', highlight: '招募已启动' },
      { id: 'task-003', title: '发布新一轮招募信息', assignee: '王五', platform: 'douyin', status: 'completed', progress: 100, deadline: '2026-05-03', businessValue: '扩大项目影响力', highlight: '信息已发布' },
      { id: 'task-004', title: '调研达人私域运营模式', assignee: '李四', platform: 'redbook', status: 'in_progress', progress: 60, deadline: '2026-05-10', delayReason: '调研报告撰写中' },
      { id: 'task-005', title: '推进花西子品牌合同', assignee: '王五', platform: 'douyin', status: 'in_progress', progress: 40, deadline: '2026-05-15', delayReason: '合同条款协商中' },
      { id: 'task-006', title: '优化内容创新流程', assignee: '张三', platform: 'bilibili', status: 'in_progress', progress: 70, deadline: '2026-05-08', delayReason: '流程文档完善中' },
    ],
    followUps: [
      { id: 'fy-task-1', question: '2项延期任务是否影响618关键节点？' },
      { id: 'fy-task-2', question: '618虚拟IP联名如何快速落地？' },
      { id: 'fy-task-3', question: '虚拟偶像周边产品如何快速上市？' },
    ],
  },

  risks: [
    {
      id: 'risk-001', level: 'warning',
      conclusion: '头部达人数量低于预警线',
      reason: '头部达人数量 5 名，低于预警线（< 8 名）',
      impact: '项目整体状态：预警',
      affectedPlatform: 'douyin',
      followUps: [
        { id: 'fy-risk1-1', question: '如何快速提升头部达人数量至安全线？' },
        { id: 'fy-risk1-2', question: '达人招募计划如何加速推进？' },
      ],
    },
    {
      id: 'risk-002', level: 'warning',
      conclusion: '商单变现进度偏慢',
      reason: '花西子尚未签约，可能影响季度收入目标',
      impact: '商单变现进度偏慢（花西子尚未签约），可能影响季度收入目标',
      affectedPlatform: 'douyin',
      followUps: [
        { id: 'fy-risk2-1', question: '花西子品牌合同如何快速推进？' },
        { id: 'fy-risk2-2', question: '是否有备选品牌合作方案？' },
      ],
    },
    {
      id: 'risk-003', level: 'normal',
      conclusion: '5月假期可能影响内容产出节奏',
      reason: '假期期间达人内容产出效率可能下降',
      impact: '需提前做好内容储备和排期规划',
      affectedPlatform: 'kuaishou',
      followUps: [
        { id: 'fy-risk3-1', question: '如何保障假期期间内容供给？' },
        { id: 'fy-risk3-2', question: '内容创新流程如何优化以应对假期影响？' },
      ],
    },
  ],

  nextWeekPlan: {
    period: '2026-05-04 至 2026-05-10',
    focus: '618大促备战启动 · 虚拟IP矩阵扩量',
    tasks: [
      { id: 'nw-001', title: '618大促方案细化', platform: 'douyin', assignee: '李小明', startDate: '2026-05-04', endDate: '2026-05-06', priority: 'high', status: 'pending' },
      { id: 'nw-002', title: '虚拟偶像出道预热', platform: 'douyin', assignee: '张三', startDate: '2026-05-05', endDate: '2026-05-08', priority: 'high', status: 'pending' },
      { id: 'nw-003', title: '花西子品牌合同签署', platform: 'douyin', assignee: '王五', startDate: '2026-05-04', endDate: '2026-05-07', priority: 'high', status: 'pending' },
      { id: 'nw-004', title: '达人私域运营方案', platform: 'redbook', assignee: '李四', startDate: '2026-05-06', endDate: '2026-05-10', priority: 'medium', status: 'pending' },
      { id: 'nw-005', title: '新IP人设设计', platform: 'kuaishou', assignee: '赵六', startDate: '2026-05-05', endDate: '2026-05-09', priority: 'medium', status: 'pending' },
      { id: 'nw-006', title: '内容产出排期', platform: 'bilibili', assignee: '张三', startDate: '2026-05-04', endDate: '2026-05-05', priority: 'low', status: 'pending' },
    ],
  },
};
