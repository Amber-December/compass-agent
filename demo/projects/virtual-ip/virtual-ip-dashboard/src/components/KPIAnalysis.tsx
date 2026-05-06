'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { KPIModule, Platform, DailyKPI, ProjectKPI } from '@/types';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Filler, Tooltip, Legend);

interface Props { 
  modules: KPIModule[]; 
  projectKPI?: ProjectKPI[];
}

const platformConfig: Record<Platform, { name: string; color: string; label: string }> = {
  douyin: { name: 'Douyin', color: '#6366F1', label: '抖音' },
  kuaishou: { name: 'Kuaishou', color: '#F59E0B', label: '快手' },
  redbook: { name: 'Redbook', color: '#EF4444', label: '小红书' },
  bilibili: { name: 'Bilibili', color: '#06B6D4', label: 'B站' },
};

function formatNumber(n: number): string {
  if (n >= 100000000) return (n / 100000000).toFixed(1) + '亿';
  if (n >= 10000) return (n / 10000).toFixed(1) + '万';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toString();
}

function formatGMV(n: number): string {
  if (n >= 10000000) return (n / 10000000).toFixed(2) + '千万';
  if (n >= 10000) return (n / 10000).toFixed(0) + '万';
  return n.toString();
}

function TrendBadge({ change, unit = '' }: { change: number; unit?: string }) {
  const isUp = change > 0;
  const color = isUp ? 'var(--success)' : 'var(--danger)';
  const bg = isUp ? 'var(--success-bg)' : 'var(--danger-bg)';
  return (<span className="inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded-full" style={{ background: bg, color }}>{isUp ? '↑' : '↓'}{Math.abs(change).toFixed(1)}{unit === '%' || unit === 'pp' ? unit : ''}</span>);
}

const chartDefaults = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } };

function GMVLineChart({ data, color }: { data: DailyKPI[]; color: string }) {
  const labels = data.map(d => d.date.split('-').slice(1).join('/'));
  const chartData = { labels, datasets: [{ label: '本周', data: data.map(d => d.gmv), borderColor: color, backgroundColor: color + '15', tension: 0.4, fill: true, pointRadius: 2, pointHoverRadius: 5, borderWidth: 2 }] };
  const options = { ...chartDefaults, plugins: { ...chartDefaults.plugins, tooltip: { callbacks: { label: (ctx: unknown) => ` ¥${formatGMV((ctx as { raw: number }).raw)}` }, backgroundColor: 'rgba(15, 23, 42, 0.9)', padding: 8, titleFont: { size: 10 }, bodyFont: { size: 10 } } }, scales: { x: { display: false }, y: { display: false, ticks: { callback: (v: string | number) => formatGMV(Number(v)) } } } };
  return <Line data={chartData} options={options as never} />;
}

function ConversionBarChart({ data, color }: { data: DailyKPI[]; color: string }) {
  const labels = data.map(d => d.date.split('-').slice(1).join('/'));
  const chartData = { labels, datasets: [{ label: '转化率', data: data.map(d => d.conversionRate), backgroundColor: color + 'CC', borderColor: color, borderWidth: 1, borderRadius: 3, borderSkipped: false }] };
  const options = { ...chartDefaults, plugins: { ...chartDefaults.plugins, tooltip: { callbacks: { label: (ctx: unknown) => ` ${(ctx as { raw: number }).raw}%` }, backgroundColor: 'rgba(15, 23, 42, 0.9)', padding: 8 } }, scales: { x: { display: false }, y: { display: false } } };
  return <Bar data={chartData} options={options as never} />;
}

function ViewsDoughnutChart({ data, color }: { data: DailyKPI[]; color: string }) {
  const totalViews = data.reduce((sum, d) => sum + d.views, 0);
  const totalOrders = data.reduce((sum, d) => sum + d.orders, 0);
  const totalFans = data.reduce((sum, d) => sum + d.fans, 0);
  const chartData = { labels: ['曝光', '订单', '粉丝'], datasets: [{ data: [totalViews, totalOrders * 1000, totalFans * 10000], backgroundColor: [color + 'CC', color + '70', color + '30'], borderColor: [color, color, color], borderWidth: 1, hoverOffset: 4 }] };
  const options = { ...chartDefaults, plugins: { legend: { display: true, position: 'bottom' as const, labels: { font: { size: 9 }, color: '#94A3B8', padding: 6, usePointStyle: true, pointStyleWidth: 5 } }, tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', padding: 6 } }, cutout: '68%' };
  return <Doughnut data={chartData} options={options as never} />;
}

const statusLabels: Record<string, string> = { normal: '正常', warning: '风险', critical: '异常' };
const statusDotColors: Record<string, string> = { normal: 'var(--success)', warning: 'var(--warning)', critical: 'var(--danger)' };

function ProjectKPITable({ kpis }: { kpis: ProjectKPI[] }) {
  const statusColors: Record<string, { bg: string; text: string }> = {
    green: { bg: 'var(--success-bg)', text: 'var(--success)' },
    yellow: { bg: 'var(--warning-bg)', text: 'var(--warning)' },
    red: { bg: 'var(--danger-bg)', text: 'var(--danger)' },
  };

  return (
    <div className="card p-5 mb-5 overflow-x-auto">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'var(--success-bg)' }}>
          <svg width="18" height="18" viewBox="0 0 16 16" fill="none" style={{ color: 'var(--success)' }}>
            <rect x="1" y="3" width="14" height="10" rx="1.5" stroke="currentColor" strokeWidth="1.2"/>
            <path d="M1 6H15" stroke="currentColor" strokeWidth="1.2"/>
            <path d="M5 1V3M11 1V3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
        </div>
        <span className="text-base font-bold" style={{ color: 'var(--foreground)' }}>核心指标追踪</span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: 'var(--text-tertiary)' }}>
            <th className="text-left py-2 font-medium pr-4">指标</th>
            <th className="text-right py-2 font-medium px-4">本周</th>
            <th className="text-right py-2 font-medium px-4">上周</th>
            <th className="text-right py-2 font-medium px-4">环比</th>
            <th className="text-right py-2 font-medium px-4">目标</th>
            <th className="text-center py-2 font-medium pl-4">状态</th>
          </tr>
        </thead>
        <tbody>
          {kpis.map((kpi, i) => {
            const colors = statusColors[kpi.status];
            return (
              <tr key={i} className="border-t" style={{ borderColor: 'var(--border-subtle)' }}>
                <td className="py-3 pr-4 font-medium" style={{ color: 'var(--foreground)' }}>{kpi.label}</td>
                <td className="text-right py-3 px-4 font-bold" style={{ color: 'var(--foreground)' }}>{kpi.thisWeek}</td>
                <td className="text-right py-3 px-4" style={{ color: 'var(--text-secondary)' }}>{kpi.lastWeek}</td>
                <td className="text-right py-3 px-4">
                  <span className={`inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded-full ${kpi.change.startsWith('-') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                    {kpi.change.startsWith('-') ? '↓' : '↑'}{Math.abs(parseFloat(kpi.change)).toFixed(0)}
                    {kpi.change.includes('%') ? '%' : ''}
                  </span>
                </td>
                <td className="text-right py-3 px-4" style={{ color: 'var(--text-tertiary)' }}>{kpi.target}</td>
                <td className="text-center py-3 pl-4">
                  <span className="inline-flex items-center justify-center w-6 h-6 rounded-full" style={{ background: colors.bg }}>
                    {kpi.status === 'green' && <span style={{ color: colors.text }}>●</span>}
                    {kpi.status === 'yellow' && <span style={{ color: colors.text }}>◐</span>}
                    {kpi.status === 'red' && <span style={{ color: colors.text }}>○</span>}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function KPIAnalysis({ modules, projectKPI }: Props) {
  const [activePlatform, setActivePlatform] = useState<Platform>(modules[0]?.platform || 'douyin');
  const activeModule = modules.find(m => m.platform === activePlatform) || modules[0];
  const totalGMV = modules.reduce((sum, m) => sum + m.gmv.value, 0);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 flex flex-col justify-center">
        <div className="content-container mx-auto w-full max-w-7xl">
          {projectKPI && projectKPI.length > 0 && <ProjectKPITable kpis={projectKPI} />}

          <div className="card p-4 flex-shrink-0 mb-4">
            <div className="flex items-center gap-5">
              <div className="flex-shrink-0 pr-3 border-r" style={{ borderColor: 'var(--border)' }}>
                <div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>全平台虚拟IP总曝光</div>
                <div className="text-xl font-bold" style={{ color: 'var(--foreground)' }}>{formatNumber(totalGMV)}</div>
              </div>
              <div className="flex gap-2.5 flex-1 overflow-x-auto">
                {modules.map(m => {
                  const cfg = platformConfig[m.platform];
                  const pct = ((m.gmv.value / totalGMV) * 100).toFixed(1);
                  const isActive = activePlatform === m.platform;
                  return (<button key={m.platform} onClick={() => setActivePlatform(m.platform)} className="flex-shrink-0 flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl transition-all duration-200 cursor-pointer" style={{ background: isActive ? cfg.color + '15' : 'transparent', border: `1.5px solid ${isActive ? cfg.color + '40' : 'transparent'}` }}>
                    <div className="flex items-center gap-2"><span className="text-sm font-bold" style={{ color: isActive ? cfg.color : 'var(--text-secondary)' }}>{cfg.label}</span><span className="w-2 h-2 rounded-full" style={{ background: statusDotColors[m.status] }} /></div>
                    <div className="text-xs font-medium" style={{ color: 'var(--text-tertiary)' }}>{pct}% · {formatNumber(m.gmv.value)}</div>
                  </button>);
                })}
              </div>
            </div>
          </div>

          <div className="flex gap-3 min-h-0">
            {activeModule && (
              <div className="w-96 flex-shrink-0 flex flex-col gap-3">
                <div className="card p-4 flex-shrink-0">
                  <div className="flex items-center gap-2.5 mb-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white text-base" style={{ background: platformConfig[activeModule.platform].color }}>{platformConfig[activeModule.platform].label.charAt(0)}</div>
                    <div>
                      <div className="flex items-center gap-2"><span className="text-base font-bold" style={{ color: 'var(--foreground)' }}>{platformConfig[activeModule.platform].label}</span><span className="text-xs font-medium px-1.5 py-0.5 rounded-full" style={{ background: activeModule.status === 'normal' ? 'var(--success-bg)' : activeModule.status === 'warning' ? 'var(--warning-bg)' : 'var(--danger-bg)', color: activeModule.status === 'normal' ? 'var(--success)' : activeModule.status === 'warning' ? 'var(--warning)' : 'var(--danger)' }}>{statusLabels[activeModule.status]}</span></div>
                      <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>IP曝光量 {formatNumber(activeModule.gmv.value)}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2.5">
                    <div className="p-3 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>曝光量</div><div className="text-lg font-bold" style={{ color: platformConfig[activeModule.platform].color }}>{formatNumber(activeModule.gmv.value)}</div><TrendBadge change={activeModule.gmv.change} /></div>
                    <div className="p-3 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>互动率</div><div className="text-lg font-bold" style={{ color: platformConfig[activeModule.platform].color }}>{activeModule.conversionRate.value.toFixed(1)}%</div><TrendBadge change={activeModule.conversionRate.change} unit="%" /></div>
                    <div className="p-3 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>粉丝增长</div><div className="text-lg font-bold" style={{ color: platformConfig[activeModule.platform].color }}>{formatNumber(activeModule.views.value)}</div><TrendBadge change={activeModule.views.change} /></div>
                    <div className="p-3 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>商业价值</div><div className="text-lg font-bold" style={{ color: platformConfig[activeModule.platform].color }}>{activeModule.fans.value > 0 ? '+' + formatNumber(activeModule.fans.value) : formatNumber(activeModule.fans.value)}</div><TrendBadge change={activeModule.fans.change} /></div>
                  </div>
                </div>
                <div className="card p-3 flex-1 min-h-0"><div className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>曝光趋势</div><div className="flex-1 min-h-0" style={{ minHeight: '100px' }}><GMVLineChart data={activeModule.dailyData} color={platformConfig[activeModule.platform].color} /></div></div>
              </div>
            )}
            <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
              <div className="card p-3 flex flex-col"><div className="flex items-center justify-between mb-2"><span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>互动率走势</span><TrendBadge change={activeModule?.conversionRate.change || 0} unit="%" /></div><div className="flex-1 min-h-0" style={{ minHeight: '120px' }}><ConversionBarChart data={activeModule?.dailyData || []} color={platformConfig[activeModule?.platform || 'douyin'].color} /></div></div>
              <div className="card p-3 flex flex-col"><span className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>IP运营统计</span><div className="grid grid-cols-3 gap-2 mb-3"><div className="text-center p-2 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xl font-bold" style={{ color: 'var(--accent)' }}>12</div><div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>运营IP数</div></div><div className="text-center p-2 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xl font-bold" style={{ color: 'var(--success)' }}>580万</div><div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>总粉丝</div></div><div className="text-center p-2 rounded-lg" style={{ background: 'var(--surface-muted)' }}><div className="text-xl font-bold" style={{ color: 'var(--warning)' }}>8.5%</div><div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>平均互动</div></div></div><div className="text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>各平台IP分布</div><div className="flex-1 min-h-0" style={{ minHeight: '80px' }}><Doughnut data={{ labels: ['抖音', '快手', '小红书', 'B站'], datasets: [{ data: [5, 3, 2, 2], backgroundColor: ['#6366F1', '#F59E0B', '#EF4444', '#06B6D4'], borderWidth: 0, spacing: 2 }] }} options={{ responsive: true, maintainAspectRatio: false, cutout: '60%', plugins: { legend: { position: 'right', labels: { boxWidth: 10, padding: 8, font: { size: 10 } } } } }} /></div></div>
              <div className="card p-3 col-span-2 flex flex-col"><span className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>每日数据明细</span><div className="flex-1 overflow-auto" style={{ maxHeight: '120px' }}><table className="w-full text-xs"><thead><tr style={{ color: 'var(--text-tertiary)' }}><th className="text-left py-1 font-medium">日期</th><th className="text-right py-1 font-medium">曝光量</th><th className="text-right py-1 font-medium">互动率</th><th className="text-right py-1 font-medium">粉丝增长</th><th className="text-right py-1 font-medium">商业价值</th></tr></thead><tbody>{activeModule?.dailyData.map((d, i) => (<tr key={i} className="border-t" style={{ borderColor: 'var(--border-subtle)' }}><td className="py-1" style={{ color: 'var(--foreground)' }}>{d.date}</td><td className="text-right py-1 font-medium" style={{ color: platformConfig[activeModule.platform].color }}>{formatNumber(d.gmv)}</td><td className="text-right py-1">{d.conversionRate.toFixed(1)}%</td><td className="text-right py-1">{d.fans > 0 ? '+' + d.fans : d.fans}</td><td className="text-right py-1">{formatNumber(d.views)}</td></tr>))}</tbody></table></div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
