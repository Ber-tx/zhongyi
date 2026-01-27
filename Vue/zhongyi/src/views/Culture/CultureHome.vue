<template>
  <div class="tcm-ai-hub" :class="{ 'is-focus': activeModule !== null, 'fade-out': isLeaving }">
    <div class="aura-bg">
      <div class="breath-sphere s-qi"></div>    <div class="breath-sphere s-blood"></div> <div class="paper-grain"></div>
    </div>

    <header class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">岐黄 · 智御</h1>
        <p class="hero-subtitle">万物波动，皆有定数。在这里，用算法触碰生命的律动。</p>
      </div>
    </header>

    <div class="bento-container">
      
      <div class="bento-item span-2-2 has-bg" :class="{ active: activeModule === 1 }" @click="handleModuleClick(1)" :style="{ backgroundImage: `url(${diag1})`, backgroundSize: 'cover', backgroundPosition: 'center' }">
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
              <circle class="node pulse-node" cx="30" cy="100" r="5" />
            </g>
          </svg>
        </div>
        <p class="desc">👉 提前发现身体的小问题，避免真正生病</p>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 2 }" @click="handleModuleClick(2)">
        <div class="label">MUSIC/音乐养生</div>
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
          <div class="gallery-mask small"><img class="soft-img" src="../../assets/images/mainShow/3.jpg" alt="儿童" /></div>
          <div class="neural-nodes">
            <span v-for="i in 3" :key="i" :style="{ animationDelay: i*0.2+'s' }"></span>
          </div>
        </div>
      </div>

      <div class="bento-item span-2" :class="{ active: activeModule === 4 }" @click="handleModuleClick(4)">
        <div class="label">妇婴保健</div>
        <div class="flex-row">
          <div class="gallery-mask"><img class="soft-img" src="../../assets/images/mainShow/4.jpg" alt="妇婴" /></div>
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

      <div class="bento-item span-2 theme-ink-jade" :class="{ active: activeModule === 6 }" @click="handleModuleClick(6)">
        <div class="label">情志调摄</div>
        <div class="inner-glow"></div> 
        <p class="advice-text">情绪内观 · 心神安位</p>
        <div class="advice-meta">
          <span class="status-dot"></span>
          👉 调节情绪压力，帮助内心恢复平衡
        </div>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 7 }" @click="handleModuleClick(7)">
        <div class="label">SLEEP/睡眠养生</div>
        <h3 class="section-title">昼夜归序 · 深度修复</h3>
        <div class="ripple-visual">
          <div class="r r1"></div><div class="r r2"></div>
        </div>
        <div class="gallery-mask small"><img class="soft-img" src="../../assets/images/mainShow/7.jpg" alt="睡眠" /></div>
      </div>

      <div class="bento-item" :class="{ active: activeModule === 8 }" @click="handleModuleClick(8)">
        <div class="label">休闲养生</div>
        <h3 class="section-title">松弛之域 · 日常回养</h3>
        <div class="growth-node"></div>
        <div class="gallery-mask small"><img class="soft-img" src="../../assets/images/mainShow/8.jpg" alt="休闲" /></div>
      </div>

      <div class="bento-item has-bg" :class="{ active: activeModule === 9 }" @click="handleModuleClick(9)" :style="{ backgroundImage: `url(${solar})`, backgroundSize: 'cover', backgroundPosition: 'center' }">
        <div class="label">节气养生</div>
        <h3 class="section-title">时令感知 · 天地同频</h3>
        <div class="follow-data-bar"></div>
        
      </div>

      <div class="bento-item has-bg" :class="{ active: activeModule === 10 }" @click="handleModuleClick(10)" :style="{ backgroundImage: `url(${seasons})`, backgroundSize: 'cover', backgroundPosition: 'center' }">
        <div class="label">四季养生</div>
        <h3 class="section-title">四时循环 · 生命长波</h3>
        <div class="zen-dot"></div>
        
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
import { useRouter } from 'vue-router' // 1. 引入路由
import solar from '/src/assets/images/mainShow/9.jpg'
import seasons from '/src/assets/images/mainShow/10.jpg'
import diag1 from '/src/assets/images/mainShow/1.jpg'
const isLeaving = ref(false)
const router = useRouter() // 2. 初始化
const activeModule = ref(null)

// 3. 统一跳转函数
const handleModuleClick = (id) => {
  activeModule.value = id
  // 延迟一小会儿跳转，让用户看到点击反馈动画（可选，比如 300ms）
  setTimeout(() => {
      // 2. 触发全屏淡出效果
      isLeaving.value = true 
      
      // 3. 在淡出动画进行到一半或结束时，再真正执行路由跳转
      setTimeout(() => {
        if (id === 1) {
          router.push('/culture/preventive')
        } else {
          // 路径会匹配你路由表中的 /culture/module/:id
          // 如果 id 是 4 或 8，路由表会自动分发到对应的 ModuleFour/Eight 组件
          router.push(`/culture/module/${id}`)
        }
      }, 800) // 延迟和 CSS 的 transition 时间匹配
    }, 400) 
  }
</script>

<style scoped>
/* 一、色彩与质感定义 */
:host, .tcm-ai-hub {
  --c-paper: #FBFBF9;
  --c-ink-jade: #1E2622;  /* 墨玉色：深绿入墨 */
  --c-qi: #4A907E;        /* 生机青 */
  --c-blood: #A64444;     /* 律动红 */
  --c-warm: #D9A05B;      /* 温阳金 */
  --ease-slow: cubic-bezier(0.34, 1.56, 0.64, 1);
}

.tcm-ai-hub {
  background-color: var(--c-paper);
  color: #1A1C1E;
  min-height: 100vh;
  font-family: "PingFang SC", "Noto Serif SC", serif;
}

/* 二、动态气场背景 */
.aura-bg { position: fixed; inset: 0; z-index: 0; overflow: hidden; }
.breath-sphere {
  position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.22;
  animation: float 12s infinite alternate ease-in-out;
}
.s-qi { width: 60vw; height: 60vw; background: var(--c-qi); top: -20%; left: -10%; }
.s-blood { width: 45vw; height: 45vw; background: var(--c-blood); bottom: -10%; right: -5%; animation-delay: -3s; }
.paper-grain {
  position: absolute; inset: 0; opacity: 0.04; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

@keyframes float { from { transform: translate(0,0); } to { transform: translate(40px, 60px); } }

/* 三、Hero 区域压缩 */
.hero-section { padding: 60px 4vw 30px; position: relative; z-index: 10; }
.hero-title { font-size: 3.2rem; font-family: "Noto Serif SC", serif; letter-spacing: 0.1em; }
.hero-subtitle { color: #888; font-weight: 300; margin-top: 8px; }

/* 四、Bento 容器交互 */
.bento-container {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px;
  padding: 0 4vw 60px; position: relative; z-index: 10;
}

.bento-item {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  padding: 26px; border-radius: 20px;
  transition: all 0.5s var(--ease-slow);
  cursor: pointer; display: flex; flex-direction: column;
}

.bento-item:hover {
  transform: translateY(-6px);
  background: #FFF;
  border-color: var(--c-qi);
  box-shadow: 0 20px 40px rgba(74, 144, 126, 0.1);
}

/* 背景图卡片遮罩，提升可读性 */
.bento-item.has-bg { position: relative; }
.bento-item.has-bg::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.25));
  border-radius: inherit;
  pointer-events: none;
  z-index: 0;
}
.bento-item.has-bg * { position: relative; z-index: 1; }

/* 尺寸与圆角节奏 */
.span-2-2 { grid-column: span 2; grid-row: span 2; border-radius: 60px 20px; }
.span-2 { grid-column: span 2; border-radius: 20px 40px; }

/* 01 四诊视觉 */
.fusion-visual { height: 160px; position: relative; display: flex; align-items: center; justify-content: center; }
.core-glow { position: absolute; width: 50px; height: 50px; background: var(--c-qi); filter: blur(30px); opacity: 0.2; }
.orbit-path { fill: none; stroke: var(--c-qi); stroke-opacity: 0.1; stroke-dasharray: 4; }
.pulse-node { fill: var(--c-qi); animation: nodePulse 2s infinite; }
@keyframes nodePulse { 50% { r: 7; opacity: 1; } }

/* 02 脉象视觉 */
.wave-path { fill: none; stroke: var(--c-blood); stroke-width: 2; stroke-dasharray: 200; animation: wave 4s infinite linear; }
@keyframes wave { to { stroke-dashoffset: -400; } }

/* 06 墨玉调理方案 (重点修改：不再突兀) */
.theme-ink-jade {
  background: linear-gradient(135deg, #242D28 0%, #1A1F1D 100%) !important;
  color: #E2E8E4 !important;
  border: 1px solid rgba(107, 143, 113, 0.2) !important;
  position: relative; overflow: hidden;
}
.inner-glow {
  position: absolute; inset: -50%;
  background: radial-gradient(circle at center, rgba(74, 144, 126, 0.08) 0%, transparent 50%);
  animation: rotate 15s infinite linear;
}
@keyframes rotate { from { transform: rotate(0); } to { transform: rotate(360deg); } }
.advice-text { font-family: "Noto Serif SC", serif; font-size: 1.25rem; line-height: 1.7; margin: 20px 0; position: relative; }
.advice-meta { font-size: 11px; opacity: 0.5; display: flex; align-items: center; gap: 8px; position: relative; }
.status-dot { width: 4px; height: 4px; background: var(--c-qi); border-radius: 50%; box-shadow: 0 0 8px var(--c-qi); }

/* 05 体质球视觉 */
.state-orb { 
  width: 70px; height: 70px; border-radius: 50%; margin: 20px auto;
  background: radial-gradient(circle at 30% 30%, var(--c-warm), var(--c-blood));
  filter: blur(8px); animation: breath 4s infinite alternate;
}
@keyframes breath { from { transform: scale(0.9); opacity: 0.7; } to { transform: scale(1.15); opacity: 1; } }

/* 聚焦态控制 */
.is-focus .bento-item:not(.active) { opacity: 0.2; filter: grayscale(1) blur(4px); transform: scale(0.96); }
.bento-item.active { transform: scale(1.04); z-index: 50; border-color: var(--c-qi); box-shadow: 0 30px 60px rgba(0,0,0,0.1); }

/* 基础通用 */
.label { font-size: 10px; font-weight: 800; color: #AAA; letter-spacing: 2px; }
.section-title { font-family: "Noto Serif SC", serif; font-size: 1.3rem; margin: 10px 0; }
.desc { font-size: 12px; color: #999; line-height: 1.5; }
.flex-row { display: flex; align-items: center; gap: 20px; }
.gallery-mask {
  width: clamp(100px, 18vw, 220px);
  height: clamp(100px, 18vw, 220px);
  border-radius: 50%;
  border: 1px solid var(--c-qi);
  overflow: hidden;
}
.soft-img { width: 100%; height: 100%; display: block; object-fit: cover; }
.gallery-mask.small {
  width: clamp(70px, 12vw, 140px);
  height: clamp(70px, 12vw, 140px);
  border-radius: 50%;
}

.philosophy-footer { padding: 40px 4vw; border-top: 1px solid rgba(0,0,0,0.05); }
.copyright { font-size: 10px; color: #BBB; letter-spacing: 2px; }

/* 定义一个离开动画 */
.fade-out {
  opacity: 0;
  filter: blur(10px);
  transform: scale(1.1); /* 稍微放大一点点，更有穿透感 */
  transition: all 0.6s ease-out;
}

/* 确保容器有 transition 属性 */
.tcm-ai-hub {
  transition: opacity 0.8s ease;
}
</style>

