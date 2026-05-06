'use client';

import { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import * as THREE from 'three';
import { getSunPosition } from '../scripts/astronomy';

interface Sundial3DProps {
  time: number;
  latitude: number;
  month: number;
  skyColors?: { top: string; bottom: string };
  isNight?: boolean;
  onSunPositionChange?: (pos: { altitude: number; azimuth: number }) => void;
}

// ─── 简易 OrbitControls 实现 ───
class SimpleOrbitControls {
  object: THREE.PerspectiveCamera;
  domElement: HTMLElement;
  target = new THREE.Vector3();

  private _phi = Math.PI / 2.5;
  private _theta = 0;
  private _radius = 22;
  private _isDragging = false;
  private _lastX = 0;
  private _lastY = 0;

  private _presetViews = {
    front: { phi: Math.PI / 2.2, theta: Math.PI / 2, radius: 22 },
    free: { phi: Math.PI / 3, theta: Math.PI / 4, radius: 25 }
  };
  private _currentView: 'free' | 'front' = 'front';

  constructor(camera: THREE.PerspectiveCamera, domElement: HTMLElement) {
    this.object = camera;
    this.domElement = domElement;
    this._updateCamera();

    domElement.addEventListener('mousedown', this._onMouseDown.bind(this));
    domElement.addEventListener('mousemove', this._onMouseMove.bind(this));
    domElement.addEventListener('mouseup', this._onMouseUp.bind(this));
    domElement.addEventListener('wheel', this._onWheel.bind(this), { passive: false });
    domElement.addEventListener('touchstart', this._onTouchStart.bind(this), { passive: false });
    domElement.addEventListener('touchmove', this._onTouchMove.bind(this), { passive: false });
    domElement.addEventListener('touchend', this._onTouchEnd.bind(this));
    domElement.style.cursor = 'grab';
  }

  setView(view: 'front' | 'free') {
    const preset = this._presetViews[view];
    this._phi = preset.phi;
    this._theta = preset.theta;
    this._radius = preset.radius;
    this._currentView = view;
    this._updateCamera();
  }

  private _updateCamera() {
    const x = this._radius * Math.sin(this._phi) * Math.cos(this._theta);
    const y = this._radius * Math.cos(this._phi);
    const z = this._radius * Math.sin(this._phi) * Math.sin(this._theta);
    this.object.position.set(
      this.target.x + x,
      this.target.y + y,
      this.target.z + z
    );
    this.object.lookAt(this.target);
  }

  update() { this._updateCamera(); }

  dispose() {
    const el = this.domElement;
    el.removeEventListener('mousedown', this._onMouseDown.bind(this));
    el.removeEventListener('mousemove', this._onMouseMove.bind(this));
    el.removeEventListener('mouseup', this._onMouseUp.bind(this));
    el.removeEventListener('wheel', this._onWheel.bind(this));
    el.removeEventListener('touchstart', this._onTouchStart.bind(this));
    el.removeEventListener('touchmove', this._onTouchMove.bind(this));
    el.removeEventListener('touchend', this._onTouchEnd.bind(this));
  }

  private _onMouseDown(e: MouseEvent) {
    if (this._currentView !== 'free') return;
    this._isDragging = true;
    this._lastX = e.clientX;
    this._lastY = e.clientY;
    this.domElement.style.cursor = 'grabbing';
  }

  private _onMouseMove(e: MouseEvent) {
    if (!this._isDragging) return;
    const dx = e.clientX - this._lastX;
    const dy = e.clientY - this._lastY;
    this._theta -= dx * 0.01;
    this._phi -= dy * 0.01;
    this._phi = Math.max(0.1, Math.min(Math.PI - 0.1, this._phi));
    this._lastX = e.clientX;
    this._lastY = e.clientY;
    this._updateCamera();
  }

  private _onMouseUp() {
    this._isDragging = false;
    this.domElement.style.cursor = 'grab';
  }

  private _onWheel(e: WheelEvent) {
    e.preventDefault();
    this._radius += e.deltaY * 0.02;
    this._radius = Math.max(8, Math.min(60, this._radius));
    this._updateCamera();
  }

  private _onTouchStart(e: TouchEvent) {
    if (e.touches.length === 1) {
      this._isDragging = true;
      this._lastX = e.touches[0].clientX;
      this._lastY = e.touches[0].clientY;
    }
  }

  private _onTouchMove(e: TouchEvent) {
    if (!this._isDragging || e.touches.length !== 1) return;
    const dx = e.touches[0].clientX - this._lastX;
    const dy = e.touches[0].clientY - this._lastY;
    this._theta -= dx * 0.01;
    this._phi -= dy * 0.01;
    this._phi = Math.max(0.1, Math.min(Math.PI - 0.1, this._phi));
    this._lastX = e.touches[0].clientX;
    this._lastY = e.touches[0].clientY;
    this._updateCamera();
  }

  private _onTouchEnd() { this._isDragging = false; }
}

// ─── 创建日晷盘面纹理 ───
function createDialTexture(): THREE.CanvasTexture {
  const size = 1024;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const cx = size / 2;
  const cy = size / 2;

  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, size, size);

  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 4;
  [485, 410, 200].forEach((r) => {
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  });

  const dZhi = ['午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳'];

  for (let i = 0; i < 96; i++) {
    const angle = (i / 96) * Math.PI * 2 + Math.PI / 2;
    let startR = 450, endR = 480, weight = 2, color = '#64748b';

    if (i % 4 === 0) { startR = 410; weight = 8; color = '#0f172a'; }
    else if (i % 2 === 0) { startR = 430; weight = 4; color = '#475569'; }

    ctx.lineWidth = weight;
    ctx.strokeStyle = color;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(angle) * startR, cy + Math.sin(angle) * startR);
    ctx.lineTo(cx + Math.cos(angle) * endR, cy + Math.sin(angle) * endR);
    ctx.stroke();

    if (i % 8 === 0) {
      const zhiIdx = i / 8;
      ctx.fillStyle = (zhiIdx === 0 || zhiIdx === 6) ? '#dc2626' : '#0f172a';
      ctx.font = 'bold 58px "STKaiti", "KaiTi", serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(dZhi[zhiIdx], cx + Math.cos(angle) * 340, cy + Math.sin(angle) * 340);

      const hourNum = (zhiIdx * 2 + 12) % 24;
      ctx.font = 'bold 28px "Courier New", monospace';
      ctx.fillStyle = '#1e293b';
      ctx.fillText(hourNum === 0 ? "24" : hourNum.toString(), cx + Math.cos(angle) * 260, cy + Math.sin(angle) * 260);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.anisotropy = 16;
  return texture;
}

export interface Sundial3DRef {
  setView: (view: 'front' | 'free') => void;
}

export default forwardRef<Sundial3DRef, Sundial3DProps>(function Sundial3D(
  { time, latitude, month, skyColors, isNight, onSunPositionChange },
  ref
) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bgOverlayRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const sunLightRef = useRef<THREE.DirectionalLight | null>(null);
  const ambientLightRef = useRef<THREE.AmbientLight | null>(null);
  const plateGroupRef = useRef<THREE.Group | null>(null);
  const animIdRef = useRef<number>(0);
  const controlsRef = useRef<SimpleOrbitControls | null>(null);

  useImperativeHandle(ref, () => ({
    setView: (view: 'front' | 'free') => controlsRef.current?.setView(view)
  }), []);

  // 初始化 Three.js
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(35, container.clientWidth / container.clientHeight, 0.1, 1000);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth || 600, container.clientHeight || 400);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const controls = new SimpleOrbitControls(camera, renderer.domElement);
    controls.setView('front');
    controlsRef.current = controls;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    ambientLightRef.current = ambientLight;

    const sunLight = new THREE.DirectionalLight(0xffffff, 0.8);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.left = -10;
    sunLight.shadow.camera.right = 10;
    sunLight.shadow.camera.top = 10;
    sunLight.shadow.camera.bottom = -10;
    scene.add(sunLight);
    sunLightRef.current = sunLight;

    const stoneMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.8 });

    const base = new THREE.Mesh(new THREE.BoxGeometry(8, 1.0, 8), stoneMat);
    base.position.y = -6.4;
    base.castShadow = true;
    base.receiveShadow = true;
    scene.add(base);

    const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.4, 6, 32), stoneMat);
    pillar.position.y = -3.4;
    pillar.castShadow = true;
    pillar.receiveShadow = true;
    scene.add(pillar);

    const plateGroup = new THREE.Group();
    scene.add(plateGroup);
    plateGroupRef.current = plateGroup;

    const dialTex = createDialTexture();
    const plateSideMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const plateTopMat = new THREE.MeshStandardMaterial({ map: dialTex, roughness: 0.4, metalness: 0.05 });

    const plateGeo = new THREE.CylinderGeometry(4.5, 4.5, 0.4, 128);
    const plate = new THREE.Mesh(plateGeo, [plateSideMat, plateTopMat, plateTopMat]);
    plate.rotation.y = Math.PI / 2;
    plate.receiveShadow = true;
    plate.castShadow = true;
    plateGroup.add(plate);

    const gnomonGeo = new THREE.CylinderGeometry(0.05, 0.05, 2.8, 32);
    const gnomonMat = new THREE.MeshStandardMaterial({
      color: 0x374151, metalness: 0.4, roughness: 0.3,
      emissive: 0x1e293b, emissiveIntensity: 0.1
    });
    const gnomon = new THREE.Mesh(gnomonGeo, gnomonMat);
    gnomon.position.y = 1.6;
    gnomon.castShadow = true;
    plateGroup.add(gnomon);

    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth || 600;
      const h = containerRef.current.clientHeight || 400;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    let animId = 0;
    function animate() {
      animId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();
    animIdRef.current = animId;

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
      controls.dispose();
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  // 更新太阳位置和光照
  useEffect(() => {
    const plateGroup = plateGroupRef.current;
    const sunLight = sunLightRef.current;
    const ambientLight = ambientLightRef.current;
    const bgOverlay = bgOverlayRef.current;
    if (!plateGroup || !sunLight || !ambientLight) return;

    const sunPos = getSunPosition(time, latitude, month);
    onSunPositionChange?.({ altitude: sunPos.altitude, azimuth: sunPos.azimuth });

    if (bgOverlay && skyColors) {
      bgOverlay.style.background = `linear-gradient(180deg, ${skyColors.top} 0%, ${skyColors.bottom} 100%)`;
    }

    sunLight.position.set(sunPos.x, sunPos.y, sunPos.z);

    if (isNight || sunPos.altitude <= 0) {
      sunLight.intensity = 0;
      ambientLight.intensity = 0.15;
    } else {
      const lightIntensity = Math.max(0.3, Math.min(1, (sunPos.y + 8) / 16));
      sunLight.intensity = 1.2 * lightIntensity;
      ambientLight.intensity = 0.5 + 0.3 * lightIntensity;
    }

    plateGroup.rotation.x = (Math.PI / 2) - (latitude * Math.PI / 180);
  }, [time, latitude, month, skyColors, isNight, onSunPositionChange]);

  return (
    <div className="relative w-full h-full">
      <div
        ref={bgOverlayRef}
        className="absolute inset-0 rounded-2xl transition-all duration-1000"
        style={{ background: 'linear-gradient(180deg, #bae6fd 0%, #ffffff 100%)', zIndex: 0 }}
      />
      <div ref={containerRef} className="absolute inset-0 rounded-2xl overflow-hidden" style={{ zIndex: 1 }} />
    </div>
  );
});
