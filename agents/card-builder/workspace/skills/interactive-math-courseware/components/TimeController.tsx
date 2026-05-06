'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export type SkyPeriod = 'night' | 'dawn' | 'day' | 'dusk';

interface TimeControllerProps {
  time: number;
  onTimeChange: (time: number) => void;
  isPlaying: boolean;
  onPlayPause: () => void;
  speed?: number;
  onSpeedChange?: (speed: number) => void;
  month?: number;
  onMonthChange?: (month: number) => void;
  skyPeriod?: SkyPeriod;
  className?: string;
}

const MONTH_NAMES = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

export default function TimeController({
  time,
  onTimeChange,
  isPlaying,
  onPlayPause,
  speed = 1,
  onSpeedChange,
  month = 5,
  onMonthChange,
  skyPeriod = 'day',
  className = ''
}: TimeControllerProps) {
  const formatTime = (t: number) => {
    const hours = Math.floor(t);
    const minutes = Math.floor((t - hours) * 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  };

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
      transition={{ delay: 0.3 }}
    >
      <h3 className={`text-sm font-medium mb-4 flex items-center gap-2 ${getTextColor()}`}>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        时间控制
      </h3>

      <div className={`text-3xl font-bold mb-4 ${getTextColor()}`}>
        {formatTime(time)}
      </div>

      <div className="mb-4">
        <input
          type="range"
          min="0"
          max="24"
          step="0.1"
          value={time}
          onChange={(e) => onTimeChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
        />
        <div className={`flex justify-between text-xs mt-1 ${getSubTextColor()}`}>
          <span>00:00</span>
          <span>12:00</span>
          <span>24:00</span>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={onPlayPause}
          className="flex-1 py-2 px-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
        >
          {isPlaying ? (
            <><svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> 暂停</>
          ) : (
            <><svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg> 播放</>
          )}
        </button>
        {onSpeedChange && (
          <select
            value={speed}
            onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            className="py-2 px-3 bg-slate-100 rounded-lg text-sm"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={5}>5x</option>
          </select>
        )}
      </div>

      {onMonthChange && (
        <div>
          <label className={`text-xs mb-2 block ${getSubTextColor()}`}>月份</label>
          <div className="grid grid-cols-6 gap-1">
            {MONTH_NAMES.map((name, i) => (
              <button
                key={i}
                onClick={() => onMonthChange(i)}
                className={`py-1 px-2 text-xs rounded transition-colors ${
                  month === i
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
              >
                {name}
              </button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
