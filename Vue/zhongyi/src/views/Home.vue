<template>
  <div class="tcm-system">
    <audio ref="audioRef" loop>
      <source src="../assets/audio/bgm/梁祝.wav" type="audio/mpeg" />
    </audio>

    <!-- ===== 页眉 ===== -->
    <header class="sys-header">
      <div class="header-deco"></div>
      <h1 class="sys-title">中医体质辨识系统</h1>
      <div class="header-deco right"></div>
      <div class="header-right-btns">
        <div class="music-btn" @click="toggleMusic">
          <span class="music-waves" :class="{ active: isPlaying }">
            <i></i><i></i><i></i>
          </span>
          {{ isPlaying ? '♫' : '♪' }}
        </div>
        <div class="more-btn" @click="showMore = !showMore">
          更多功能 ▾
          <transition name="dropdown">
            <div v-if="showMore" class="more-dropdown" @click.stop>
              <div class="dropdown-item" @click="goTo('/intro')">📖 系统介绍</div>
              <div class="dropdown-item" @click="goTo('/hardware')">🔧 硬件指引</div>
              <div class="dropdown-item" @click="goTo('/culture')">🏮 中医文化</div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item" @click="goTo('/admin/login')">⚙️ 管理后台</div>
            </div>
          </transition>
        </div>
      </div>
    </header>

    <!-- ===== 顶部导航 ===== -->
    <nav class="sys-nav">
      <div
        v-for="item in navItems"
        :key="item.key"
        class="nav-item"
        :class="{ active: activeTab === item.key }"
        @click="handleNav(item.key)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        {{ item.label }}
      </div>
    </nav>

    <!-- ===== 主内容区（动态组件切换）===== -->
    <main class="sys-main" @click="showMore = false">
      <keep-alive>
        <component :is="currentComponent" :key="activeTab" />
      </keep-alive>
    </main>

    <!-- ===== 页脚 ===== -->
    <footer class="sys-footer">
      Copyright © 2025 · 中医体质辨识系统 · All Rights Reserved.
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
// 异步加载各面板组件（按需加载，提升首屏速度）
const PatientRegister   = defineAsyncComponent(() => import('./TCM/PatientRegister.vue'))
const DiagnosisArchive  = defineAsyncComponent(() => import('./TCM/DiagnosisArchive.vue'))
const HealthExam        = defineAsyncComponent(() => import('./TCM/HealthExam.vue'))
const ConstitutionStats = defineAsyncComponent(() => import('./TCM/ConstitutionStats.vue'))

const router = useRouter()

// ===== 导航配置 =====
const activeTab = ref('register')
const navItems = [
  { key: 'register', label: '开始测试',    icon: '⚕' },
  { key: 'archive',  label: '辨识档案管理', icon: '📋' },
  { key: 'health',   label: '居民体检管理', icon: '🏥' },
  { key: 'stats',    label: '体质统计分析', icon: '📊' },
]

const currentComponent = computed(() => {
  const map = {
    register: PatientRegister,
    archive:  DiagnosisArchive,
    health:   HealthExam,
    stats:    ConstitutionStats,
  }
  return map[activeTab.value] || PatientRegister
})

const handleNav = (key) => { activeTab.value = key }

// ===== 更多功能下拉 =====
const showMore = ref(false)
const goTo = (path) => { showMore.value = false; router.push(path) }

// ===== 音乐 =====
const audioRef = ref(null)
const isPlaying = ref(false)
const toggleMusic = () => {
  if (isPlaying.value) { audioRef.value?.pause() }
  else { audioRef.value?.play().catch(() => {}) }
  isPlaying.value = !isPlaying.value
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap');

.tcm-system {
  --c-border: #c8a96e;
  --c-gold:   #c8a020;
  --c-accent: #8b1a1a;

  min-height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
  color: #3d2b10;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 宣纸纹理 */
.tcm-system::before {
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
  pointer-events: none; z-index: 0;
}

/* 页眉 */
.sys-header {
  position: relative; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(180deg, #6b2d12 0%, #8b3d1a 60%, #a04820 100%);
  padding: 0 100px;
  height: 66px;
  border-bottom: 3px solid var(--c-gold);
  box-shadow: 0 3px 16px rgba(80,20,0,.35);
}

.header-deco {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(200,160,32,.5));
}
.header-deco.right {
  background: linear-gradient(90deg, rgba(200,160,32,.5), transparent);
}

.sys-title {
  margin: 0;
  font-size: 1.9rem; font-weight: 700;
  color: #fdeabb; letter-spacing: 5px;
  text-shadow: 0 2px 8px rgba(0,0,0,.4), 0 0 20px rgba(200,160,32,.25);
  white-space: nowrap;
}

.header-right-btns {
  position: absolute; right: 18px; top: 50%;
  transform: translateY(-50%);
  display: flex; align-items: center; gap: 10px;
}

.music-btn {
  display: flex; align-items: center; gap: 5px;
  color: #fdeabb; font-size: 13px; cursor: pointer;
  padding: 4px 12px;
  border: 1px solid rgba(253,234,187,.3); border-radius: 20px;
  transition: .2s; user-select: none;
}
.music-btn:hover { background: rgba(253,234,187,.15); }

.music-waves { display: flex; align-items: flex-end; gap: 2px; height: 11px; }
.music-waves i { display: block; width: 2px; background: #fdeabb; border-radius: 1px; height: 40%; }
.music-waves.active i:nth-child(1) { animation: wv .7s infinite alternate; }
.music-waves.active i:nth-child(2) { animation: wv .7s .2s infinite alternate; }
.music-waves.active i:nth-child(3) { animation: wv .7s .4s infinite alternate; }
@keyframes wv { to { height: 100%; } }

.more-btn {
  position: relative;
  color: #fdeabb; font-size: 13px; cursor: pointer;
  padding: 4px 14px;
  border: 1px solid rgba(253,234,187,.3); border-radius: 20px;
  transition: .2s; user-select: none;
}
.more-btn:hover { background: rgba(253,234,187,.15); }

.more-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  background: #fffbf0;
  border: 1px solid var(--c-border);
  border-radius: 6px;
  box-shadow: 0 8px 28px rgba(80,30,0,.18);
  min-width: 150px; z-index: 200;
  overflow: hidden;
}

.dropdown-item {
  padding: 10px 16px; font-size: 13px; color: #5a2d00;
  cursor: pointer; transition: .15s;
  display: flex; align-items: center; gap: 8px;
}
.dropdown-item:hover { background: #f5e8c8; }
.dropdown-divider { height: 1px; background: #e8d5a0; margin: 4px 0; }

/* 导航 */
.sys-nav {
  position: relative; z-index: 10;
  display: flex;
  background: linear-gradient(180deg, #5c2a10 0%, #6b3318 100%);
  border-bottom: 2px solid #a06828;
  box-shadow: 0 2px 8px rgba(60,20,0,.3);
}

.nav-item {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 13px 8px;
  color: #e8c88a; font-size: 14px; font-weight: 600; letter-spacing: 1px;
  cursor: pointer;
  border-right: 1px solid rgba(160,104,40,.4);
  transition: all .2s; position: relative; user-select: none;
}
.nav-item:last-child { border-right: none; }
.nav-item:hover { background: rgba(200,160,32,.15); color: #fdeabb; }
.nav-item.active {
  background: linear-gradient(180deg, #9b3a18, #c04a20);
  color: #fdeabb;
}
.nav-item.active::after {
  content: ''; position: absolute; bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 55%; height: 3px;
  background: var(--c-gold); border-radius: 2px 2px 0 0;
}
.nav-item.danger { color: #ffaaaa; }
.nav-item.danger:hover { background: rgba(180,40,40,.2); }

/* 主内容 */
.sys-main {
  position: relative; z-index: 5;
  flex: 1; display: flex; flex-direction: column;
  padding: 16px 22px;
  overflow: hidden;
}

/* 页脚 */
.sys-footer {
  position: relative; z-index: 10;
  text-align: center; padding: 9px;
  background: linear-gradient(180deg, #5c2a10, #3d1a08);
  color: rgba(253,234,187,.45); font-size: 11px;
  border-top: 1px solid #a06828;
}

/* 下拉动画 */
.dropdown-enter-active, .dropdown-leave-active { transition: all .2s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-8px); }
</style>