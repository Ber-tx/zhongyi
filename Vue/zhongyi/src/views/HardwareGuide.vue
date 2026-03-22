<template>
  <div class="hardware-guide-container">
    <div class="nav-bar">
      <el-button circle @click="goBack">
        <el-icon><ArrowLeftBold /></el-icon>
      </el-button>
      <h1 class="page-title">硬件使用指引</h1>
      <div></div>
    </div>

    <div class="decorative-bg"></div>

    <div class="content-main">

      <!-- 设备介绍 -->
      <section class="glass-card overview-card">
        <div class="card-header">
          <el-icon class="header-icon"><Watch /></el-icon>
          <h2>脉诊采集仪</h2>
        </div>
        <p class="card-description">
          只需将手指轻放在传感器上，设备即可自动采集您的心率与血氧数据，整个过程约 30 秒，安全无创、简单方便。
        </p>
      </section>

      <!-- 使用步骤 -->
      <section class="steps-section">
        <h2 class="section-title">使用步骤</h2>
        <div class="steps-grid">
          <div class="step-card glass-card" v-for="(step, i) in steps" :key="i">
            <div class="step-badge">{{ i + 1 }}</div>
            <div class="step-icon-wrap">
              <el-icon :size="40"><component :is="step.icon" /></el-icon>
            </div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.desc }}</p>
          </div>
        </div>
      </section>

      <!-- 注意事项 -->
      <section class="tips-section">
        <h2 class="section-title">注意事项</h2>
        <div class="tips-grid">
          <div class="tip-card glass-card" v-for="tip in tips" :key="tip.title">
            <div class="tip-icon" :style="{ background: tip.color }">
              <el-icon :size="26"><component :is="tip.icon" /></el-icon>
            </div>
            <div>
              <h4>{{ tip.title }}</h4>
              <p>{{ tip.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 常见问题 -->
      <section class="faq-section">
        <h2 class="section-title">常见问题</h2>
        <div class="faq-list">
          <el-collapse>
            <el-collapse-item v-for="faq in faqs" :key="faq.q" :title="faq.q">
              <p class="faq-answer">{{ faq.a }}</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { markRaw } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeftBold,
  Watch,
  Connection,
  Pointer,
  Timer,
  CircleCheck,
  Warning,
  TurnOff,
  Sunny,
  MostlyCloudy,
} from '@element-plus/icons-vue'

const router = useRouter()
const goBack = () => router.push('/')

const steps = [
  {
    icon: markRaw(Connection),
    title: '开启设备',
    desc: '确认脉诊仪已通过USB供电，设备指示灯亮起表示已就绪。'
  },
  {
    icon: markRaw(Pointer),
    title: '放置手指',
    desc: '将食指或中指指腹平放在传感器凹槽内，轻压即可，无需用力。'
  },
  {
    icon: markRaw(Timer),
    title: '保持静止',
    desc: '手指放置后保持30秒不动，避免晃动以确保数据准确。'
  },
  {
    icon: markRaw(CircleCheck),
    title: '完成采集',
    desc: '系统自动检测完成后会提示采集成功，数据将自动上传至诊断系统。'
  },
]

const tips = [
  {
    icon: markRaw(Warning),
    title: '保持手指干燥',
    desc: '手指潮湿或有污渍时，请擦干后再进行采集，避免影响传感精度。',
    color: 'linear-gradient(135deg, #8b3d1a, #c04a20)'
  },
  {
    icon: markRaw(Sunny),
    title: '避免强光直射',
    desc: '请在室内或避光环境下使用，强烈阳光可能干扰光学传感器。',
    color: 'linear-gradient(135deg, #c8a020, #a06828)'
  },
  {
    icon: markRaw(MostlyCloudy),
    title: '放松状态检测',
    desc: '检测前请静坐休息1~2分钟，情绪激动或运动后立即测量会影响结果。',
    color: 'linear-gradient(135deg, #4a907e, #2d7d65)'
  },
  {
    icon: markRaw(TurnOff),
    title: '不使用时请断电',
    desc: '长时间不使用时，建议拔掉USB电源，延长设备使用寿命。',
    color: 'linear-gradient(135deg, #6b4c24, #8b6030)'
  },
]

const faqs = [
  {
    q: '设备指示灯不亮怎么办？',
    a: '请检查USB供电线是否连接稳固，尝试更换USB口或数据线。若仍无反应，请联系工作人员。'
  },
  {
    q: '放上手指后一直检测不到信号？',
    a: '请确认手指完全覆盖传感器，并保持放松状态，避免手指颤抖。手太凉时可先搓热手指再测试。'
  },
  {
    q: '数据显示异常或心率过高/过低？',
    a: '请重新放置手指，保持静止后再次尝试。若多次异常请告知工作人员。'
  },
  {
    q: '电脑识别不到串口设备怎么办？',
    a: '应该是串口被占用或驱动未安装，尝试选择其他串口或重新安装驱动。'
  },
]
</script>

<style scoped>
.hardware-guide-container {
  min-height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  position: relative;
  overflow-x: hidden;
}

.hardware-guide-container::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

.decorative-bg {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
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
  padding: 18px 32px;
  background: linear-gradient(180deg, #6b2d12 0%, #8b3d1a 100%);
  border-bottom: 2px solid #c8a020;
  box-shadow: 0 2px 12px rgba(60,20,0,.25);
}

.nav-bar :deep(.el-button) {
  background: rgba(200,160,32,.15) !important;
  color: #fdeabb !important;
  border: 1px solid rgba(200,160,32,.3) !important;
}
.nav-bar :deep(.el-button:hover) { background: rgba(200,160,32,.25) !important; }

.page-title {
  color: #fdeabb;
  font-size: 22px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 2px;
}

.content-main {
  position: relative;
  z-index: 5;
  max-width: 1100px;
  margin: 0 auto;
  padding: 36px 20px 56px;
}

.glass-card {
  background: rgba(255, 252, 242, 0.92);
  backdrop-filter: blur(15px);
  border: 1px solid #d4b483;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(100,60,10,.08), inset 0 1px 0 rgba(255,248,220,.6);
  transition: all 0.3s;
}

.glass-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(100,60,10,.12);
  border-color: #c8a96e;
}

.overview-card {
  margin-bottom: 40px;
  text-align: center;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-header h2 { margin: 0; font-size: 24px; color: #3d2b10; }
.header-icon { color: #8b3d1a; font-size: 30px; }
.card-description { font-size: 15px; color: #6b4c24; line-height: 1.9; margin: 0; }

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #3d2b10;
  margin-bottom: 24px;
  padding-bottom: 12px;
  position: relative;
  border-bottom: 1px solid #e8d5a0;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0;
  width: 50px; height: 3px;
  background: linear-gradient(90deg, #8b3d1a, #c8a020);
  border-radius: 2px;
}

/* 步骤 */
.steps-section { margin-bottom: 40px; }

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.step-card {
  text-align: center;
  position: relative;
  padding-top: 36px;
}

.step-badge {
  position: absolute;
  top: -16px;
  left: 50%;
  transform: translateX(-50%);
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #8b3d1a, #c04a20);
  color: #fdeabb;
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(139,61,26,.35);
}

.step-icon-wrap { color: #8b3d1a; margin-bottom: 14px; }
.step-card h3 { font-size: 16px; color: #3d2b10; margin: 0 0 10px; }
.step-card p  { font-size: 13px; color: #6b4c24; line-height: 1.7; margin: 0; }

/* 注意事项 */
.tips-section { margin-bottom: 40px; }

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
}

.tip-card {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.tip-icon {
  width: 52px; height: 52px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(0,0,0,.2);
}

.tip-card h4 { margin: 0 0 6px; color: #3d2b10; font-size: 14px; font-weight: 600; }
.tip-card p  { margin: 0; color: #6b4c24; font-size: 13px; line-height: 1.6; }

/* 常见问题 */
.faq-section { margin-bottom: 20px; }

.faq-list :deep(.el-collapse) { border: none; background: transparent; }

.faq-list :deep(.el-collapse-item__header) {
  background: rgba(255, 252, 242, 0.92);
  border-radius: 10px;
  padding: 0 20px;
  font-size: 14px;
  font-weight: 600;
  color: #3d2b10;
  margin-bottom: 8px;
  border: 1px solid #d4b483;
  height: 52px;
}

.faq-list :deep(.el-collapse-item__wrap) {
  background: rgba(255, 252, 242, 0.85);
  border-radius: 0 0 10px 10px;
  border: 1px solid #d4b483;
  border-top: none;
  margin-bottom: 8px;
}

.faq-list :deep(.el-collapse-item__content) { padding: 16px 20px; }

.faq-answer { margin: 0; color: #6b4c24; font-size: 13px; line-height: 1.8; }

@media (max-width: 768px) {
  .nav-bar { padding: 14px 20px; }
  .page-title { font-size: 18px; }
  .content-main { padding: 24px 16px 40px; }
  .steps-grid { grid-template-columns: 1fr 1fr; }
  .tips-grid { grid-template-columns: 1fr; }
}
</style>
