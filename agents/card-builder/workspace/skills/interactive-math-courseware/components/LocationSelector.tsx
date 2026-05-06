'use client';

import { motion } from 'framer-motion';

export type SkyPeriod = 'night' | 'dawn' | 'day' | 'dusk';

interface LocationSelectorProps {
  latitude: number;
  onLatitudeChange: (lat: number) => void;
  skyPeriod?: SkyPeriod;
  className?: string;
}

const PRESET_LOCATIONS = [
  { name: '哈尔滨', lat: 45.8 },
  { name: '北京', lat: 39.9 },
  { name: '上海', lat: 31.2 },
  { name: '广州', lat: 23.1 },
  { name: '海口', lat: 20.0 },
];

export default function LocationSelector({
  latitude,
  onLatitudeChange,
  skyPeriod = 'day',
  className = ''
}: LocationSelectorProps) {
  const getCardBg = () => {
    if (skyPeriod === 'night') return 'bg-slate-800/90 border-slate-600/50';
    if (skyPeriod === 'dusk' || skyPeriod === 'dawn') return 'bg-slate-700/80 border-slate-500/50';
    return 'bg-white/90 border-slate-200/80';
  };

  const getTextColor = () => {
    if (skyPeriod === 'night') return 'text-slate-100';
    if (skyPeriod === 'dusk' || skyPeriod === 'dawn') return 'text-slate-200';
    return 'text-slate-800';
  };

  const getSubTextColor = () => {
    if (skyPeriod === 'night') return 'text-slate-400';
    if (skyPeriod === 'dusk' || skyPeriod === 'dawn') return 'text-slate-400';
    return 'text-slate-500';
  };

  return (
    <motion.div
      className={`rounded-2xl p-4 shadow-xl backdrop-blur-sm border transition-all duration-1000 ${getCardBg()} ${className}`}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.4 }}
    >
      <h3 className={`text-sm font-medium mb-4 flex items-center gap-2 ${getTextColor()}`}>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        地理位置
      </h3>

      <div className={`text-2xl font-bold mb-4 ${getTextColor()}`}>
        {latitude.toFixed(1)}°N
      </div>

      <div className="mb-4">
        <input
          type="range"
          min="0"
          max="60"
          step="0.1"
          value={latitude}
          onChange={(e) => onLatitudeChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
        />
        <div className={`flex justify-between text-xs mt-1 ${getSubTextColor()}`}>
          <span>赤道 0°</span>
          <span>北纬 60°</span>
        </div>
      </div>

      <div>
        <label className={`text-xs mb-2 block ${getSubTextColor()}`}>快速选择</label>
        <div className="flex flex-wrap gap-2">
          {PRESET_LOCATIONS.map((loc) => (
            <button
              key={loc.name}
              onClick={() => onLatitudeChange(loc.lat)}
              className={`py-1.5 px-3 text-sm rounded-lg transition-colors ${
                Math.abs(latitude - loc.lat) < 1
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              {loc.name}
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
