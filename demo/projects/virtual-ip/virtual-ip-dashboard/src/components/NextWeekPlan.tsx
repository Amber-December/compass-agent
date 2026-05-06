'use client';
import { NextWeekPlan as NextWeekPlanType, NextWeekTask } from '@/types';

interface Props { data: NextWeekPlanType; }

const platformMeta: Record<string, { label: string; color: string; bg: string }> = {
  douyin: { label: '抖音', color: '#6366F1', bg: '#EEF2FF' },
  kuaishou: { label: '快手', color: '#F59E0B', bg: '#FFFBEB' },
  redbook: { label: '小红书', color: '#EF4444', bg: '#FEF2F2' },
  bilibili: { label: 'B站', color: '#06B6D4', bg: '#ECFEFF' }
};

const priorityMeta: Record<string, { label: string; color: string; bg: string }> = {
  high: { label: '高优', color: 'var(--danger)', bg: 'var(--danger-bg)' },
  medium: { label: '中优', color: 'var(--warning)', bg: 'var(--warning-bg)' },
  low: { label: '低优', color: 'var(--text-tertiary)', bg: 'var(--surface-muted)' }
};

function SimpleGantt({ tasks }: { tasks: NextWeekTask[] }) {
  const weekDays = ['5/4', '5/5', '5/6', '5/7', '5/8', '5/9', '5/10'];
  const totalDays = 7;
  
  const getDayIndex = (dateStr: string) => {
    const start = new Date('2026-05-04');
    const d = new Date(dateStr);
    const diff = Math.floor((d.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    return Math.max(0, Math.min(diff, totalDays - 1));
  };
  
  return (
    <div className="mt-4">
      {/* Day headers */}
      <div className="flex mb-2 pl-32">
        {weekDays.map((day, i) => (
          <div key={i} className="flex-1 text-center text-[10px] font-medium" style={{ color: 'var(--text-tertiary)' }}>
            {day}
          </div>
        ))}
      </div>
      
      {/* Gantt bars */}
      <div className="space-y-2">
        {tasks.slice(0, 6).map((task) => {
          const meta = platformMeta[task.platform] || platformMeta.douyin;
          const priority = priorityMeta[task.priority] || priorityMeta.medium;
          const startIdx = getDayIndex(task.startDate);
          const endIdx = getDayIndex(task.endDate);
          // 32 units = 128px offset for task label column
          const leftOffset = 128;
          const barAreaWidth = 100; // percentage of the bar area
          const leftPct = (startIdx / totalDays) * barAreaWidth;
          const widthPct = ((endIdx - startIdx + 1) / totalDays) * barAreaWidth;
          
          return (
            <div key={task.id} className="flex items-center h-8">
              {/* Task info */}
              <div className="w-32 flex-shrink-0 pr-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ background: priority.color }} />
                  <span className="text-xs truncate font-medium" style={{ color: 'var(--foreground)' }}>{task.title}</span>
                </div>
              </div>
              {/* Gantt bar - uses absolute positioning with pixel offset */}
              <div 
                className="flex-1 relative h-full rounded-sm"
                style={{ 
                  background: 'var(--border-subtle)',
                }}
              >
                <div 
                  className="absolute top-1 bottom-1 rounded-md flex items-center px-2"
                  style={{ 
                    left: `${leftPct}%`,
                    width: `${Math.max(widthPct, 8)}%`,
                    background: meta.color + '20',
                    border: `1.5px solid ${meta.color}`,
                  }}
                >
                  <span className="text-[10px] font-medium truncate" style={{ color: meta.color }}>
                    {task.assignee}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Legend */}
      <div className="flex items-center gap-5 mt-4 pt-3" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm" style={{ background: priorityMeta.high.bg, border: '1.5px solid var(--danger)' }} />
          <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>高优先级</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm" style={{ background: priorityMeta.medium.bg, border: '1.5px solid var(--warning)' }} />
          <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>中优先级</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm" style={{ background: priorityMeta.low.bg, border: '1.5px solid var(--text-tertiary)' }} />
          <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>低优先级</span>
        </div>
      </div>
    </div>
  );
}

function TaskCard({ task }: { task: NextWeekTask }) {
  const meta = platformMeta[task.platform] || platformMeta.douyin;
  const priority = priorityMeta[task.priority] || priorityMeta.medium;
  
  return (
    <div className="card p-4 transition-all duration-150" style={{ border: `1px solid ${meta.color}30` }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white text-sm" style={{ background: meta.color }}>
            {meta.label.charAt(0)}
          </div>
          <div>
            <div className="text-sm font-bold" style={{ color: 'var(--foreground)' }}>{task.title}</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{task.assignee}</div>
          </div>
        </div>
        <span className="text-xs font-semibold px-2 py-1 rounded-full" style={{ background: priority.bg, color: priority.color }}>
          {priority.label}
        </span>
      </div>
      <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--text-tertiary)' }}>
        <div className="flex items-center gap-1">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <rect x="1" y="2" width="10" height="9" rx="1.5" stroke="currentColor" strokeWidth="1"/>
            <path d="M4 1V3M8 1V3" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
            <path d="M1 5H11" stroke="currentColor" strokeWidth="1"/>
          </svg>
          <span>{task.startDate} ~ {task.endDate}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: meta.color }} />
          <span>{meta.label}</span>
        </div>
      </div>
    </div>
  );
}

export default function NextWeekPlan({ data }: Props) {
  const { period, focus, tasks } = data;
  const highPriority = tasks.filter(t => t.priority === 'high');
  const mediumPriority = tasks.filter(t => t.priority === 'medium');
  const lowPriority = tasks.filter(t => t.priority === 'low');
  
  return (
    <div>
      {/* Header */}
      <div className="card p-5 mb-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, var(--accent), var(--accent-dark))' }}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{ color: 'white' }}>
                <path d="M10 2V4M10 16V18M4 10H2M18 10H16M5.64 5.64L4.22 4.22M15.78 15.78L14.36 14.36M5.64 14.36L4.22 15.78M15.78 4.22L14.36 5.64" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight" style={{ color: 'var(--foreground)' }}>下周工作计划</span>
              <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{period}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold" style={{ color: 'var(--accent)' }}>{tasks.length}</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>项任务</div>
          </div>
        </div>
        
        {/* Focus area */}
        <div className="p-4 rounded-xl mb-5" style={{ background: 'var(--accent-bg)', border: '1px solid var(--accent-border)' }}>
          <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--accent)' }}>本周重点</div>
          <div className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{focus}</div>
        </div>
        
        {/* Summary stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="p-4 rounded-xl text-center" style={{ background: 'var(--danger-bg)' }}>
            <div className="text-2xl font-bold" style={{ color: 'var(--danger)' }}>{highPriority.length}</div>
            <div className="text-xs" style={{ color: 'var(--danger)' }}>高优先级</div>
          </div>
          <div className="p-4 rounded-xl text-center" style={{ background: 'var(--warning-bg)' }}>
            <div className="text-2xl font-bold" style={{ color: 'var(--warning)' }}>{mediumPriority.length}</div>
            <div className="text-xs" style={{ color: 'var(--warning)' }}>中优先级</div>
          </div>
          <div className="p-4 rounded-xl text-center" style={{ background: 'var(--surface-muted)' }}>
            <div className="text-2xl font-bold" style={{ color: 'var(--text-tertiary)' }}>{lowPriority.length}</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>低优先级</div>
          </div>
        </div>
        
        {/* Gantt chart */}
        <SimpleGantt tasks={tasks} />
      </div>
      
      {/* Task cards by priority */}
      <div className="space-y-5">
        {highPriority.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-1.5 h-5 rounded-full" style={{ background: 'var(--danger)' }} />
              <span className="text-sm font-bold" style={{ color: 'var(--danger)' }}>高优先级任务</span>
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>{highPriority.length}</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {highPriority.map(task => <TaskCard key={task.id} task={task} />)}
            </div>
          </div>
        )}
        
        {mediumPriority.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-1.5 h-5 rounded-full" style={{ background: 'var(--warning)' }} />
              <span className="text-sm font-bold" style={{ color: 'var(--warning)' }}>中优先级任务</span>
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}>{mediumPriority.length}</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {mediumPriority.map(task => <TaskCard key={task.id} task={task} />)}
            </div>
          </div>
        )}
        
        {lowPriority.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-1.5 h-5 rounded-full" style={{ background: 'var(--text-tertiary)' }} />
              <span className="text-sm font-bold" style={{ color: 'var(--text-secondary)' }}>低优先级任务</span>
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--surface-muted)', color: 'var(--text-tertiary)' }}>{lowPriority.length}</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {lowPriority.map(task => <TaskCard key={task.id} task={task} />)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
