# sundial_v3 项目复盘（日晷交互式课件）

## 项目定位
- 类型：日晷交互式课件（天文/科学教育）
- 目标：通过 3D 日晷模拟器，让学生理解太阳运动、影子形成、纬度影响、季节变化
- 技术栈：Next.js + React + TypeScript + Three.js + Framer Motion + Tailwind CSS

## 核心创新点

### 1) Three.js 3D 日晷模拟器
- 动态生成 Canvas 纹理作为表盘（12 时辰 + 24 小时刻度）
- 手动实现简易 OrbitControls（支持视角切换、拖拽、缩放）
- 实时计算太阳位置（基于纬度、月份、时间）
- 影子实时跟随太阳光照

### 2) 真实天文计算
- 赤纬计算：`23.44 * sin((360/365)*(dayOfYear-81))`
- 太阳高度角：`sin(alt) = sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(hourAngle)`
- 季节映射：冬/夏/春秋分三套天空颜色渐变

### 3) 日夜循环系统
- 天空颜色随时间平滑过渡（lerpColor 插值）
- 星空（90 颗预定义星星）仅在夜间显示
- 白云/火烧云/朝霞根据时段条件渲染
- 光照强度随太阳高度角变化

### 4) 教学模块设计
- 6 个知识卡片（原理、影子形成、太阳视运动、纬度、四季、历史）
- 卡片背景色随天空时段动态变化（day/dusk/dawn/night）
- 展开/收起动画，知识点分条展示

## 关键经验（可迁移）

### 天文模拟类课件的核心模式
1. **数学模型先行**：先搞定赤纬、太阳高度角、方位角计算，再做 3D 渲染
2. **预计算 + 插值**：天空颜色用 lookup table + lerp，避免实时复杂计算
3. **视角预设**：提供"读数视角"（固定）和"自由视角"（可交互）两种模式
4. **SSR 安全**：星空数据预定义在组件内，避免 hydration mismatch

### Three.js 最佳实践
- 纹理用 Canvas 动态生成（可编程、可本地化）
- 光照与环境光配合，夜晚降低强度
- 材质自发光（emissive）确保夜间可见性
- 手动实现 OrbitControls 减少依赖体积

### 视觉设计
- 背景渐变与 UI 卡片颜色联动（skyPeriod 驱动）
- 装饰性 SVG 元素（星座、指南针、沙漏、日晷符号）增强氛围
- 流星动画（CSS keyframes）增加生动感

## 可复用代码资产

### 1) 天空颜色插值系统
```ts
const skyMap = [
  { h: 0, t: "#111827", b: "#020617" },
  { h: 5.5, t: "#312e81", b: "#1e1b4b" },
  // ...
];
function lerpColor(c1: string, c2: string, factor: number): string
function getSkyColors(hour: number): { top: string; bottom: string }
```

### 2) 太阳位置计算
```ts
function getSunPosition(time: number, latitude: number, month: number): {
  x: number; y: number; z: number; altitude: number;
}
```

### 3) 季节判断
```ts
type SkyPeriod = 'night' | 'dawn' | 'day' | 'dusk';
function getSkyPeriod(hour: number, month: number, latitude: number): SkyPeriod;
```

### 4) 动态 Canvas 纹理生成器
```ts
function createDialTexture(labels: string[], options: DialOptions): THREE.CanvasTexture;
```

## 与 rational-course_v4 的对比

| 维度 | rational-course_v4（转盘锁） | sundial_v3（日晷） |
|------|---------------------------|-------------------|
| 核心交互 | 2D SVG + Framer Motion | 3D Three.js |
| 数学模型 | 环形刻度 + 正负数 | 天文计算 + 球面坐标 |
| 时间维度 | 单步推进（离散） | 连续时间 + 动画循环 |
| 视觉重点 | 故事化（海盗寻宝） | 真实模拟（天文现象） |
| 可复用层 | 转盘逻辑、步骤播放器 | 天空系统、太阳计算器、3D 控制器 |

## 结论

sundial_v3 展示了"科学模拟类课件"的另一种范式：
- **真实性优先**：基于真实天文公式，而非简化规则
- **连续体验**：时间滑块 + 动画循环，而非单步点击
- **多维变量**：时间、纬度、月份三个维度同时影响结果

其核心可复用资产是：**天空渲染系统 + 天文计算库 + 3D 交互控制器**。
