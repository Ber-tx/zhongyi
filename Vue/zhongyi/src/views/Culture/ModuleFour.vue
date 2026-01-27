<template>
  <div class="module-container">
    <div class="paper-texture"></div>
    
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <span>❮</span> 返回
      </button>
      <div class="titles">
        <h1 class="main-title">妇婴保健</h1>
        <p class="sub-title">阴阳承续 · 生命之源的温养之道</p>
      </div>
    </header>

    <div class="grid-layout">
      <div class="card" @click="goToReader('4-1')">
        <div class="card-bg" :style="{ backgroundImage: `url(${img1})` }"></div>
        <div class="card-content">
          <div class="card-tag">阶段一</div>
          <h2>妇婴保健—产妇</h2>
          <p>胎养为本，安胎养气，为新生命筑基。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>

      <div class="card" @click="goToReader('4-2')">
        <div class="card-bg" :style="{ backgroundImage: `url(${img2})` }"></div>
        <div class="card-content">
          <div class="card-tag">阶段二</div>
          <h2>妇婴中医保健 </h2>
          <p>去瘀生新，气血重塑，恢复女性本源。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>

      <div class="card" @click="goToReader('4-3')">
        <div class="card-bg" :style="{ backgroundImage: `url(${img3})` }"></div>
        <div class="card-content">
          <div class="card-tag">日常</div>
          <h2>妇婴保健—孕妇</h2>
          <p>经带胎产，调理冲任，守护女性全周期。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>

      <div class="card" @click="goToReader('4-4')">
        <div class="card-bg" :style="{ backgroundImage: `url(${img4})` }"></div>
        <div class="card-content">
          <div class="card-tag">抚育</div>
          <h2>妇婴保健—婴幼儿</h2>
          <p>稚阴稚阳，扶正固本，呵护娇嫩萌芽。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

import img1 from '@/assets/images/mainShow/imageReader/button_4/4.jpg' 
import img2 from '@/assets/images/mainShow/imageReader/button_4/1.jpg'
import img3 from '@/assets/images/mainShow/imageReader/button_4/2.jpg'
import img4 from '@/assets/images/mainShow/imageReader/button_4/3.jpg'

const router = useRouter()

const goToReader = (subId) => {
  // 跳转到通用阅读器，并传入子板块 ID (例如 '4-1')
  // 注意：你需要确保 router/index.js 里有 path: '/culture/module/:id'
  router.push(`/culture/module/${subId}`)
}
</script>

<style scoped>
/* 容器与背景 */
.module-container {
  position: fixed; inset: 0; background: #F7F5F0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.paper-texture {
  position: absolute; inset: 0; opacity: 0.06; pointer-events: none;
  background-image: url('https://www.transparenttextures.com/patterns/natural-paper.png');
}

/* 头部 */
.page-header {
  position: absolute; top: 40px; width: 100%; text-align: center; z-index: 10;
}
.back-btn {
  position: absolute; left: 40px; top: 0; cursor: pointer;
  background: none; border: 1px solid #CCC; padding: 6px 16px; border-radius: 20px;
  font-size: 14px; transition: 0.3s;
}
.back-btn:hover { background: #333; color: white; border-color: #333; }
.main-title { font-family: "Noto Serif SC", serif; font-size: 2rem; color: #2C3E50; margin-bottom: 5px; }
.sub-title { font-size: 0.9rem; color: #888; letter-spacing: 2px; }

/* 核心网格 */
.grid-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  width: 85vw; height: 65vh;
  gap: 20px; margin-top: 60px; z-index: 5;
}

/* 卡片样式 */
.card {
  position: relative; border-radius: 12px; overflow: hidden; cursor: pointer;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05); transition: all 0.4s ease;
  background: white;
}
.card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }

/* 图片层 */
.card-bg {
  position: absolute; inset: 0; background-size: cover; background-position: center;
  transition: transform 0.6s ease; filter: brightness(0.9);
}
.card:hover .card-bg { transform: scale(1.08); filter: brightness(0.7); }

/* 内容层 */
.card-content {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  justify-content: center; align-items: center; text-align: center;
  color: white; opacity: 0; transition: 0.4s ease;
  background: rgba(0,0,0,0.2); backdrop-filter: blur(2px);
  padding: 20px;
}
/* 默认显示标题，悬停显示全部 */
.card-content h2 { 
  font-family: "Noto Serif SC"; font-size: 1.8rem; text-shadow: 0 2px 10px rgba(0,0,0,0.3);
  transform: translateY(20px); transition: 0.4s;
}
.card:hover .card-content { opacity: 1; }
.card:hover h2 { transform: translateY(0); }

.card-tag { 
  background: #D9A05B; padding: 2px 8px; font-size: 10px; border-radius: 4px; 
  margin-bottom: 10px; transform: translateY(-10px); opacity: 0; transition: 0.4s 0.1s;
}
.card p { 
  font-size: 0.9rem; max-width: 80%; line-height: 1.6; margin-top: 10px;
  transform: translateY(10px); opacity: 0; transition: 0.4s 0.2s;
}
.arrow {
  margin-top: 20px; font-size: 0.8rem; border-bottom: 1px solid white; padding-bottom: 2px;
  transform: translateY(10px); opacity: 0; transition: 0.4s 0.3s;
}

.card:hover .card-tag, 
.card:hover p, 
.card:hover .arrow { opacity: 1; transform: translateY(0); }
</style>