'use client';

import { useState } from 'react';
import React from 'react';
import { RiskItem as RiskItemType, RiskLevel } from '@/types';

interface Props { risks: RiskItemType[]; }

const levelMeta: Record<RiskLevel, { label: string; color: string; bg: string; border: string; textColor: string; Icon: () => React.ReactElement }> = {
  critical: { label: '高风险', color: 'var(--danger)', bg: 'var(--danger-bg)', border: 'var(--danger-light)', textColor: 'var(--danger)', Icon: () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2L14.5 13.5H1.5L8 2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/><path d="M8 6.5V9" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/><circle cx="8" cy="10.5" r="0.6" fill="currentColor"/></svg>) },
  warning: { label: '中风险', color: 'var(--warning)', bg: 'var(--warning-bg)', border: 'var(--warning-light)', textColor: 'var(--warning)', Icon: () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.3"/><path d="M8 5V8.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/><circle cx="8" cy="10.5" r="0.6" fill="currentColor"/></svg>) },
  normal: { label: '低风险', color: 'var(--success)', bg: 'var(--success-bg)', border: 'var(--success-light)', textColor: 'var(--success)', Icon: () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.3"/><path d="M5.5 8L7 9.5L10.5 6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>) },
};

// Mock readers data
const mockReaders = [
  { name: '张伟', avatar: '张', time: '10:23' },
  { name: '李娜', avatar: '李', time: '09:45' },
  { name: '王芳', avatar: '王', time: '08:12' },
];

function RiskCard({ risk, index }: { risk: RiskItemType; index: number }) {
  const [expanded, setExpanded] = useState(risk.level === 'critical' || index === 0);
  const [isRead, setIsRead] = useState(false);
  const [showReaders, setShowReaders] = useState(false);
  const meta = levelMeta[risk.level];
  const MetaIcon = meta.Icon;

  const handleMarkAsRead = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsRead(true);
  };

  return (
    <div className="rounded-xl border overflow-hidden transition-all duration-200" style={{ borderColor: expanded ? meta.color + '40' : meta.border, background: 'var(--surface)', boxShadow: expanded ? `0 2px 12px ${meta.color}10` : 'none' }}>
      <div className="flex items-center gap-3 px-4 py-3 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: meta.bg, color: meta.color }}><MetaIcon /></div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span>
            {risk.affectedPlatform && <span className="text-xs font-medium px-2 py-0.5 rounded-full" style={{ background: 'var(--surface-muted)', color: 'var(--text-secondary)' }}>{risk.affectedPlatform === 'douyin' ? '抖音' : risk.affectedPlatform === 'kuaishou' ? '快手' : risk.affectedPlatform === 'redbook' ? '小红书' : 'B站'}</span>}
            {risk.affectedCreator && <span className="text-xs font-medium px-2 py-0.5 rounded-full truncate" style={{ background: 'var(--surface-muted)', color: 'var(--text-secondary)' }}>{risk.affectedCreator}</span>}
          </div>
          <h4 className="text-base font-bold mt-1 truncate" style={{ color: meta.textColor }}>{risk.conclusion}</h4>
        </div>
        <div className="flex-shrink-0 flex items-center gap-2"><span className="text-xs hidden sm:block" style={{ color: 'var(--text-tertiary)' }}>{expanded ? '收起' : '详情'}</span><svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{ color: 'var(--text-tertiary)', transform: expanded ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s ease' }}><path d="M3 5L7 9L11 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/></svg></div>
      </div>
      {expanded && (
        <div className="px-4 pb-4 pt-0 animate-fade-in" style={{ borderTop: `1px solid ${meta.border}` }}>
          <div className="pt-3 space-y-3">
            <div className="flex gap-3"><div className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center mt-0.5" style={{ background: meta.bg }}><span className="text-xs font-bold" style={{ color: meta.color, fontSize: '10px' }}>1</span></div><div><p className="text-xs font-semibold mb-0.5" style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>原因分析</p><p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{risk.reason}</p></div></div>
            <div className="flex gap-3"><div className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center mt-0.5" style={{ background: meta.bg }}><span className="text-xs font-bold" style={{ color: meta.color, fontSize: '10px' }}>2</span></div><div><p className="text-xs font-semibold mb-0.5" style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>影响范围</p><p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{risk.impact}</p></div></div>
            
            {/* 已阅按钮区域 */}
            <div className="flex items-center justify-between pt-3 mt-2" style={{ borderTop: `1px dashed ${meta.border}` }}>
              <div className="flex items-center gap-2">
                {!isRead ? (
                  <button 
                    onClick={handleMarkAsRead}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer"
                    style={{ background: 'var(--success-bg)', color: 'var(--success)', border: '1px solid var(--success-light)' }}
                  >
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M3 8L6.5 11.5L13 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    标记已阅
                  </button>
                ) : (
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <button 
                        onClick={(e) => { e.stopPropagation(); setShowReaders(!showReaders); }}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer"
                        style={{ background: 'var(--success)', color: 'white', border: '1px solid var(--success)' }}
                      >
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M3 8L6.5 11.5L13 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                        已阅 ({mockReaders.length + 1}人)
                      </button>
                      {showReaders && (
                        <div className="absolute bottom-full left-0 mb-2 w-48 rounded-lg shadow-lg border overflow-hidden z-10" style={{ background: 'var(--surface)', borderColor: 'var(--border-subtle)' }}>
                          <div className="px-3 py-2 text-xs font-semibold" style={{ background: 'var(--surface-muted)', color: 'var(--text-secondary)' }}>
                            以下人员已阅
                          </div>
                          <div className="p-2 space-y-1.5">
                            {/* Current user */}
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg" style={{ background: 'var(--success-bg)' }}>
                              <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" style={{ background: 'var(--success)', color: 'white' }}>我</div>
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-medium truncate" style={{ color: 'var(--foreground)' }}>我</p>
                                <p className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>刚刚</p>
                              </div>
                              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" style={{ color: 'var(--success)' }}><path d="M3 8L6.5 11.5L13 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                            </div>
                            {/* Other readers */}
                            {mockReaders.map((reader, i) => (
                              <div key={i} className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">
                                <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" style={{ background: 'var(--accent)', color: 'white' }}>{reader.avatar}</div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-medium truncate" style={{ color: 'var(--foreground)' }}>{reader.name}</p>
                                  <p className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>{reader.time}</p>
                                </div>
                                <svg width="12" height="12" viewBox="0 0 16 16" fill="none" style={{ color: 'var(--success)' }}><path d="M3 8L6.5 11.5L13 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>点击卡片标题可展开详情</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function RiskAlert({ risks }: Props) {
  const criticalCount = risks.filter(r => r.level === 'critical').length;
  const warningCount = risks.filter(r => r.level === 'warning').length;
  const normalCount = risks.filter(r => r.level === 'normal').length;
  if (!risks || risks.length === 0) return (<div><div className="flex items-center gap-2 mb-4"><div className="w-1 h-5 rounded-full" style={{ background: 'var(--accent)' }} /><h2 className="text-base font-bold" style={{ color: 'var(--foreground)' }}>风险识别</h2><span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: 'var(--surface-muted)', color: 'var(--text-secondary)' }}>本周风险评估</span></div><div className="card p-8 text-center"><div className="w-12 h-12 rounded-full mx-auto flex items-center justify-center mb-3" style={{ background: 'var(--success-bg)' }}><svg width="24" height="24" viewBox="0 0 24 24" fill="none" style={{ color: 'var(--success)' }}><path d="M5 13L9 17L19 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></div><p className="font-medium" style={{ color: 'var(--foreground)' }}>本周暂无重大风险</p><p className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>所有IP运营指标均在可控范围内</p></div></div>);
  return (
    <div>
      <div className="flex gap-3 mb-4">
        <div className="flex-1 rounded-xl px-4 py-4 flex items-center gap-3" style={{ background: 'var(--danger-bg)', border: '1px solid var(--danger-light)' }}><svg width="20" height="20" viewBox="0 0 16 16" fill="none" style={{ color: 'var(--danger)' }}><path d="M8 2L14.5 13.5H1.5L8 2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/><path d="M8 6.5V9" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/><circle cx="8" cy="10.5" r="0.6" fill="currentColor"/></svg><span className="text-2xl font-bold" style={{ color: 'var(--danger)' }}>{criticalCount}</span><span className="text-sm font-medium" style={{ color: 'var(--danger)' }}>高风险</span></div>
        <div className="flex-1 rounded-xl px-4 py-4 flex items-center gap-3" style={{ background: 'var(--warning-bg)', border: '1px solid var(--warning-light)' }}><svg width="20" height="20" viewBox="0 0 16 16" fill="none" style={{ color: 'var(--warning)' }}><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.3"/><path d="M8 5V8.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/><circle cx="8" cy="10.5" r="0.6" fill="currentColor"/></svg><span className="text-2xl font-bold" style={{ color: 'var(--warning)' }}>{warningCount}</span><span className="text-sm font-medium" style={{ color: 'var(--warning)' }}>中风险</span></div>
        <div className="flex-1 rounded-xl px-4 py-4 flex items-center gap-3" style={{ background: 'var(--success-bg)', border: '1px solid var(--success-light)' }}><svg width="20" height="20" viewBox="0 0 16 16" fill="none" style={{ color: 'var(--success)' }}><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.3"/><path d="M5.5 8L7 9.5L10.5 6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg><span className="text-2xl font-bold" style={{ color: 'var(--success)' }}>{normalCount}</span><span className="text-sm font-medium" style={{ color: 'var(--success)' }}>低风险</span></div>
      </div>
      <div className="flex items-center gap-2 mb-5"><div className="w-1 h-5 rounded-full" style={{ background: 'var(--accent)' }} /><h2 className="text-base font-bold" style={{ color: 'var(--foreground)' }}>风险识别</h2><span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: 'var(--surface-muted)', color: 'var(--text-secondary)' }}>本周风险评估</span>{risks.length > 0 && <span className="text-xs px-2 py-0.5 rounded-full font-semibold" style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>{criticalCount > 0 ? `${criticalCount} 高` : `${warningCount} 中`}</span>}</div>
      <div className="space-y-3">{risks.map((risk, index) => <RiskCard key={risk.id} risk={risk} index={index} />)}</div>
    </div>
  );
}
