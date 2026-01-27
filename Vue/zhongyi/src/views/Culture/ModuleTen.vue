<template>
  <div class="module-container">
    <div class="paper-texture"></div>
    
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <span>❮</span> 返回
      </button>
      <div class="titles">
        <h1 class="main-title">四季养生</h1>
        <p class="sub-title">春生夏长 · 秋收冬藏 · 顺时而养</p>
      </div>
    </header>

    <div class="grid-layout seasons-grid">
      <div class="card theme-spring" @click="goToReader('10-1')">
        <div class="card-bg" :style="{ backgroundImage: `url(${imgSpring})` }"></div>
        <div class="card-content">
          <div class="season-char">春</div>
          <h2>春生 · 疏肝</h2>
          <p>夜卧早起，广步于庭，被发缓形，以使志生。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>

      <div class="card theme-summer" @click="goToReader('10-2')">
        <div class="card-bg" :style="{ backgroundImage: `url(${imgSummer})` }"></div>
        <div class="card-content">
          <div class="season-char">夏</div>
          <h2>夏长 · 养心</h2>
          <p>夜卧早起，无厌于日，使志无怒，使华英成秀。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>

      <div class="card theme-autumn" @click="goToReader('10-3')">
        <div class="card-bg" :style="{ backgroundImage: `url(${imgAutumn})` }"></div>
        <div class="card-content">
          <div class="season-char">秋</div>
          <h2>秋收 · 润肺</h2>
          <p>早卧早起，与鸡俱兴，使志安宁，以缓秋刑。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>

      <div class="card theme-winter" @click="goToReader('10-4')">
        <div class="card-bg" :style="{ backgroundImage: `url(${imgWinter})` }"></div>
        <div class="card-content">
          <div class="season-char">冬</div>
          <h2>冬藏 · 补肾</h2>
          <p>早卧晚起，必待日光，使志若伏若匿，去寒就温。</p>
          <span class="arrow">进入阅览 ➔</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
// 请替换为你实际的四季封面图
import imgSpring from '@/assets/images/mainShow/imageReader/button_10/spring.jpg'
import imgSummer from '@/assets/images/mainShow/imageReader/button_10/summer.jpg'
import imgAutumn from '@/assets/images/mainShow/imageReader/button_10/autumn.jpg'
import imgWinter from '@/assets/images/mainShow/imageReader/button_10/winter.jpg'

const router = useRouter()

const goToReader = (subId) => {
  // 跳转 ID 为 '10-1', '10-2' 等
  router.push(`/culture/module/${subId}`)
}
</script>

<style scoped>
/* 复用上面的基础样式，这里只写差异部分 */
.module-container { 
  position: fixed; 
  inset: 0; 
  background: #F7F5F0; /* 这里的颜色已同步 */
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
}
.paper-texture { position: absolute; inset: 0; opacity: 0.06; pointer-events: none; background-image: url('https://www.transparenttextures.com/patterns/natural-paper.png'); }

.page-header { position: absolute; top: 40px; width: 100%; text-align: center; z-index: 10; }
.back-btn { position: absolute; left: 40px; top: 0; cursor: pointer; background: none; border: 1px solid #999; padding: 6px 16px; border-radius: 20px; transition: 0.3s; }
.back-btn:hover { background: #333; color: white; border-color: #333; }
.main-title { font-family: "Noto Serif SC", serif; font-size: 2rem; color: #1A1A1A; }
.sub-title { font-size: 0.9rem; color: #666; letter-spacing: 3px; }

.grid-layout { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; width: 85vw; height: 65vh; gap: 15px; margin-top: 60px; z-index: 5; }

.card { position: relative; border-radius: 8px; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: 0.4s; background: #000; }
.card:hover { transform: scale(1.01); box-shadow: 0 20px 40px rgba(0,0,0,0.2); z-index: 10; }

.card-bg { position: absolute; inset: 0; background-size: cover; background-position: center; transition: 0.7s ease; opacity: 0.8; }
.card:hover .card-bg { transform: scale(1.1); opacity: 0.4; }

.card-content { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; color: white; padding: 20px; }

.season-char { 
  font-family: "KaiTi", serif; font-size: 3rem; opacity: 0.2; position: absolute; top: 20px; right: 30px; 
  transition: 0.5s; font-weight: bold;
}
.card:hover .season-char { opacity: 0.8; transform: scale(1.2); color: white; }

h2 { font-family: "Noto Serif SC"; font-size: 2rem; margin-bottom: 10px; position: relative; }
h2::after { content: ''; display: block; width: 0; height: 2px; background: white; margin: 10px auto 0; transition: 0.3s; }
.card:hover h2::after { width: 40px; }

p { font-size: 0.9rem; max-width: 80%; opacity: 0; transform: translateY(20px); transition: 0.4s; }
.arrow { margin-top: 25px; border: 1px solid rgba(255,255,255,0.5); padding: 5px 15px; border-radius: 20px; font-size: 12px; opacity: 0; transform: translateY(20px); transition: 0.4s 0.1s; }

.card:hover p, .card:hover .arrow { opacity: 1; transform: translateY(0); }
.card:hover .arrow:hover { background: white; color: black; }

/* 四季主题色微调（可选） */
.theme-spring:hover { background: #2E5C46; } /* 春绿背景底色 */
.theme-summer:hover { background: #8E3535; } /* 夏红 */
.theme-autumn:hover { background: #B8860B; } /* 秋金 */
.theme-winter:hover { background: #2F3E4E; } /* 冬蓝 */
</style>