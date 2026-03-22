<template>
  <div class="intro-wrap">
    <header class="nav-bar">
      <el-button circle @click="goBack" class="back-btn">
        <el-icon><ArrowLeftBold /></el-icon>
      </el-button>
      <h1 class="page-title">系统介绍</h1>
      <div></div>
    </header>

    <div class="bg-layer"></div>
    <main class="main">
      <section class="card intro-card">
        <div class="card-head">
          <el-icon class="head-icon"><DocumentCopy /></el-icon>
          <h2>中医智慧诊疗系统</h2>
        </div>
        <p class="intro-desc">
          融合传统中医四诊与现代 AI、硬件传感技术，为社区、体检机构及中医诊所提供体质辨识与健康管理平台。
          涵盖患者登记、望闻问切采集、AI 辨证、报告生成与档案管理，支持单板块快速初诊与完整四诊合参。
        </p>
      </section>

      <section>
        <h2 class="sec-title">功能模块</h2>
        <div class="grid">
          <div class="card item-card" v-for="m in mainModules" :key="m.id">
            <div class="item-icon" :style="{ background: m.color }">
              <el-icon :size="24"><component :is="m.icon" /></el-icon>
            </div>
            <h3>{{ m.title }}</h3>
            <p>{{ m.desc }}</p>
          </div>
        </div>
      </section>

      <section>
        <h2 class="sec-title">更多功能</h2>
        <p class="sec-hint">主页右上角「更多功能 ▾」下拉菜单中包含：</p>
        <div class="grid more-grid">
          <div class="card item-card" v-for="x in moreItems" :key="x.title">
            <div class="item-icon small" :style="{ background: x.color }">{{ x.emoji }}</div>
            <h3>{{ x.title }}</h3>
            <p>{{ x.desc }}</p>
          </div>
        </div>
      </section>

      <section>
        <h2 class="sec-title">四诊流程</h2>
        <div class="grid flow-grid">
          <div class="card flow-card" v-for="(d, i) in diagnostics" :key="i">
            <span class="flow-num">{{ String.fromCharCode(65 + i) }}</span>
            <div class="flow-icon" :style="{ color: d.accent }">
              <el-icon :size="40"><component :is="d.icon" /></el-icon>
            </div>
            <h3>{{ d.name }}</h3>
            <p>{{ d.desc }}</p>
            <div class="flow-pts">
              <span v-for="pt in d.pts" :key="pt">{{ pt }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="card compact-card">
        <h2 class="sec-title">报告与硬件</h2>
        <p>
          报告支持<strong>部分诊断</strong>（1～4 板块任意组合）与<strong>四诊合参</strong>，AI 生成辨证与调理建议，可 PDF 导出、打印。
          望诊需摄像头/拍照，闻诊需麦克风，问诊为 33 项问卷，切诊需 MAX30102 脉诊仪（详见 <router-link to="/hardware">硬件指引</router-link>）。
        </p>
      </section>

      <section>
        <h2 class="sec-title">使用流程</h2>
        <div class="steps">
          <div class="step" v-for="(s, i) in steps" :key="i">
            <span class="step-num">{{ i + 1 }}</span>
            <div>
              <h4>{{ s.title }}</h4>
              <p>{{ s.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="card compact-card disclaimer">
        <el-icon class="disclaimer-icon"><Warning /></el-icon>
        <p>本系统由 AI 辅助分析，<strong>仅供健康参考</strong>，不作为临床诊断依据。确诊与用药请咨询专业医师。</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeftBold, DocumentCopy, Warning,
  User, FolderOpened, Timer, TrendCharts,
  View, Bell, ChatDotSquare, DataLine
} from '@element-plus/icons-vue'

const router = useRouter()
const goBack = () => router.push('/')

const grad = {
  red: 'linear-gradient(135deg, #8b3d1a 0%, #c04a20 100%)',
  green: 'linear-gradient(135deg, #4a907e 0%, #2d7d65 100%)',
  gold: 'linear-gradient(135deg, #c8a020 0%, #a06828 100%)',
  brown: 'linear-gradient(135deg, #6b4c24 0%, #8b6030 100%)'
}

const mainModules = ref([
  { id: 1, icon: markRaw(User), title: '开始测试', desc: '患者登记后进入四诊采集，任意组合完成即可生成报告', color: grad.red },
  { id: 2, icon: markRaw(FolderOpened), title: '辨识档案管理', desc: '历史诊断、报告详情，按患者/日期检索导出', color: grad.green },
  { id: 3, icon: markRaw(Timer), title: '居民体检管理', desc: '关联健康档案，体检与体质辨识一体化', color: grad.gold },
  { id: 4, icon: markRaw(TrendCharts), title: '体质统计分析', desc: '体质分布、趋势分析，支撑健康管理决策', color: grad.brown }
])

const moreItems = ref([
  { emoji: '📖', title: '系统介绍', desc: '本页，全面了解系统架构与使用说明', color: grad.red },
  { emoji: '🔧', title: '硬件指引', desc: '脉诊采集仪使用步骤、注意事项与常见问题', color: grad.green },
  { emoji: '🏮', title: '中医文化', desc: '治未病、音乐养生、儿童调养等模块，拓展中医知识', color: grad.gold },
  { emoji: '📄', title: '报告设置', desc: '自定义机构名称、签发医师、免责声明，显示在报告抬头', color: grad.brown },
  { emoji: '⚙️', title: '管理后台', desc: '管理员登录，数据统计与系统配置', color: grad.brown }
])

const diagnostics = ref([
  { name: '望诊', icon: markRaw(View), desc: '摄像头/拍照采集舌象，AI 分析舌质舌苔', pts: ['舌色辨识', '舌苔厚薄', '辨证模型'], accent: '#409eff' },
  { name: '闻诊', icon: markRaw(Bell), desc: '录制语音与呼吸，声纹频谱分析体质倾向', pts: ['音频采样', '频谱分析', '体质标签'], accent: '#67c23a' },
  { name: '问诊', icon: markRaw(ChatDotSquare), desc: '33 项体质问卷，含 BMI 自动计算', pts: ['精准提问', '自适应问卷', '症状量化'], accent: '#e6a23c' },
  { name: '切诊', icon: markRaw(DataLine), desc: 'MAX30102 采集 PPG，实时心率血氧与脉象', pts: ['实时监测', '波形可视化', '脉象建议'], accent: '#f56c6c' }
])

const steps = ref([
  { title: '患者登记', desc: '在「开始测试」录入信息，获得就诊 ID' },
  { title: '选择诊断', desc: '按需完成望、闻、问、切各板块' },
  { title: '采集分析', desc: '按指引采集，系统自动 AI 分析' },
  { title: '生成报告', desc: '任一板块完成可生成报告，支持 PDF 导出' },
  { title: '档案管理', desc: '在「辨识档案管理」查阅历史，支持复诊对比' }
])
</script>

<style scoped>
.intro-wrap {
  min-height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  position: relative;
}

.intro-wrap::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

.bg-layer {
  position: fixed;
  inset: 0;
  background: linear-gradient(180deg, rgba(245,232,200,0.4) 0%, transparent 40%, transparent 60%, rgba(139,61,26,0.05) 100%);
  z-index: 0;
  pointer-events: none;
}

.nav-bar {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 28px;
  background: linear-gradient(180deg, #6b2d12 0%, #8b3d1a 100%);
  border-bottom: 2px solid #c8a020;
  box-shadow: 0 2px 12px rgba(60,20,0,.25);
}

.back-btn {
  background: rgba(200,160,32,.15) !important;
  color: #fdeabb !important;
  border: 1px solid rgba(200,160,32,.3) !important;
}
.back-btn:hover { background: rgba(200,160,32,.25) !important; }

.page-title {
  color: #fdeabb;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 2px;
}

.main {
  position: relative;
  z-index: 5;
  max-width: 1000px;
  margin: 0 auto;
  padding: 28px 20px 48px;
}

.sec-title {
  font-size: 18px;
  font-weight: 700;
  color: #3d2b10;
  margin: 0 0 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8d5a0;
  position: relative;
}

.sec-title::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(90deg, #8b3d1a, #c8a020);
  border-radius: 2px;
}

.sec-hint {
  font-size: 13px;
  color: #8b6030;
  margin: 0 0 16px;
}

.card {
  background: rgba(255, 252, 242, 0.92);
  backdrop-filter: blur(12px);
  border: 1px solid #d4b483;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 3px 14px rgba(100,60,10,.06);
  transition: all 0.25s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(100,60,10,.1);
  border-color: #c8a96e;
}

.intro-card {
  margin-bottom: 36px;
  text-align: center;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
}

.card-head h2 { margin: 0; font-size: 22px; color: #3d2b10; }
.head-icon { color: #8b3d1a; font-size: 26px; }

.intro-desc {
  font-size: 14px;
  color: #6b4c24;
  line-height: 1.8;
  margin: 0;
}

section { margin-bottom: 36px; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.more-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }

.item-card {
  text-align: center;
}

.item-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 3px 10px rgba(0,0,0,.2);
}

.item-icon.small {
  width: 40px;
  height: 40px;
  font-size: 18px;
}

.item-card h3 {
  font-size: 15px;
  color: #3d2b10;
  margin: 0 0 8px;
}

.item-card p {
  font-size: 12px;
  color: #6b4c24;
  line-height: 1.55;
  margin: 0;
}

.flow-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

.flow-card {
  text-align: center;
  position: relative;
}

.flow-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #8b3d1a, #c8a020);
  border-radius: 10px 10px 0 0;
}

.flow-num {
  position: absolute;
  top: 10px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #8b3d1a, #c04a20);
  color: #fdeabb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.flow-icon { margin: 20px 0 10px; }

.flow-card h3 { font-size: 15px; color: #3d2b10; margin: 0 0 8px; }
.flow-card p { font-size: 12px; color: #6b4c24; margin-bottom: 10px; line-height: 1.5; }

.flow-pts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  border-top: 1px solid #e8d5a0;
  padding-top: 10px;
}

.flow-pts span {
  font-size: 11px;
  color: #8b6030;
  background: rgba(232,213,160,.3);
  padding: 2px 8px;
  border-radius: 4px;
}

.compact-card p {
  font-size: 14px;
  color: #5a2d00;
  line-height: 1.8;
  margin: 0;
}

.compact-card :deep(a) {
  color: #8b3d1a;
  font-weight: 600;
  text-decoration: none;
}
.compact-card :deep(a:hover) { text-decoration: underline; }

.steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px 18px;
  background: rgba(255, 252, 242, 0.8);
  border: 1px solid #e8d5a0;
  border-radius: 8px;
}

.step-num {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #8b3d1a, #c04a20);
  color: #fdeabb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 13px;
  flex-shrink: 0;
}

.step h4 { margin: 0 0 4px; font-size: 14px; color: #3d2b10; }
.step p { margin: 0; font-size: 12px; color: #6b4c24; line-height: 1.55; }

.disclaimer {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  background: rgba(253,240,230,.95) !important;
  border-color: #e8b89a !important;
}

.disclaimer-icon { color: #c0392b; font-size: 22px; flex-shrink: 0; }
.disclaimer p { margin: 0; font-size: 13px; color: #6b4c24; line-height: 1.7; }

@media (max-width: 768px) {
  .nav-bar { padding: 12px 20px; }
  .page-title { font-size: 17px; }
  .main { padding: 20px 16px 36px; }
  .grid { grid-template-columns: 1fr; }
  .more-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
