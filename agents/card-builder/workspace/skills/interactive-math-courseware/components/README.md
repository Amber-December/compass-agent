# components 使用说明

这是一组可直接复制到项目中的 React 组件，用于构建日晷/天文类交互课件。

## 依赖
- React 18+
- Three.js (`three`)
- Framer Motion (`framer-motion`)
- Tailwind CSS

## 组件清单

### Sundial3D
3D 日晷模拟器核心组件。

```tsx
import Sundial3D from '@/components/Sundial3D';
import { useRef } from 'react';

const sundialRef = useRef<{ setView: (view: 'front' | 'free') => void }>(null);

<Sundial3D
  ref={sundialRef}
  time={12}        // 0-24
  latitude={40}    // 北纬度数
  month={5}        // 0-11
  skyColors={{ top: '#e0f2fe', bottom: '#bae6fd' }}
  isNight={false}
  onSunPositionChange={(pos) => console.log(pos.altitude)}
/>

// 切换视角
sundialRef.current?.setView('front');
```

### TimeController
时间控制面板（滑块、播放、速度、月份）。

```tsx
import TimeController from '@/components/TimeController';

<TimeController
  time={time}
  onTimeChange={setTime}
  isPlaying={isPlaying}
  onPlayPause={() => setIsPlaying(!isPlaying)}
  speed={speed}
  onSpeedChange={setSpeed}
  month={month}
  onMonthChange={setMonth}
  skyPeriod="day"
/>
```

### LocationSelector
地理位置选择（纬度滑块 + 预设城市）。

```tsx
import LocationSelector from '@/components/LocationSelector';

<LocationSelector
  latitude={latitude}
  onLatitudeChange={setLatitude}
  skyPeriod="day"
/>
```

## 完整示例

```tsx
'use client';
import { useState } from 'react';
import Sundial3D from '@/components/Sundial3D';
import TimeController from '@/components/TimeController';
import LocationSelector from '@/components/LocationSelector';
import { getSkyColors, getSkyPeriod } from '@/lib/astronomy';

export default function SundialPage() {
  const [time, setTime] = useState(12);
  const [latitude, setLatitude] = useState(40);
  const [month, setMonth] = useState(5);
  const [isPlaying, setIsPlaying] = useState(false);

  const skyColors = getSkyColors(time);
  const skyPeriod = getSkyPeriod(time, month, latitude);

  return (
    <div className="min-h-screen p-4">
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 h-[500px]">
          <Sundial3D
            time={time}
            latitude={latitude}
            month={month}
            skyColors={skyColors}
          />
        </div>
        <div className="space-y-4">
          <TimeController
            time={time}
            onTimeChange={setTime}
            isPlaying={isPlaying}
            onPlayPause={() => setIsPlaying(!isPlaying)}
            month={month}
            onMonthChange={setMonth}
            skyPeriod={skyPeriod}
          />
          <LocationSelector
            latitude={latitude}
            onLatitudeChange={setLatitude}
            skyPeriod={skyPeriod}
          />
        </div>
      </div>
    </div>
  );
}
```

## 设计原则
1. 组件与业务逻辑解耦，只接收 props 和回调
2. 支持 `skyPeriod` 驱动的动态主题（day/dusk/dawn/night）
3. 使用 Framer Motion 做入场动画
4. Three.js 部分已做 SSR 安全处理
