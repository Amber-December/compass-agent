export type Platform = 'douyin' | 'kuaishou' | 'redbook' | 'bilibili';

export type taskStatus = 'completed' | 'in_progress' | 'delayed' | 'pending';
export type RiskLevel = 'critical' | 'warning' | 'normal';

export interface DailyKPI {
  date: string;
  gmv: number;
  views: number;
  conversionRate: number;
  orders: number;
  fans: number;
  engagement: number;
}

export interface CreatorMetrics {
  id: string;
  name: string;
  platform: Platform;
  avatar: string;
  followers: number;
  weeklyGMV: number;
  weeklyOrders: number;
  avgViews: number;
  topVideo?: { title: string; views: number; gmv: number };
  status: 'rising' | 'stable' | 'declining';
}

export interface KPIModule {
  platform: Platform;
  status: RiskLevel;
  gmv: { value: number; change: number; reason: string; insight: string };
  conversionRate: { value: number; change: number; reason: string; insight: string };
  views: { value: number; change: number; reason: string; insight: string };
  fans: { value: number; change: number; reason: string; insight: string };
  topCreator: CreatorMetrics | null;
  dailyData: DailyKPI[];
  followUps: FollowUp[];
}

export interface ProjectKPI {
  label: string;
  thisWeek: string | number;
  lastWeek: string | number;
  change: string;
  target: string;
  status: 'green' | 'yellow' | 'red';
}

export interface taskItem {
  id: string;
  title: string;
  assignee: string;
  platform: Platform;
  status: taskStatus;
  progress: number;
  deadline: string;
  delayReason?: string;
  highlight?: string;
  businessValue?: string;
}

export interface TaskRetro {
  summary: { total: number; completed: number; delayed: number; completionRate: number };
  tasks: taskItem[];
  followUps: FollowUp[];
}

export interface RiskItem {
  id: string;
  level: RiskLevel;
  conclusion: string;
  reason: string;
  impact: string;
  affectedPlatform?: Platform;
  affectedCreator?: string;
  followUps: FollowUp[];
}

export interface FollowUp {
  id: string;
  question: string;
}

export interface PlatformData {
  platform: Platform;
  name: string;
  color: string;
  icon: string;
}

export interface HeroSummary {
  period: string;
  lines: {
    emoji: string;
    label: string;
    value: string;
    trend: 'up' | 'down' | 'neutral';
    status: RiskLevel;
    note: string;
  }[];
}

export interface WeeklyReport {
  heroSummary: HeroSummary;
  platformData: PlatformData[];
  kpiAnalysis: KPIModule[];
  projectKPI: ProjectKPI[];
  taskRetro: TaskRetro;
  risks: RiskItem[];
  nextWeekPlan: NextWeekPlan;
}

export interface NextWeekPlan {
  period: string;
  focus: string;
  tasks: NextWeekTask[];
}

export interface NextWeekTask {
  id: string;
  title: string;
  platform: Platform;
  assignee: string;
  startDate: string;
  endDate: string;
  priority: 'high' | 'medium' | 'low';
  status: string;
}
