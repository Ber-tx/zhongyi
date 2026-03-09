<template>
  <div class="system-intro-container">
    <!-- 返回按钮 -->
    <div class="nav-bar">
      <el-button circle @click="goBack">
        <el-icon><ArrowLeftBold /></el-icon>
      </el-button>
      <h1 class="page-title">系统介绍</h1>
      <div></div>
    </div>

    <!-- 背景装饰 -->
    <div class="decorative-bg"></div>

    <!-- 主容器 -->
    <div class="content-main">
      <!-- 系统概览卡片 -->
      <section class="glass-card overview-card">
        <div class="card-header">
          <el-icon class="header-icon"><DocumentCopy /></el-icon>
          <h2>中医智慧诊疗系统</h2>
        </div>
        <p class="card-description">
          融合传统中医理论与现代科技，打造智能化的四诊辨识平台。
          通过AI算法与硬件传感器，实现「望闻问切」的数字化，为您的健康保驾护航。
        </p>
      </section>

      <!-- 四诊流程卡片 -->
      <section class="flow-container">
        <h2 class="section-title">四诊智能化流程</h2>
        
        <div class="flow-grid">
          <div class="flow-item glass-card" v-for="(item, index) in diagnosticMethods" :key="index">
            <div class="flow-number">{{ String.fromCharCode(65 + index) }}</div>
            <div class="flow-icon">
              <el-icon :size="48">
                <component :is="item.icon" />
              </el-icon>
            </div>
            <h3>{{ item.name }}</h3>
            <p class="flow-description">{{ item.description }}</p>
            <div class="flow-points">
              <div v-for="point in item.points" :key="point" class="point">
                <el-icon><SuccessFilled /></el-icon>
                <span>{{ point }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 核心特性 -->
      <section class="features-section">
        <h2 class="section-title">核心特性</h2>
        
        <div class="features-grid">
          <div class="feature-item glass-card" v-for="feature in features" :key="feature.id">
            <div class="feature-icon" :style="{ background: feature.color }">
              <el-icon :size="32">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </section>

      <!-- 系统架构 -->
      <section class="architecture-section glass-card">
        <h2 class="section-title">系统架构</h2>
        
        <div class="architecture-diagram">
          <div class="arch-layer">
            <div class="arch-item">
              <el-icon><Connection /></el-icon>
              <span>硬件层</span>
              <small>传感器 / 采集</small>
            </div>
          </div>
          
          <div class="arch-arrow"><el-icon><ArrowDown /></el-icon></div>
          
          <div class="arch-layer">
            <div class="arch-item">
              <el-icon><Cpu /></el-icon>
              <span>数据处理层</span>
              <small>信号处理 / AI分析</small>
            </div>
          </div>
          
          <div class="arch-arrow"><el-icon><ArrowDown /></el-icon></div>
          
          <div class="arch-layer">
            <div class="arch-item">
              <el-icon><Document /></el-icon>
              <span>诊断结果层</span>
              <small>报告生成 / 建议输出</small>
            </div>
          </div>
        </div>
      </section>

      <!-- 优势说明 -->
      <section class="advantages-section">
        <h2 class="section-title">系统优势</h2>
        
        <div class="advantages-list">
          <div class="advantage-item glass-card" v-for="(adv, idx) in advantages" :key="idx">
            <div class="adv-number">{{ idx + 1 }}</div>
            <div>
              <h4>{{ adv.title }}</h4>
              <p>{{ adv.description }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ArrowLeftBold, 
  DocumentCopy, 
  SuccessFilled,
  Connection,
  Cpu,
  Document,
  ArrowDown,
  Setting,
  Timer,
  DataAnalysis,
  TrendCharts,
  ChatDotSquare,
  Collection,
  Bell,
  DataLine,
  View
} from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.push('/')
}

// 四诊方法数据
const diagnosticMethods = ref([
  {
    name: '望诊（观）',
    icon: markRaw(View),
    description: '通过摄像头采集舌象、舌苔等可视化信息',
    points: ['舌色辨识', '舌苔诊断', '神态观察']
  },
  {
    name: '闻诊（听）',
    icon: markRaw(Bell),
    description: '采集并分析患者的声音、呼吸等信息',
    points: ['音频采样', '频谱分析', '特征提取']
  },
  {
    name: '问诊（问）',
    icon: markRaw(ChatDotSquare),
    description: '智能问卷系统，全面采集症状和病史信息',
    points: ['精准提问', '自适应问卷', '症状记录']
  },
  {
    name: '切诊（脉象）',
    icon: markRaw(DataLine),
    description: 'MAX30102传感器实时采集脉搏波形数据',
    points: ['实时监测', '波形分析', '脉象辨识']
  }
])

// 核心特性
const features = ref([
  {
    id: 1,
    icon: markRaw(Cpu),
    title: '智能AI引擎',
    description: '采用深度学习算法，实现中医诊断的智能化',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    id: 2,
    icon: markRaw(DataAnalysis),
    title: '多维数据融合',
    description: '整合望闻问切四诊信息，全面分析',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    id: 3,
    icon: markRaw(Timer),
    title: '实时监测',
    description: '从硬件采集到诊断结果，秒级响应',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    id: 4,
    icon: markRaw(Setting),
    title: '个性化方案',
    description: '根据诊断结果提供定制化的调理建议',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  }
])

// 系统优势
const advantages = ref([
  {
    title: '科学精准',
    description: '基于传统中医理论与现代医学验证，诊断准确率高'
  },
  {
    title: '操作简便',
    description: '一键启动采集，全自动分析处理，用户体验友好'
  },
  {
    title: '即时反馈',
    description: '实时生成诊断报告，快速获得健康建议'
  },
  {
    title: '隐私保护',
    description: '本地数据加密存储，用户信息安全可靠'
  }
])
</script>

<style scoped>
.system-intro-container {
  min-height: 100vh;
  background: url('../assets/images/answerDialog/background_no_scroll.png') no-repeat center center / cover;
  position: relative;
  overflow-x: hidden;
}

/* 背景层 */
.decorative-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.5) 100%);
  z-index: 0;
  pointer-events: none;
}

/* 导航栏 */
.nav-bar {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-title {
  color: white;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

/* 主容器 */
.content-main {
  position: relative;
  z-index: 5;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 玻璃卡片通用样式 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.95);
}

/* 概览卡片 */
.overview-card {
  margin-bottom: 50px;
  text-align: center;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0;
  font-size: 28px;
  color: #2c3e50;
}

.header-icon {
  color: #4ca1af;
  font-size: 32px;
}

.card-description {
  font-size: 16px;
  color: #555;
  line-height: 1.8;
  margin: 0;
}

/* 部分标题 */
.section-title {
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin-bottom: 30px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  position: relative;
  padding-bottom: 15px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #4ca1af, transparent);
  border-radius: 2px;
}

/* 流程卡片 */
.flow-container {
  margin-bottom: 60px;
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-top: 25px;
}

.flow-item {
  text-align: center;
  position: relative;
  overflow: hidden;
}

.flow-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4ca1af, #2c3e50);
}

.flow-number {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 32px;
  height: 32px;
  background: #4ca1af;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.flow-icon {
  margin: 25px 0 15px 0;
  color: #4ca1af;
}

.flow-item h3 {
  font-size: 18px;
  color: #2c3e50;
  margin: 15px 0;
}

.flow-description {
  color: #666;
  font-size: 13px;
  margin-bottom: 15px;
}

.flow-points {
  text-align: left;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.point {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 12px;
  margin-bottom: 8px;
}

.point :deep(.el-icon) {
  color: #4ca1af;
  flex-shrink: 0;
}

.point:last-child {
  margin-bottom: 0;
}

/* 特性网格 */
.features-section {
  margin-bottom: 60px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-top: 25px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 15px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.feature-item h3 {
  font-size: 16px;
  color: #2c3e50;
  margin: 10px 0;
}

.feature-item p {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 架构图 */
.architecture-section {
  margin-bottom: 60px;
}

.architecture-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 25px;
}

.arch-layer {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
}

.arch-item {
  background: linear-gradient(135deg, #4ca1af 0%, #2c3e50 100%);
  color: white;
  padding: 20px 30px;
  border-radius: 12px;
  min-width: 180px;
  text-align: center;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.arch-item small {
  opacity: 0.8;
  font-size: 12px;
}

.arch-arrow {
  color: #4ca1af;
  font-size: 28px;
  margin: 10px 0;
}

/* 优势列表 */
.advantages-section {
  margin-bottom: 60px;
}

.advantages-list {
  display: grid;
  gap: 20px;
  margin-top: 25px;
}

.advantage-item {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.adv-number {
  min-width: 50px;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #4ca1af 0%, #2c3e50 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  flex-shrink: 0;
}

.advantage-item h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.advantage-item p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-bar {
    padding: 15px 20px;
  }

  .page-title {
    font-size: 20px;
  }

  .content-main {
    padding: 20px 15px;
  }

  .glass-card {
    padding: 20px;
  }

  .section-title {
    font-size: 20px;
  }

  .flow-grid {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .advantage-item {
    flex-direction: column;
    align-items: center;
  }
}
</style>
