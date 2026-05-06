'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { demoReport } from '@/data/demoData';
import HeroSummary from '@/components/HeroSummary';
import KPIAnalysis from '@/components/KPIAnalysis';
import TaskRetro from '@/components/TaskRetro';
import RiskAlert from '@/components/RiskAlert';
import NextWeekPlan from '@/components/NextWeekPlan';

type NavSection = 'overview' | 'kpi' | 'tasks' | 'risks' | 'nextweek';
type SectionMeta = {
  id: NavSection;
  label: string;
  icon: React.ReactNode;
  accent: string;
  gradient: string;
};

const sections: SectionMeta[] = [
  { id: 'overview', label: '周报总览', icon: (<svg width="18" height="18" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.3" fill="currentColor" fillOpacity="0.15"/><rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.3" fill="currentColor" fillOpacity="0.15"/><rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.3" fill="currentColor" fillOpacity="0.25"/><rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.3" fill="currentColor" fillOpacity="0.08"/></svg>), accent: '#3B82F6', gradient: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(96, 165, 250, 0.10))' },
  { id: 'kpi', label: '本周数据看板', icon: (<svg width="18" height="18" viewBox="0 0 16 16" fill="none"><path d="M2 12L5.5 7L8.5 9.5L14 3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/><circle cx="14" cy="3" r="1.5" fill="currentColor"/></svg>), accent: '#10B981', gradient: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.10))' },
  { id: 'tasks', label: '任务复盘', icon: (<svg width="18" height="18" viewBox="0 0 16 16" fill="none"><rect x="1" y="2.5" width="11" height="2.5" rx="1.25" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1.2"/><rect x="1" y="6.75" width="11" height="2.5" rx="1.25" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1.2"/><rect x="1" y="11" width="7" height="2.5" rx="1.25" fill="currentColor" fillOpacity="0.45" stroke="currentColor" strokeWidth="1.2"/></svg>), accent: '#8B5CF6', gradient: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.10))' },
  { id: 'risks', label: '风险识别', icon: (<svg width="18" height="18" viewBox="0 0 16 16" fill="none"><path d="M8 2L10 6.5L14.5 7L11.5 10.5L12.5 15L8 12.5L3.5 15L4.5 10.5L1.5 7L6 6.5L8 2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>), accent: '#EF4444', gradient: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.10))' },
  { id: 'nextweek', label: '下周计划', icon: (<svg width="18" height="18" viewBox="0 0 16 16" fill="none"><path d="M8 2V4M8 12V14M4 8H2M14 8H16M5.64 5.64L4.22 4.22M11.78 11.78L10.36 10.36M5.64 10.36L4.22 11.78M11.78 4.22L10.36 5.64" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/><circle cx="8" cy="8" r="2.5" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1.2"/></svg>), accent: '#F59E0B', gradient: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.10))' },
];

function ScrollDots({ activeSection, onNavigate }: { activeSection: NavSection; onNavigate: (id: NavSection) => void }) {
  return (<div className="scroll-dots">{sections.map((section) => { const isActive = activeSection === section.id; return (<button key={section.id} className="scroll-dot" onClick={() => onNavigate(section.id)} title={section.label} style={isActive ? { background: section.accent, borderColor: section.accent, boxShadow: `0 0 12px ${section.accent}80`, transform: 'scale(1.4)', width: '10px', height: '10px' } : {}} />); })}</div>);
}

function SectionHeader({ title, badge, accent }: { title: string; badge?: string; accent: string }) {
  return (<div className="flex items-center gap-3 mb-5 px-1"><div className="w-1 h-6 xl:h-7 2xl:h-8 rounded-full flex-shrink-0" style={{ background: `linear-gradient(180deg, ${accent}, ${accent}80)`, boxShadow: `0 0 8px ${accent}50` }} /><h2 className="text-lg sm:text-xl xl:text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{title}</h2>{badge && <span className="text-xs font-medium px-2.5 py-0.5 rounded-full" style={{ background: `${accent}15`, color: accent, border: `1px solid ${accent}30` }}>{badge}</span>}</div>);
}

function ScrollHint({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (<div className="scroll-hint"><span className="scroll-hint-text">向下滚动翻页</span><svg className="scroll-hint-arrow" viewBox="0 0 20 20" fill="none"><path d="M10 4V16M10 16L5 11M10 16L15 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg></div>);
}

function OrbDecorations() {
  return (<><div className="orb orb-purple" style={{ width: '500px', height: '500px', top: '-150px', right: '5%', opacity: 0.12 }} /><div className="orb orb-violet" style={{ width: '400px', height: '400px', bottom: '5%', left: '-50px', opacity: 0.1 }} /><div className="orb orb-fuchsia" style={{ width: '300px', height: '300px', top: '30%', right: '2%', opacity: 0.08 }} /></>);
}

function CatalogNav({ activeSection, onNavigate, period }: { activeSection: NavSection; onNavigate: (id: NavSection) => void; period: string }) {
  const current = sections.find(s => s.id === activeSection) || sections[0];
  return (
    <div className="w-full" style={{ padding: '20px 24px', borderTop: '1px solid rgba(255,255,255,0.3)' }}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-500" style={{ background: `linear-gradient(135deg, ${current.accent}, ${current.accent}99)`, boxShadow: `0 0 16px ${current.accent}40` }}>
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="white" strokeWidth="1.5"/><path d="M10 5C7.5 5 5 7 5 10C5 12.5 7 15 10 16" stroke="white" strokeWidth="1.5" strokeLinecap="round"/><circle cx="10" cy="10" r="2" fill="white"/></svg>
          </div>
          <div className="hidden sm:block"><p className="text-xs font-bold" style={{ color: 'var(--foreground)' }}>Virtual IP</p><p className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>{period}</p></div>
        </div>
        <div className="flex items-center gap-1 flex-1 justify-center min-w-0 overflow-x-auto">
          {sections.map((section, index) => { const isActive = activeSection === section.id; const isPast = sections.findIndex(s => s.id === activeSection) > index; return (<div key={section.id} className="flex items-center gap-1 flex-shrink-0"><button onClick={() => onNavigate(section.id)} className="relative flex items-center gap-2 px-3 py-2 rounded-xl transition-all duration-400 cursor-pointer" style={isActive ? { background: section.gradient, border: `1.5px solid ${section.accent}40`, boxShadow: `0 0 16px ${section.accent}20` } : { background: 'rgba(255,255,255,0.45)', border: `1.5px solid ${isPast ? section.accent + '25' : 'rgba(255,255,255,0.5)'}`, opacity: isPast ? 0.6 : 0.45 }}><span style={{ color: isActive ? section.accent : 'var(--text-secondary)', transition: 'color 0.3s ease' }}>{section.icon}</span><span className="text-xs font-medium whitespace-nowrap hidden sm:inline transition-colors duration-300" style={{ color: isActive ? section.accent : 'var(--text-secondary)' }}>{section.label}</span>{isActive && <span className="absolute -bottom-px left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full" style={{ background: section.accent, boxShadow: `0 0 8px ${section.accent}` }} />}</button>{index < sections.length - 1 && <div className="w-4 h-px mx-0.5 flex-shrink-0 transition-opacity duration-300" style={{ background: `linear-gradient(90deg, ${sections[index].accent}40, ${sections[index + 1].accent}40)` }} />}</div>); })}
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold flex-shrink-0 transition-all duration-300" style={{ background: `${current.accent}15`, color: current.accent, border: `1.5px solid ${current.accent}30` }}><span className="w-1.5 h-1.5 rounded-full" style={{ background: current.accent, boxShadow: `0 0 6px ${current.accent}` }} /><span className="hidden md:inline">{current.label}</span></div>
      </div>
    </div>
  );
}

export default function Home() {
  const report = demoReport;
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeSection, setActiveSection] = useState<NavSection>('overview');
  const [showScrollHint, setShowScrollHint] = useState(true);
  const [isScrolling, setIsScrolling] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
          const id = entry.target.getAttribute('data-section') as NavSection;
          if (id && id !== activeSection) {
            setIsTransitioning(true);
            setTimeout(() => { setActiveSection(id); if (id !== 'overview') setShowScrollHint(false); }, 150);
            setTimeout(() => { setIsTransitioning(false); }, 500);
          }
        }
      });
    }, { root: container, threshold: 0.5 });
    container.querySelectorAll('[data-section]').forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [activeSection]);

  const navigateTo = useCallback((id: NavSection) => {
    const container = containerRef.current;
    if (!container || id === activeSection) return;
    setIsTransitioning(true);
    setIsScrolling(true);
    const target = container.querySelector(`[data-section="${id}"]`) as HTMLElement;
    if (target) { container.scrollTo({ top: target.offsetTop - container.offsetTop, behavior: 'smooth' }); }
    setTimeout(() => { setActiveSection(id); if (id !== 'overview') setShowScrollHint(false); }, 150);
    if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
    scrollTimeoutRef.current = setTimeout(() => { setIsScrolling(false); setIsTransitioning(false); }, 700);
  }, [activeSection]);

  return (
    <div className="relative">
      <OrbDecorations />
      <div className={`scroll-overlay ${isScrolling ? 'visible' : ''}`} style={{ pointerEvents: isScrolling ? 'auto' : 'none' }} />
      <div className={`page-crossfade-overlay ${isTransitioning ? 'active' : ''}`} />
      <ScrollDots activeSection={activeSection} onNavigate={navigateTo} />
      <div ref={containerRef} className="snap-container">
        <section data-section="overview" className="snap-section relative flex flex-col">
          <div className="flex-[2] flex flex-col justify-end px-4 md:px-8 xl:px-10 pb-2 pt-8">
            <div className="content-container mx-auto w-full">
              <div className="flex items-center gap-2 mb-1"><div className="w-2 h-2 rounded-full" style={{ background: 'linear-gradient(135deg, var(--accent), var(--gradient-mid))', boxShadow: '0 0 8px rgba(59, 130, 246, 0.5)' }} /><span className="text-xs font-semibold tracking-wider uppercase" style={{ color: 'var(--accent)' }}>Virtual IP Bulletin</span></div>
              <h1 className="hero-title text-4xl sm:text-5xl xl:text-6xl 2xl:text-7xl font-extrabold tracking-tight" style={{ color: 'var(--foreground)' }}>虚拟IP孵化战报</h1>
              <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>Week 17 · {report.heroSummary.period} · 虚拟IP矩阵运营数据一屏尽览</p>
            </div>
          </div>
          <div className="flex-[5] flex items-center px-4 md:px-8 xl:px-10 py-4"><div className="content-container mx-auto w-full"><div className="card-animate-in"><HeroSummary data={report.heroSummary} /></div></div></div>
          <div className="glass-nav mx-4 mb-4 rounded-2xl flex-shrink-0"><CatalogNav activeSection={activeSection} onNavigate={navigateTo} period={report.heroSummary.period} /></div>
          <ScrollHint visible={showScrollHint} />
        </section>
        <section data-section="kpi" className="snap-section relative px-4 md:px-8 xl:px-10 py-4 flex flex-col">
          <div className="flex-1 flex flex-col justify-center min-h-0 content-container mx-auto w-full"><div className="mb-3"><SectionHeader title="本周数据看板" badge="核心指标追踪" accent="var(--success)" /></div><div className="card-animate-in"><KPIAnalysis modules={report.kpiAnalysis} projectKPI={report.projectKPI} /></div></div>
          <div className="glass-nav mx-4 mb-4 rounded-2xl flex-shrink-0 mt-4"><CatalogNav activeSection={activeSection} onNavigate={navigateTo} period={report.heroSummary.period} /></div>
        </section>
        <section data-section="tasks" className="snap-section relative px-4 md:px-8 xl:px-10 py-4 flex flex-col">
          <div className="flex-1 flex flex-col justify-center min-h-0 content-container mx-auto w-full">
            <div className="flex-shrink-0 flex gap-4 mb-3"><div className="flex-1"><SectionHeader title="任务复盘" badge="本周执行回顾" accent="var(--accent)" /></div><div className="w-48 flex-shrink-0"><div className="card p-3"><div className="text-xs font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>完成率</div><div className="flex items-end gap-2"><span className="text-2xl font-bold" style={{ color: 'var(--accent)' }}>{report.taskRetro.summary.completionRate}%</span><span className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>完成</span></div></div></div></div>
            <div className="card-animate-in"><TaskRetro data={report.taskRetro} /></div>
          </div>
          <div className="glass-nav mx-4 mb-4 rounded-2xl flex-shrink-0 mt-4"><CatalogNav activeSection={activeSection} onNavigate={navigateTo} period={report.heroSummary.period} /></div>
        </section>
        <section data-section="risks" className="snap-section relative px-4 md:px-8 xl:px-10 py-4 flex flex-col">
          <div className="flex-1 flex flex-col justify-center min-h-0"><div className="content-container mx-auto w-full flex-shrink-0 mb-3"><SectionHeader title="风险识别" badge="本周风险评估" accent="var(--danger)" /></div><div className="content-container mx-auto w-full card-animate-in overflow-y-auto pr-1"><RiskAlert risks={report.risks} /></div></div>
          <div className="glass-nav mx-4 mb-4 rounded-2xl flex-shrink-0 mt-4"><CatalogNav activeSection={activeSection} onNavigate={navigateTo} period={report.heroSummary.period} /></div>
        </section>
        <section data-section="nextweek" className="snap-section relative px-4 md:px-8 xl:px-10 py-4 flex flex-col">
          <div className="flex-1 flex flex-col justify-center min-h-0 content-container mx-auto w-full">
            <div className="mb-3"><SectionHeader title="下周计划" badge="2026年第19周" accent="var(--accent)" /></div>
            <div className="card-animate-in"><NextWeekPlan data={report.nextWeekPlan} /></div>
          </div>
          <div className="glass-nav mx-4 mb-4 rounded-2xl flex-shrink-0 mt-4"><CatalogNav activeSection={activeSection} onNavigate={navigateTo} period={report.heroSummary.period} /></div>
        </section>
      </div>
    </div>
  );
}
