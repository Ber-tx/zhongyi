<template>
  <div class="tcm-ai-hub" :class="{ 'is-focus': activeModule !== null, 'fade-out': isLeaving }">

    <!-- 背景：宣纸暖黄 -->
    <div class="aura-bg">
      <div class="breath-sphere s-qi"></div>
      <div class="breath-sphere s-blood"></div>
      <div class="paper-grain"></div>
    </div>

    <!-- 页眉 -->
    <header class="hero-section">
      <el-button class="back-btn" @click="router.push('/')">← 返回主页</el-button>
      <div class="hero-content">
        <h1 class="hero-title">岐黄 · 智御</h1>
        <p class="hero-subtitle">万物波动，皆有定数。在这里，用算法触碰生命的律动。</p>
        <p class="loading-tip">提示：首次进入模块时，首张内容加载可能较慢，后续会更快。</p>
      </div>
    </header>

    <!-- Bento 卡片网格 -->
    <div class="bento-container">

      <div class="bento-item span-2-2 has-bg"
        :class="{ active: activeModule === 1 }"
        @click="handleModuleClick(1)"
        :style="{ backgroundImage: `url(${diag1})` }">
        <div class="label">MODULE 01 / 中医治未病</div>
        <h3 class="section-title">未病之域 · 生命预演</h3>
        <div class="visual-box fusion-visual">
          <div class="core-glow"></div>
          <svg class="connecting-lines" viewBox="0 0 200 200">
            <circle class="orbit-path" cx="100" cy="100" r="70" />
            <g class="nodes">
              <circle class="node pulse-node" cx="100" cy="30" r="5" />
              <circle class="node pulse-node" cx="170" cy="100" r="5" />
              <circle class="node pulse-node" cx="100" cy="170" r="5" />
              <circle class="node pulse-node" cx="30"  cy="100" r="5" />
            </g>
          </svg>
        </div>
        <p class="desc">👉 提前发现身体的小问题，避免真正生病</p>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 2 }" @click="handleModuleClick(2)">
        <div class="label">MUSIC / 音乐养生</div>
        <h3 class="section-title">声律共振 · 气机调和</h3>
        <div class="visual-box pulse-visual">
          <svg class="pulse-svg" viewBox="0 0 200 60">
            <path class="wave-path" d="M0,30 Q25,5 50,30 T100,30 T150,30 T200,30" />
          </svg>
        </div>
        <p class="desc">👉 通过音乐节奏，放松情绪、调节身体状态</p>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 3 }" @click="handleModuleClick(3)">
        <div class="label">儿童调养</div>
        <h3 class="section-title">稚阳初生 · 生长守护</h3>
        <div class="visual-box logic-visual">
          <div class="gallery-mask small">
            <img class="soft-img" src="../../assets/images/mainShow/3.jpg" alt="儿童" />
          </div>
          <div class="neural-nodes">
            <span v-for="i in 3" :key="i" :style="{ animationDelay: i * 0.2 + 's' }"></span>
          </div>
        </div>
      </div>

      <div class="bento-item span-2" :class="{ active: activeModule === 4 }" @click="handleModuleClick(4)">
        <div class="label">妇婴保健</div>
        <div class="flex-row">
          <div class="gallery-mask">
            <img class="soft-img" src="../../assets/images/mainShow/4.jpg" alt="妇婴" />
          </div>
          <div>
            <h3 class="section-title">阴阳承续 · 温养之源</h3>
            <p class="desc">👉 呵护孕期与产后，支持生命延续</p>
          </div>
        </div>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 5 }" @click="handleModuleClick(5)">
        <div class="label">中老年保健</div>
        <h3 class="section-title">固本缓行 · 长养之道</h3>
        <div class="state-orb-wrap">
          <div class="state-orb"></div>
        </div>
      </div>

      <div class="bento-item span-2 theme-ink" :class="{ active: activeModule === 6 }" @click="handleModuleClick(6)">
        <div class="label">情志调摄</div>
        <div class="inner-glow"></div>
        <p class="advice-text">情绪内观 · 心神安位</p>
        <div class="advice-meta">
          <span class="status-dot"></span>
          👉 调节情绪压力，帮助内心恢复平衡
        </div>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 7 }" @click="handleModuleClick(7)">
        <div class="label">SLEEP / 睡眠养生</div>
        <h3 class="section-title">昼夜归序 · 深度修复</h3>
        <div class="ripple-visual">
          <div class="r r1"></div><div class="r r2"></div>
        </div>
        <div class="gallery-mask small">
          <img class="soft-img" src="../../assets/images/mainShow/7.jpg" alt="睡眠" />
        </div>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 8 }" @click="handleModuleClick(8)">
        <div class="label">休闲养生</div>
        <h3 class="section-title">松弛之域 · 日常回养</h3>
        <div class="growth-node"></div>
        <div class="gallery-mask small">
          <img class="soft-img" src="../../assets/images/mainShow/8.jpg" alt="休闲" />
        </div>
      </div>

      <div class="bento-item has-bg" :class="{ active: activeModule === 9 }" @click="handleModuleClick(9)"
        :style="{ backgroundImage: `url(${solar})` }">
        <div class="label">节气养生</div>
        <h3 class="section-title">时令感知 · 天地同频</h3>
      </div>

      <div class="bento-item has-bg" :class="{ active: activeModule === 10 }" @click="handleModuleClick(10)"
        :style="{ backgroundImage: `url(${seasons})` }">
        <div class="label">四季养生</div>
        <h3 class="section-title">四时循环 · 生命长波</h3>
      </div>

    </div>

    <footer class="philosophy-footer">
      <div class="footer-divider"></div>
      <p class="copyright">EST. 2025 · 岐黄 AI · 传承重构</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import solar  from '/src/assets/images/mainShow/9.jpg'
import seasons from '/src/assets/images/mainShow/10.jpg'
import diag1  from '/src/assets/images/mainShow/1.jpg'

const isLeaving    = ref(false)
const router       = useRouter()
const activeModule = ref(null)
const TRANSITION_PREPARE_MS = 60
const TRANSITION_ROUTE_MS = 180
const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']
const _firstPageGlob = import.meta.glob(
  [
    '../../assets/images/mainShow/imageReader/button_*/1.jpg',
    '../../assets/images/mainShow/imageReader/button_*/1.jpeg',
    '../../assets/images/mainShow/imageReader/button_*/1.png',
    '../../assets/images/mainShow/imageReader/button_*/1.JPG',
    '../../assets/images/mainShow/imageReader/button_*/1.JPEG',
    '../../assets/images/mainShow/imageReader/button_*/1.PNG'
  ],
  { query: '?url', import: 'default', eager: false }
)
const _firstPageWarmSet = new Set()

const resolveFirstPageKey = (moduleId) => {
  const base = `../../assets/images/mainShow/imageReader/button_${moduleId}/1`
  for (const ext of IMAGE_EXTS) {
    const key = `${base}.${ext}`
    if (_firstPageGlob[key]) return key
  }
  return ''
}

const prewarmReaderFirstPage = (id) => {
  if (id === 4 || id === 10) return
  const moduleId = String(id)
  const key = resolveFirstPageKey(moduleId)
  if (!key || _firstPageWarmSet.has(key)) return
  _firstPageWarmSet.add(key)

  const loader = _firstPageGlob[key]
  if (!loader) return
  loader().then((url) => {
    if (!url) return
    const img = new Image()
    img.decoding = 'async'
    img.loading = 'eager'
    img.fetchPriority = 'high'
    img.src = url
  }).catch(() => {})
}

const handleModuleClick = (id) => {
  activeModule.value = id
  prewarmReaderFirstPage(id)
  if (id !== 4 && id !== 10) import('./ImageReader.vue')
  setTimeout(() => {
    isLeaving.value = true
    setTimeout(() => {
      if (id === 1) router.push('/culture/preventive')
      else          router.push(`/culture/module/${id}`)
    }, TRANSITION_ROUTE_MS)
  }, TRANSITION_PREPARE_MS)
}
</script>

<style scoped>
/* ── 色彩变量（与 Home.vue 保持一致）── */
.tcm-ai-hub {
  --c-paper:   #fdf8ef;
  --c-border:  #c8a96e;
  --c-gold:    #c8a020;
  --c-ink:     #3d2b10;
  --c-ink-lt:  #6b4c24;
  --c-brown:   #8b3d1a;
  --c-qi:      #4a7060;   /* 比原来更暗、更沉稳的青绿 */
  --c-blood:   #8b3020;   /* 比原来更暗的砖红 */
  --c-warm:    #c8a020;   /* 金色 */
  --ease-slow: cubic-bezier(0.34, 1.56, 0.64, 1);

  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  color: var(--c-ink);
  min-height: 100vh;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

/* ── 背景气场 ── */
.aura-bg { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; }

.breath-sphere {
  position: absolute; border-radius: 50%;
  filter: blur(120px); opacity: 0.12;   /* 比原来更透，不抢主体 */
  animation: float 12s infinite alternate ease-in-out;
}
.s-qi    { width: 60vw; height: 60vw; background: #4a7060; top: -20%;  left: -10%; }
.s-blood { width: 45vw; height: 45vw; background: #8b3020; bottom: -10%; right: -5%; animation-delay: -3s; }

.paper-grain {
  position: absolute; inset: 0; opacity: 0.04; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
}
@keyframes float { from { transform: translate(0,0); } to { transform: translate(40px, 60px); } }

/* ── 页眉 ── */
.hero-section {
  padding: 36px 4vw 24px;
  position: relative; z-index: 10;
  border-bottom: 1px solid #e8d5a0;
  margin-bottom: 4px;
}

.back-btn {
  background: rgba(139,61,26,.08) !important;
  color: #6b4c24 !important;
  border: 1px solid #c8a96e !important;
  border-radius: 4px !important;
  font-family: inherit !important;
  font-size: 13px !important;
  margin-bottom: 16px;
}
.back-btn:hover { background: rgba(139,61,26,.16) !important; }

.hero-content { text-align: center; }
.hero-title {
  font-size: 2.8rem;
  font-family: "Noto Serif SC", serif;
  letter-spacing: 0.12em;
  color: var(--c-ink);
  margin: 0 0 8px;
  text-shadow: 0 1px 3px rgba(100,50,0,.1);
}
.hero-subtitle { color: var(--c-ink-lt); font-weight: 300; margin: 0; font-size: 14px; }
.loading-tip {
  margin-top: 10px;
  color: #8a6a3f;
  font-size: 12px;
}

/* ── Bento 容器 ── */
.bento-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 20px 4vw 60px;
  position: relative; z-index: 10;
}

/* ── 卡片基础 ── */
.bento-item {
  background: rgba(255, 252, 242, 0.88);
  border: 1px solid #d4b483;
  border-radius: 16px;
  padding: 22px;
  cursor: pointer;
  display: flex; flex-direction: column;
  box-shadow: 0 3px 12px rgba(100,60,10,.07),
              inset 0 1px 0 rgba(255,248,220,.7);
  transition: all 0.4s var(--ease-slow);
  position: relative;
}

/* 顶部金线 */
.bento-item::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, #c8a020 50%, transparent);
  border-radius: 16px 16px 0 0; opacity: .4;
}

.bento-item:hover {
  transform: translateY(-6px);
  background: #fffdf5;
  border-color: var(--c-gold);
  box-shadow: 0 16px 36px rgba(100,60,10,.14);
}

/* 背景图卡片 */
.bento-item.has-bg { background-size: cover; background-position: center; }
.bento-item.has-bg::after {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(rgba(30,15,5,.55), rgba(30,15,5,.3));
  border-radius: inherit;
  pointer-events: none; z-index: 0;
}
.bento-item.has-bg > * { position: relative; z-index: 1; }
/* 覆盖顶部金线，防止两个 pseudo 冲突 */
.bento-item.has-bg::before { opacity: 0; }

/* 尺寸变体 */
.span-2-2 { grid-column: span 2; grid-row: span 2; border-radius: 24px 12px; }
.span-2   { grid-column: span 2; border-radius: 12px 24px; }

/* ── 聚焦态 ── */
.is-focus .bento-item:not(.active) {
  opacity: 0.25; filter: grayscale(1) blur(3px); transform: scale(0.97);
}
.bento-item.active {
  transform: scale(1.04); z-index: 50;
  border-color: var(--c-gold);
  box-shadow: 0 24px 50px rgba(100,60,10,.18);
}

/* ── 通用文字 ── */
.label {
  font-size: 10px; font-weight: 800; color: var(--c-ink-lt);
  letter-spacing: 2px; margin-bottom: 6px;
}
.bento-item.has-bg .label { color: rgba(255,240,200,.7); }

.section-title {
  font-family: "Noto Serif SC", serif;
  font-size: 1.2rem; margin: 8px 0;
  color: var(--c-ink);
}
.bento-item.has-bg .section-title { color: #fdeabb; text-shadow: 0 1px 4px rgba(0,0,0,.4); }

.desc { font-size: 12px; color: var(--c-ink-lt); line-height: 1.6; margin: 0; }
.bento-item.has-bg .desc { color: rgba(255,240,200,.8); }

/* ── 视觉元素 ── */
.fusion-visual {
  height: 150px; position: relative;
  display: flex; align-items: center; justify-content: center;
}
.core-glow {
  position: absolute; width: 50px; height: 50px;
  background: var(--c-gold); filter: blur(28px); opacity: .25;
}
.orbit-path { fill: none; stroke: var(--c-gold); stroke-opacity: .2; stroke-dasharray: 4; }
.pulse-node { fill: var(--c-gold); animation: nodePulse 2s infinite; }
@keyframes nodePulse { 50% { r: 7; opacity: 1; } }

.wave-path {
  fill: none; stroke: var(--c-blood); stroke-width: 2;
  stroke-dasharray: 200; animation: wave 4s infinite linear;
}
@keyframes wave { to { stroke-dashoffset: -400; } }

/* 情志卡片（深色主题） */
.theme-ink {
  background: linear-gradient(135deg, #2e1e0e 0%, #1e150a 100%) !important;
  border-color: rgba(200,160,32,.25) !important;
  color: #f0e0c0 !important;
  overflow: hidden;
}
.theme-ink .label { color: rgba(200,160,32,.6); }
.theme-ink .section-title { color: #fdeabb; }
.inner-glow {
  position: absolute; inset: -50%;
  background: radial-gradient(circle at center, rgba(200,160,32,.08) 0%, transparent 50%);
  animation: rotate 15s infinite linear;
}
@keyframes rotate { from { transform: rotate(0); } to { transform: rotate(360deg); } }
.advice-text {
  font-family: "Noto Serif SC", serif; font-size: 1.2rem;
  line-height: 1.7; margin: 16px 0; position: relative;
  color: #fdeabb;
}
.advice-meta {
  font-size: 11px; opacity: .6;
  display: flex; align-items: center; gap: 8px; position: relative;
}
.status-dot {
  width: 4px; height: 4px; background: var(--c-gold);
  border-radius: 50%; box-shadow: 0 0 6px var(--c-gold);
}

/* 体质球 */
.state-orb {
  width: 64px; height: 64px; border-radius: 50%; margin: 16px auto;
  background: radial-gradient(circle at 30% 30%, #c8a020, #8b3020);
  filter: blur(8px); animation: breath 4s infinite alternate;
}
@keyframes breath { from { transform: scale(.9); opacity: .7; } to { transform: scale(1.15); opacity: 1; } }

/* 涟漪 */
.ripple-visual { position: relative; height: 40px; margin: 8px 0; }
.r {
  position: absolute; border-radius: 50%;
  border: 1px solid var(--c-gold); opacity: 0;
  animation: ripple 3s infinite ease-out;
  top: 50%; left: 50%; transform: translate(-50%, -50%);
}
.r1 { width: 30px; height: 30px; }
.r2 { width: 30px; height: 30px; animation-delay: 1.5s; }
@keyframes ripple {
  0%   { width: 20px; height: 20px; opacity: .6; }
  100% { width: 70px; height: 70px; opacity: 0; }
}

/* 生长节点 */
.growth-node {
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--c-gold);
  margin: 12px 0;
  box-shadow: 0 0 12px rgba(200,160,32,.5);
  animation: breath 2s infinite alternate;
}

/* 图片遮罩 */
.flex-row { display: flex; align-items: center; gap: 18px; }
.gallery-mask {
  width: clamp(80px, 16vw, 200px);
  height: clamp(80px, 16vw, 200px);
  border-radius: 50%;
  border: 2px solid var(--c-gold);
  overflow: hidden; flex-shrink: 0;
}
.gallery-mask.small {
  width: clamp(60px, 10vw, 120px);
  height: clamp(60px, 10vw, 120px);
}
.soft-img { width: 100%; height: 100%; display: block; object-fit: cover; }

/* ── 页脚 ── */
.philosophy-footer {
  padding: 30px 4vw;
  border-top: 1px solid #e8d5a0;
  position: relative; z-index: 10;
}
.copyright { font-size: 11px; color: var(--c-ink-lt); letter-spacing: 3px; }

/* ── 离开动画 ── */
.fade-out {
  opacity: 0; filter: blur(10px); transform: scale(1.06);
  transition: all 0.6s ease-out;
}
.tcm-ai-hub { transition: opacity 0.8s ease; }
</style>