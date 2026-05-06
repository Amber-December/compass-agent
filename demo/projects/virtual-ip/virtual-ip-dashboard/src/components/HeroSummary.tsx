'use client';
import { useEffect, useRef, useState } from 'react';
import React from 'react';
import { HeroSummary as HeroSummaryType } from '@/types';

interface Props { data: HeroSummaryType; }

const platformMeta: Record<string, { accent: string; bg: string; icon: React.ReactElement }> = {
  'IP孵化数': { accent: '#3B82F6', bg: '#EFF6FF', icon: (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2L10 6L14 7L11 10L12 14L8 12L4 14L5 10L2 7L6 6L8 2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>) },
  '粉丝总量': { accent: '#10B981', bg: '#ECFDF5', icon: (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.3"/><path d="M2 14C2 11.2 4.7 9 8 9C11.3 9 14 11.2 14 14" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>) },
  '互动率': { accent: '#8B5CF6', bg: '#F5F3FF', icon: (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2C5 2 2 4 2 7C2 9 3.5 10.5 5 11.5L8 14L14 8C14 5 12 2 8 2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>) },
  '商业价值': { accent: '#F59E0B', bg: '#FFFBEB', icon: (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2V14M5 5H10.5C11.5 5 12 5.5 12 6.5C12 7.5 11.5 8 10.5 8H5H10.5C11.5 8 12 8.5 12 9.5C12 10.5 11.5 11 10.5 11H5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>) },
  '内容产出': { accent: '#06B6D4', bg: '#ECFEFF', icon: (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.3"/><path d="M5 8L7 10L11 6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>) },
};

function SparklineCanvas({ values, color }: { values: number[]; color: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => { setReady(true); }, []);
  useEffect(() => {
    if (!ready) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    const w = rect.width, h = rect.height, pad = 2;
    const min = Math.min(...values), max = Math.max(...values);
    const range = max - min || 1;
    const step = (w - pad * 2) / (values.length - 1);
    const points = values.map((v, i) => ({ x: pad + i * step, y: pad + (1 - (v - min) / range) * (h - pad * 2) }));
    ctx.clearRect(0, 0, w, h);
    const areaGradient = ctx.createLinearGradient(0, 0, 0, h);
    areaGradient.addColorStop(0, color + '40');
    areaGradient.addColorStop(1, color + '00');
    ctx.beginPath();
    ctx.moveTo(points[0].x, h);
    points.forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.lineTo(points[points.length - 1].x, h);
    ctx.closePath();
    ctx.fillStyle = areaGradient;
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    ctx.stroke();
    const last = points[points.length - 1];
    ctx.beginPath();
    ctx.arc(last.x, last.y, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }, [ready, values, color]);
  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} className="sparkline-canvas" />;
}

const sparklineData: Record<string, { values: number[]; trend: 'up' | 'down' | 'neutral' }> = {
  'IP孵化数': { values: [8, 9, 10, 11, 12, 12, 12], trend: 'up' },
  '粉丝总量': { values: [420, 460, 510, 540, 560, 575, 580], trend: 'up' },
  '互动率': { values: [6.2, 6.8, 7.2, 7.5, 8.0, 8.2, 8.5], trend: 'up' },
  '商业价值': { values: [85, 92, 105, 115, 128, 140, 150], trend: 'up' },
  '内容产出': { values: [28, 32, 35, 38, 42, 45, 48], trend: 'up' },
};

const statusColors: Record<string, string> = { normal: 'var(--success)', warning: 'var(--warning)', critical: 'var(--danger)' };

export default function HeroSummary({ data }: Props) {
  return (
    <div className="card p-5 sm:p-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg flex items-center justify-center" style={{ background: 'var(--accent-light)' }}>
            <svg width="12" height="12" viewBox="0 0 14 14" fill="none" style={{ color: 'var(--accent)' }}><path d="M2 10L5 6.5L7.5 8.5L12 3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </div>
          <h2 className="text-sm font-bold" style={{ color: 'var(--foreground)' }}>本周虚拟IP孵化战报</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}>Week 17</span>
          <span className="text-xs px-2 py-0.5 rounded-full font-medium hidden sm:inline" style={{ background: 'var(--surface-muted)', color: 'var(--text-secondary)' }}>{data.period}</span>
        </div>
      </div>
      <div className="hero-stat-grid grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-5">
        {data.lines.map((line, i) => {
          const meta = platformMeta[line.label] || platformMeta['IP孵化数'];
          const spark = sparklineData[line.label] || sparklineData['IP孵化数'];
          const statusColor = statusColors[line.status] || statusColors.normal;
          return (
            <div key={i} className="hero-stat-card relative rounded-xl p-4 sm:p-5 card-hover cursor-default group" style={{ background: meta.bg, border: `1px solid ${meta.accent}20` }}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: meta.accent + '20', color: meta.accent }}>{meta.icon}</div>
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: statusColor, animation: line.status !== 'normal' ? 'pulse-dot 2s ease-in-out infinite' : 'none' }} />
              </div>
              <div className="mb-1">
                <span className="stat-value" style={{ color: line.status === 'critical' ? 'var(--danger)' : line.status === 'warning' ? 'var(--warning)' : meta.accent, animation: `countUp 0.5s ease-out ${i * 0.08}s forwards`, opacity: 0, fontSize: '30px' }}>{line.value}</span>
              </div>
              <div className="text-base mb-3" style={{ color: meta.accent }}>{line.label}</div>
              <div className="hero-sparkline h-12"><SparklineCanvas values={spark.values} color={meta.accent} trend={line.trend} /></div>
              <div className="mt-2 pt-2" style={{ borderTop: `1px solid ${meta.accent}15` }}>
                <div className="flex items-center gap-1.5 mb-0.5">
                  {line.trend === 'up' && <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ color: 'var(--success)' }}><path d="M5 2L9 6M5 2L2 6M5 2V8" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  {line.trend === 'down' && <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ color: 'var(--danger)' }}><path d="M5 8L2 4M5 8L8 4M5 8V2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  {line.trend === 'neutral' && <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ color: 'var(--text-secondary)' }}><path d="M2 5H8" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>}
                  <span className="text-xs font-medium truncate" style={{ color: 'var(--text-secondary)' }}>{line.note.split('，')[0]}</span>
                </div>
              </div>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 rounded-lg text-xs whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10" style={{ background: 'var(--foreground)', color: 'white', boxShadow: 'var(--shadow-md)' }}>
                {line.note}
                <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0" style={{ borderLeft: '5px solid transparent', borderRight: '5px solid transparent', borderTop: '5px solid var(--foreground)' }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
