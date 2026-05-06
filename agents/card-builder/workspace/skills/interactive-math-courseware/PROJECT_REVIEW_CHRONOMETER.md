# chornmeter_block.html 项目复盘（机械秒表单文件实现）

## 项目定位
- 类型：高仿真机械秒表（单文件 HTML）
- 目标：纯 CSS 绘制秒表外观，JS 实现计时功能
- 技术栈：HTML5 + CSS3（Tailwind CDN）+ Vanilla JS
- 特点：零构建步骤，单文件即可运行

## 核心创新点

### 1) 纯 CSS 绘制机械秒表
- **金属质感**：conic-gradient 实现表盘金属光泽
- **玻璃反光**：linear-gradient 模拟玻璃表面反光
- **按钮按压效果**：:active + transform 模拟物理按键
- **指针细节**：伪元素 + border-radius 实现秒针尾端圆点

### 2) 动态刻度生成
- 大表盘：60 秒刻度，每 5 秒大刻度 + 数字标签
- 子表盘：30 分钟刻度，每 5 分钟标记
- 文字反向旋转：刻度数字随刻度旋转后，内部文字反向旋转保持正向

### 3) 计时精度
- 使用 `performance.now()` 获取高精度时间
- `requestAnimationFrame` 实现平滑动画
- 累计时间计算：elapsedTime + (now - startTime)

### 4) 指针运动学
- 秒针：6°/秒（360°/60秒）
- 分针：12°/分钟（360°/30分钟）+ 秒针进度补偿

## 关键代码模式

### CSS 金属表盘
```css
.watch-body {
  background: conic-gradient(from 0deg, #888, #eee, #888, #eee, #888);
  border-radius: 50%;
  box-shadow: 
    0 20px 50px rgba(0,0,0,0.5),
    inset 0 2px 5px rgba(255,255,255,0.8);
}
```

### 刻度生成（JS）
```js
for (let i = 0; i < 60; i++) {
  const marker = document.createElement('div');
  marker.style.transform = `rotate(${i * 6}deg)`;
  marker.style.transformOrigin = '50% 155px'; // 从中心偏移
  // 文字反向旋转保持正向
  textNode.style.transform = `rotate(-${i * 6}deg)`;
}
```

### 平滑指针动画
```js
function updateDisplay() {
  const secDegrees = seconds * 6; // 6度/秒
  const minDegrees = (minutes % 30) * 12 + (seconds / 60) * 12;
  secHand.style.transform = `rotate(${secDegrees}deg)`;
  minHand.style.transform = `rotate(${minDegrees}deg)`;
  timerId = requestAnimationFrame(updateDisplay);
}
```

## 与转盘锁、日晷项目的对比

| 维度 | 转盘锁 (rational-course_v4) | 日晷 (sundial_v3) | 秒表 (chornmeter) |
|------|---------------------------|-------------------|-------------------|
| 技术栈 | React + Next.js + Framer Motion | React + Three.js | 纯 HTML/CSS/JS |
| 构建步骤 | 需要 | 需要 | 零构建 |
| 渲染方式 | SVG + CSS | WebGL 3D | CSS + DOM |
| 动画机制 | Framer Motion spring | Three.js 渲染循环 | requestAnimationFrame |
| 适用场景 | 复杂交互课件 | 3D 科学模拟 | 快速原型/单文件交付 |

## 可复用模式

### 1) 纯 CSS 拟物化组件
- 金属质感：conic-gradient + box-shadow
- 玻璃反光：linear-gradient (135deg 透明渐变)
- 按压反馈：:active + transform translateY

### 2) 刻度盘生成器
```ts
function createDialMarkers(
  count: number,
  largeInterval: number,
  radius: number,
  labelFormatter: (i: number) => string
): HTMLElement[];
```

### 3) 高精度计时器
```ts
class Stopwatch {
  private startTime = 0;
  private elapsedTime = 0;
  private isRunning = false;
  
  start() { this.startTime = performance.now(); this.isRunning = true; }
  stop() { this.elapsedTime += performance.now() - this.startTime; this.isRunning = false; }
  reset() { this.elapsedTime = 0; this.isRunning = false; }
  getTime() { return this.isRunning ? performance.now() - this.startTime + this.elapsedTime : this.elapsedTime; }
}
```

### 4) 指针角度计算
```ts
function getHandAngles(totalSeconds: number): {
  secondHand: number;  // 0-360
  minuteHand: number; // 0-360 (30分钟一圈)
}
```

## 结论

chornmeter 展示了"单文件交付"的极致形态：
- 无需构建工具
- 纯浏览器原生技术
- 视觉效果不输框架方案

其核心资产是：**CSS 拟物化技巧 + 高精度计时逻辑 + 刻度盘生成模式**。

这种模式特别适合：快速原型、嵌入式课件、低环境依赖场景。
