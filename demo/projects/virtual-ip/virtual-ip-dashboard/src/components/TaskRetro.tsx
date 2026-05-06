'use client';
import { useState } from 'react';
import { TaskRetro as TaskRetroType, TaskItem } from '@/types';

interface Props { data: TaskRetroType; }

const platformMeta: Record<string, { label: string; color: string; bg: string }> = { douyin: { label: '抖音', color: '#6366F1', bg: '#EEF2FF' }, kuaishou: { label: '快手', color: '#F59E0B', bg: '#FFFBEB' }, redbook: { label: '小红书', color: '#EF4444', bg: '#FEF2F2' }, bilibili: { label: 'B站', color: '#06B6D4', bg: '#ECFEFF' } };
const statusMeta: Record<string, { label: string; color: string; bg: string; border: string }> = { completed: { label: '已完成', color: 'var(--success)', bg: 'var(--success-bg)', border: 'var(--success-light)' }, in_progress: { label: '进行中', color: 'var(--accent)', bg: 'var(--accent-light)', border: 'var(--accent-border)' }, delayed: { label: '已延期', color: 'var(--danger)', bg: 'var(--danger-bg)', border: 'var(--danger-light)' }, pending: { label: '待开始', color: 'var(--text-tertiary)', bg: 'var(--surface-muted)', border: 'var(--border-subtle)' } };

function GanttChart({ tasks }: { tasks: TaskItem[] }) {
  // Parse week dates (假设本周从4月27日到5月3日)
  const weekStart = new Date('2026-04-27');
  const weekDays = ['4/27', '4/28', '4/29', '4/30', '5/1', '5/2', '5/3'];
  const totalDays = 7;
  
  // Get deadline day index (relative to week start)
  const getDayIndex = (deadline: string) => {
    const d = new Date(deadline);
    const diff = Math.floor((d.getTime() - weekStart.getTime()) / (1000 * 60 * 60 * 24));
    return Math.min(Math.max(diff, 0), totalDays - 1);
  };
  
  return (
    <div className="mt-3">
      {/* Day headers */}
      <div className="flex mb-1.5 pl-20">
        {weekDays.map((day, i) => (
          <div key={i} className="flex-1 text-center text-[10px]" style={{ color: 'var(--text-tertiary)' }}>{day}</div>
        ))}
      </div>
      {/* Timeline grid */}
      <div className="relative">
        {/* Vertical grid lines */}
        <div className="absolute inset-0 flex pointer-events-none">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex-1 border-l" style={{ borderColor: i > 0 && i < 7 ? 'var(--border-subtle)' : 'transparent' }} />
          ))}
        </div>
        {/* Task bars */}
        <div className="space-y-1.5 relative z-10">
          {tasks.slice(0, 6).map((task) => {
            const meta = platformMeta[task.platform] || platformMeta.douyin;
            const endDay = getDayIndex(task.deadline);
            // Calculate bar position: each day is 1/7 of the width
            const barStart = 0; // Start from day 0
            const barEnd = ((endDay + 0.8) / totalDays) * 100; // End at ~deadline
            
            return (
              <div key={task.id} className="flex items-center h-6">
                <div className="w-20 flex-shrink-0 pr-2">
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: meta.color }} />
                    <span className="text-[10px] truncate" style={{ color: 'var(--foreground)' }}>{task.title.substring(0, 8)}</span>
                  </div>
                </div>
                <div className="flex-1 relative h-4">
                  {/* Background bar (full timeline) */}
                  <div 
                    className="absolute h-2 top-1 rounded-sm"
                    style={{ 
                      left: `${barStart}%`,
                      width: `${barEnd}%`,
                      background: 'var(--surface-muted)',
                    }}
                  />
                  {/* Status bar */}
                  {task.status === 'completed' && (
                    <div 
                      className="absolute h-2 top-1 rounded-sm flex items-center justify-end pr-1"
                      style={{ 
                        left: `${barStart}%`,
                        width: `${barEnd}%`,
                        background: meta.color,
                      }}
                    >
                      <svg width="6" height="6" viewBox="0 0 8 8" fill="none"><path d="M1.5 4L3.2 5.7L6.5 2" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    </div>
                  )}
                  {task.status === 'delayed' && (
                    <div 
                      className="absolute h-2 top-1 rounded-sm flex items-center justify-end pr-1"
                      style={{ 
                        left: `${barStart}%`,
                        width: '100%',
                        background: 'var(--danger)',
                        opacity: 0.7,
                      }}
                    >
                      <svg width="6" height="6" viewBox="0 0 8 8" fill="none"><path d="M4 2.5V4.5L5.5 6" stroke="white" strokeWidth="1.5" strokeLinecap="round"/></svg>
                    </div>
                  )}
                  {task.status === 'in_progress' && (
                    <>
                      <div 
                        className="absolute h-2 top-1 rounded-l-sm"
                        style={{ 
                          left: `${barStart}%`,
                          width: `${(barEnd * task.progress) / 100}%`,
                          background: meta.color,
                        }}
                      />
                      <div 
                        className="absolute h-2 top-1 rounded-sm border-2"
                        style={{ 
                          left: `${barStart}%`,
                          width: `${barEnd}%`,
                          borderColor: meta.color,
                          background: 'transparent',
                        }}
                      />
                    </>
                  )}
                  {/* Deadline marker */}
                  <div 
                    className="absolute top-0 bottom-0 w-0.5 rounded-full"
                    style={{ 
                      left: `${barEnd}%`,
                      background: task.status === 'delayed' ? 'var(--danger)' : 'var(--text-tertiary)',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 pt-2" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-2 rounded-sm" style={{ background: 'var(--success)' }} />
          <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>已完成</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-2 rounded-sm border-2" style={{ borderColor: 'var(--accent)' }} />
          <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>进行中</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-2 rounded-sm" style={{ background: 'var(--danger)' }} />
          <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>已延期</span>
        </div>
      </div>
    </div>
  );
}

function TaskItemRow({ task }: { task: TaskItem }) {
  const [expanded, setExpanded] = useState(false);
  const meta = platformMeta[task.platform] || platformMeta.douyin;
  const status = statusMeta[task.status] || statusMeta.pending;
  const isExpandable = task.delayReason || task.highlight || task.businessValue;
  return (
    <div className="rounded-lg border transition-all duration-150" style={{ background: 'var(--surface)', borderColor: task.status === 'delayed' ? 'var(--danger-light)' : 'var(--border-subtle)', boxShadow: task.status === 'delayed' ? '0 1px 3px rgba(239,68,68,0.08)' : 'none' }}>
      <div className="flex items-center gap-3 px-4 py-2.5 cursor-pointer" onClick={() => isExpandable && setExpanded(!expanded)} style={{ cursor: isExpandable ? 'pointer' : 'default' }}>
        <div className="flex-shrink-0">{task.status === 'completed' ? (<div className="w-4 h-4 rounded-full flex items-center justify-center" style={{ background: status.color }}><svg width="8" height="8" viewBox="0 0 8 8" fill="none"><path d="M1.5 4L3.2 5.7L6.5 2" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/></svg></div>) : task.status === 'delayed' ? (<div className="w-4 h-4 rounded-full flex items-center justify-center" style={{ background: status.color }}><svg width="8" height="8" viewBox="0 0 8 8" fill="none"><path d="M4 2.5V4.5L5.5 6" stroke="white" strokeWidth="1.2" strokeLinecap="round"/></svg></div>) : task.status === 'in_progress' ? (<div className="w-4 h-4 rounded-full flex items-center justify-center border-2" style={{ borderColor: status.color }}><div className="w-1.5 h-1.5 rounded-full" style={{ background: status.color }} /></div>) : (<div className="w-4 h-4 rounded-full border-2" style={{ borderColor: 'var(--border)' }} />)}</div>
        <div className="flex-shrink-0"><span className="text-xs font-semibold px-1.5 py-0.5 rounded" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span></div>
        <div className="flex-1 min-w-0"><span className="text-sm font-medium truncate" style={{ color: task.status === 'delayed' ? 'var(--danger)' : 'var(--foreground)' }}>{task.title}</span></div>
        <div className="flex-shrink-0 hidden sm:block"><span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{task.assignee}</span></div>
        <div className="flex items-center gap-2 flex-shrink-0 w-24"><div className="flex-1 h-1 bg-slate-100 rounded-full overflow-hidden"><div className="h-full rounded-full transition-all duration-500" style={{ width: `${task.progress}%`, background: task.status === 'delayed' ? 'var(--danger)' : task.status === 'completed' ? 'var(--success)' : meta.color }} /></div><span className="text-xs font-medium flex-shrink-0" style={{ color: 'var(--text-secondary)', width: '28px', textAlign: 'right' }}>{task.progress}%</span></div>
        <div className="flex-shrink-0"><span className="text-xs font-medium px-2 py-0.5 rounded-full" style={{ background: status.bg, color: status.color }}>{status.label}</span></div>
        {isExpandable && <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ color: 'var(--text-tertiary)', transform: expanded ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s ease', flexShrink: 0 }}><path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/></svg>}
      </div>
      {expanded && isExpandable && (
        <div className="px-4 pb-3 pt-1" style={{ borderTop: `1px solid ${task.status === 'delayed' ? 'var(--danger-light)' : 'var(--border-subtle)'}` }}>
          <div className="space-y-2 pl-7">
            {task.delayReason && <div className="flex items-start gap-2"><div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ background: 'var(--danger)' }} /><p className="text-xs" style={{ color: 'var(--danger)' }}>{task.delayReason}</p></div>}
            {task.highlight && <div className="flex items-start gap-2"><div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ background: 'var(--success)' }} /><p className="text-xs font-medium" style={{ color: 'var(--success)' }}>{task.highlight}</p></div>}
            {task.businessValue && <div className="flex items-start gap-2"><div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ background: meta.color }} /><p className="text-xs" style={{ color: 'var(--text-secondary)' }}>业务价值：{task.businessValue}</p></div>}
          </div>
        </div>
      )}
    </div>
  );
}

function ProgressHeatmap({ tasks }: { tasks: TaskItem[] }) {
  const platformOrder = ['douyin', 'kuaishou', 'redbook', 'bilibili'];
  const platforms = platformOrder.filter(p => tasks.some(t => t.platform === p));
  const maxTasks = Math.max(...platforms.map(p => tasks.filter(t => t.platform === p).length), 1);
  return (
    <div className="mb-2">
      <div className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>各平台IP孵化任务完成进度</div>
      <div className="flex gap-3">
        {platforms.map(platform => { const meta = platformMeta[platform]; const platformTasks = tasks.filter(t => t.platform === platform); const completed = platformTasks.filter(t => t.status === 'completed').length; const total = platformTasks.length; const pct = total > 0 ? Math.round((completed / total) * 100) : 0; return (<div key={platform} className="flex-1 min-w-0"><div className="flex items-center justify-between mb-1"><span className="text-xs font-medium truncate" style={{ color: meta.color }}>{meta.label}</span><span className="text-xs font-semibold flex-shrink-0" style={{ color: 'var(--foreground)' }}>{pct}%</span></div><div className="flex gap-1">{Array.from({ length: maxTasks }).map((_, i) => { const task = platformTasks[i]; const filled = !!task; const status = task?.status || 'empty'; const colors: Record<string, string> = { completed: meta.color, in_progress: meta.color + '50', delayed: 'var(--danger)', empty: 'var(--border-subtle)' }; return (<div key={i} className="flex-1 h-4 sm:h-5 rounded-sm transition-all duration-150" style={{ background: filled ? colors[status] : colors.empty }} title={task ? `${task.title} - ${statusMeta[task.status]?.label}` : ''} />); })}</div></div>); })}
      </div>
    </div>
  );
}

export default function TaskRetro({ data }: Props) {
  const { summary, tasks } = data;
  const platformOrder = ['douyin', 'kuaishou', 'redbook', 'bilibili'];
  const tasksByPlatform = platformOrder.map(platform => ({ platform, tasks: tasks.filter(t => t.platform === platform), delayedCount: tasks.filter(t => t.platform === platform && t.status === 'delayed').length })).filter(g => g.tasks.length > 0);
  const [activePlatform, setActivePlatform] = useState<string | null>(null);
  const completionRateColor = summary.completionRate >= 90 ? 'var(--success)' : summary.completionRate >= 75 ? 'var(--warning)' : 'var(--danger)';
  return (
    <div>
      <div className="card p-5 mb-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5"><div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'var(--success-bg)' }}><svg width="16" height="16" viewBox="0 0 14 14" fill="none" style={{ color: 'var(--success)' }}><path d="M2.5 7L5.5 10L11.5 4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg></div><span className="text-base font-bold" style={{ color: 'var(--foreground)' }}>本周IP孵化任务概览</span></div>
          <div className="flex items-center gap-2"><span className="text-3xl font-bold" style={{ color: completionRateColor }}>{summary.completionRate}%</span><span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>完成率</span></div>
        </div>
        <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-4"><div className="h-full rounded-full transition-all duration-700" style={{ width: `${summary.completionRate}%`, background: completionRateColor }} /></div>
        <div className="flex gap-2.5 overflow-x-auto pb-1">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg flex-shrink-0" style={{ background: 'var(--surface-muted)' }}><span className="text-base font-bold" style={{ color: 'var(--foreground)' }}>{summary.total}</span><span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>总任务</span></div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg flex-shrink-0" style={{ background: 'var(--success-bg)' }}><span className="text-base font-bold" style={{ color: 'var(--success)' }}>{summary.completed}</span><span className="text-xs" style={{ color: 'var(--success)' }}>已完成</span></div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg flex-shrink-0" style={{ background: 'var(--danger-bg)' }}><span className="text-base font-bold" style={{ color: 'var(--danger)' }}>{summary.delayed}</span><span className="text-xs" style={{ color: 'var(--danger)' }}>已延期</span></div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg flex-shrink-0" style={{ background: 'var(--surface-muted)' }}><span className="text-base font-bold" style={{ color: 'var(--foreground)' }}>{summary.total - summary.completed - summary.delayed}</span><span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>进行中</span></div>
        </div>
        <GanttChart tasks={tasks} />
      </div>
      <div className="card p-5 mb-5"><ProgressHeatmap tasks={tasks} /></div>
      <div className="grid grid-cols-2 gap-4">{tasksByPlatform.map(({ platform, tasks: pTasks }) => { const meta = platformMeta[platform]; const delayedCount = pTasks.filter(t => t.status === 'delayed').length; const completedCount = pTasks.filter(t => t.status === 'completed').length; const total = pTasks.length; const pct = total > 0 ? Math.round((completedCount / total) * 100) : 0; return (<button key={platform} onClick={() => setActivePlatform(platform === activePlatform ? null : platform)} className="card p-4 w-full text-left transition-all duration-150 cursor-pointer" style={{ border: `1px solid ${platform === activePlatform ? meta.color + '50' : 'var(--border-subtle)'}`, boxShadow: platform === activePlatform ? `0 2px 8px ${meta.color}15` : 'none' }}><div className="flex items-center gap-2 mb-2"><div className="w-1.5 h-6 rounded-full" style={{ background: meta.color }} /><span className="text-sm font-bold" style={{ color: meta.color }}>{meta.label}</span>{delayedCount > 0 && <span className="text-xs px-1.5 py-0.5 rounded-full font-medium" style={{ background: 'var(--danger-bg)', color: 'var(--danger)', marginLeft: 'auto' }}>{delayedCount}延期</span>}</div><div className="text-xs mb-2" style={{ color: 'var(--text-tertiary)' }}>{total} 项任务 · {completedCount} 完成</div><div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden"><div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: meta.color }} /></div></button>); })}</div>
      {activePlatform && (() => { const pTasks = tasks.filter(t => t.platform === activePlatform); const meta = platformMeta[activePlatform] || platformMeta.douyin; const delayedCount = pTasks.filter(t => t.status === 'delayed').length; return (<div className="card p-4 mt-3"><div className="flex items-center gap-2 mb-3"><div className="w-1 h-4 rounded-full" style={{ background: meta.color }} /><span className="text-sm font-bold" style={{ color: meta.color }}>{meta.label}</span><span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{pTasks.length} 项任务</span>{delayedCount > 0 && <span className="text-xs px-1.5 py-0.5 rounded-full font-medium" style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>{delayedCount} 延期</span>}<button onClick={() => setActivePlatform(null)} className="ml-auto text-xs px-2 py-0.5 rounded-lg transition-colors cursor-pointer" style={{ color: 'var(--text-tertiary)', background: 'var(--surface-muted)' }}>收起</button></div>{pTasks.map(task => <TaskItemRow key={task.id} task={task} />)}</div>); })()}
    </div>
  );
}
