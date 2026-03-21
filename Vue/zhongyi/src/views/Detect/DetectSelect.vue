<template>
  <div class="detect-container">
    <div class="bg-texture"></div>

    <div class="content-wrapper">
      <!-- 页眉 -->
      <header class="detect-header">
        <el-button class="back-btn" @click="router.push('/')">← 返回主页</el-button>
        <div class="header-center">
          <p class="header-sub">AI-POWERED TCM</p>
          <h1 class="header-title">四诊合参 <span class="dot">·</span> 智慧诊断</h1>
          <p class="header-desc">融合传统医学智慧与现代人工智能技术</p>
        </div>
        <div class="patient-info" v-if="lockedPatientId">
          <span class="patient-tag">
            <span class="patient-dot"></span>
            当前就诊 ID：{{ lockedPatientId }}
          </span>
        </div>
      </header>

      <!-- 四诊卡片 -->
      <div class="cards-grid">
        <div
          v-for="item in diagItems"
          :key="item.key"
          class="diag-card"
          :class="{ 'is-done': statusMap[item.key] }"
          @click="goTo(item.key)"
        >
          <div v-if="statusMap[item.key]" class="done-badge">
            <span>✓</span> 已完成
          </div>

          <div class="card-icon-wrap">
            <div class="card-icon" :style="{ background: item.color }">
              {{ item.char }}
            </div>
          </div>

          <div class="card-body">
            <h3 class="card-title">{{ item.title }}</h3>
            <p class="card-desc">{{ item.desc }}</p>
          </div>

          <div class="card-footer">
            <span class="card-action">
              {{ statusMap[item.key] ? '结果已锁定' : item.action }}
            </span>
            <span class="card-arrow">{{ statusMap[item.key] ? '🔒' : '→' }}</span>
          </div>
        </div>
      </div>

      <!-- 进度 + 报告区 -->
      <div class="bottom-section">
        <!-- 左侧：已完成标签 -->
        <div class="completed-area">
          <div class="progress-label">
            四诊完成进度
            <span class="count-badge">{{ completedCount }} / 4</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: (completedCount * 25) + '%' }"></div>
          </div>
          <div class="completed-tags" v-if="completedCount > 0">
            <el-tag v-if="wangFinished"    size="small" class="ctag">✓ 望诊</el-tag>
            <el-tag v-if="wenFinished"     size="small" class="ctag">✓ 闻诊</el-tag>
            <el-tag v-if="wenjuanFinished" size="small" class="ctag">✓ 问诊</el-tag>
            <el-tag v-if="qieFinished"     size="small" class="ctag">✓ 切诊</el-tag>
          </div>
          <p v-else class="no-data-tip">请完成至少一个诊断板块后生成报告</p>
        </div>

        <!-- 右侧：生成报告 -->
        <div class="report-area" v-if="completedCount > 0">
          <el-button class="btn-report" @click="generateReport" :loading="isGenerating">
            {{ completedCount === 4 ? '生成四诊合参报告' : `生成报告（已完成 ${completedCount} 项）` }} →
          </el-button>
          <p class="report-hint" v-if="completedCount < 4">
            完成全部四诊可获得更精准的综合诊断
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { Right, CircleCheckFilled } from '@element-plus/icons-vue'
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route  = useRoute()

const lockedPatientId = ref(null)
const lockedIdCard    = ref('')

const wangFinished    = ref(false)
const wenFinished     = ref(false)
const wenjuanFinished = ref(false)
const qieFinished     = ref(false)
const isGenerating    = ref(false)

const statusMap = computed(() => ({
  wang:    wangFinished.value,
  wen:     wenFinished.value,
  wenjuan: wenjuanFinished.value,
  qie:     qieFinished.value,
}))

const completedCount = computed(() =>
  [wangFinished, wenFinished, wenjuanFinished, qieFinished].filter(v => v.value).length
)

const diagItems = [
  {
    key: 'wang', char: '望', title: '望诊分析',
    desc: '基于计算机视觉提取舌质、舌苔及面部色泽特征。',
    action: '开始采集 →',
    color: 'linear-gradient(135deg, #4a8fc4 0%, #2d6ea8 100%)',
  },
  {
    key: 'wen', char: '闻', title: '闻诊分析',
    desc: '通过声纹识别技术分析呼吸声与语音，辨析脏腑虚实。',
    action: '音频录制 →',
    color: 'linear-gradient(135deg, #5aab60 0%, #357a3a 100%)',
  },
  {
    key: 'wenjuan', char: '问', title: '问诊分析',
    desc: '系统化交互问卷，深度梳理自觉症状与生活习惯。',
    action: '填写问卷 →',
    color: 'linear-gradient(135deg, #c8861a 0%, #9a6010 100%)',
  },
  {
    key: 'qie', char: '切', title: '切诊分析',
    desc: '数字化脉波采集，实时呈现指下脉象的位、数、形、势。',
    action: '连接设备 →',
    color: 'linear-gradient(135deg, #b54a3a 0%, #8b2a1e 100%)',
  },
]

const refreshStatuses = () => {
  const currentId = lockedPatientId.value || localStorage.getItem('current_patient_id')
  if (!currentId) return
  if (!lockedPatientId.value) {
    lockedPatientId.value = currentId
    lockedIdCard.value = localStorage.getItem('current_patient_idCard') || ''
  }
  const id = String(currentId)
  wangFinished.value    = localStorage.getItem('wang_finished_id')    === id
  wenFinished.value     = localStorage.getItem('wen_finished_id')     === id
  wenjuanFinished.value = localStorage.getItem('wenjuan_finished_id') === id
  qieFinished.value     = localStorage.getItem('qie_finished_id')     === id
}

const goTo = (type) => {
  if (statusMap.value[type]) {
    ElMessage.info('该检测项目已完成，结果已锁定')
    return
  }
  router.push({
    path:  `/detect/${type}`,
    query: { id: lockedPatientId.value, idCard: lockedIdCard.value },
  })
}

const generateReport = () => {
  const patientId = lockedPatientId.value || localStorage.getItem('current_patient_id')
  if (!patientId) { ElMessage.error('缺少病人ID，请重新登录'); return }
  const completedTypes = []
  if (wangFinished.value)    completedTypes.push('wang')
  if (wenFinished.value)     completedTypes.push('wen_audio')
  if (wenjuanFinished.value) completedTypes.push('wen_questionnaire')
  if (qieFinished.value)     completedTypes.push('qie')
  router.push({ path: '/report', query: { id: patientId, completedTypes: completedTypes.join(',') } })
}

onMounted(() => refreshStatuses())
onActivated(() => {
  const latest = localStorage.getItem('current_patient_id')
  if (latest !== lockedPatientId.value) {
    lockedPatientId.value = latest
    lockedIdCard.value = localStorage.getItem('current_patient_idCard') || ''
  }
  refreshStatuses()
})
watch(() => route.fullPath, refreshStatuses)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap');

.detect-container {
  min-height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
  color: #3d2b10;
  position: relative;
  display: flex; align-items: flex-start; justify-content: center;
  padding: 0 0 48px;
}

/* 宣纸纹理 */
.bg-texture {
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
  pointer-events: none; z-index: 0;
}

.content-wrapper {
  position: relative; z-index: 5;
  width: 100%; max-width: 1200px;
  padding: 0 24px;
}

/* ===== 页眉 ===== */
.detect-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 22px 0 20px;
  border-bottom: 1px solid #e8d5a0;
  margin-bottom: 32px;
}

.back-btn {
  background: rgba(139,61,26,.08) !important;
  color: #6b4c24 !important;
  border: 1px solid #c8a96e !important;
  border-radius: 4px !important;
  font-family: inherit !important;
  font-size: 13px !important;
}
.back-btn:hover { background: rgba(139,61,26,.16) !important; }

.header-center { text-align: center; flex: 1; }
.header-sub { font-size: 11px; letter-spacing: 4px; color: #9a7040; margin: 0 0 6px; }
.header-title {
  font-size: 2.2rem; font-weight: 700; color: #3d2b10;
  margin: 0 0 8px; letter-spacing: 3px;
}
.dot { color: #c8a020; }
.header-desc { font-size: 13px; color: #8b6030; margin: 0; }

.patient-tag {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 13px; color: #5a2d00;
  background: linear-gradient(135deg, #f5e4a8, #ebd07a);
  border: 1px solid #c8a020;
  padding: 5px 14px; border-radius: 20px;
}
.patient-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #4a907e;
  animation: blink 2s infinite;
}
@keyframes blink { 50% { opacity: .4; } }

/* ===== 四诊卡片 ===== */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.diag-card {
  position: relative;
  background: rgba(255, 252, 242, 0.92);
  border: 1px solid #d4b483;
  border-radius: 8px;
  padding: 28px 22px 20px;
  cursor: pointer;
  transition: all .3s ease;
  display: flex; flex-direction: column;
  box-shadow: 0 3px 12px rgba(100,60,10,.08),
              inset 0 1px 0 rgba(255,248,220,.8);
  overflow: hidden;
}

/* 顶部金线装饰 */
.diag-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, #c8a020, transparent);
  opacity: .5;
}

.diag-card:hover:not(.is-done) {
  transform: translateY(-6px);
  box-shadow: 0 14px 36px rgba(100,60,10,.16),
              inset 0 1px 0 rgba(255,248,220,.8);
  border-color: #c8a020;
  background: #fffdf5;
}

.diag-card.is-done {
  background: linear-gradient(160deg, #f5ead0 0%, #fdf5e0 100%);
  border-color: #b8963a;
  cursor: not-allowed;
  opacity: .82;
}
.diag-card.is-done::after {
  content: '';
  position: absolute; inset: 0;
  background: repeating-linear-gradient(
    -45deg, transparent, transparent 8px,
    rgba(200,160,32,.04) 8px, rgba(200,160,32,.04) 9px
  );
  pointer-events: none;
}

.done-badge {
  position: absolute; top: 12px; right: 12px;
  background: linear-gradient(135deg, #4a907e, #2d7d65);
  color: #fff; font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 10px;
  display: flex; align-items: center; gap: 4px;
  box-shadow: 0 2px 8px rgba(74,144,126,.4);
}

.card-icon-wrap { margin-bottom: 18px; }
.card-icon {
  width: 60px; height: 60px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; color: white; font-weight: 700;
  font-family: 'Noto Serif SC', "KaiTi", serif;
  box-shadow: 0 4px 14px rgba(0,0,0,.2);
}

.card-body { flex: 1; }
.card-title { font-size: 17px; font-weight: 700; color: #3d2b10; margin: 0 0 10px; }
.card-desc  { font-size: 13px; color: #7a5520; line-height: 1.7; margin: 0; }

.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 18px; padding-top: 14px;
  border-top: 1px solid #e8d5a0;
}
.card-action { font-size: 13px; font-weight: 600; color: #8b3d1a; }
.diag-card.is-done .card-action { color: #6b8b6a; }
.card-arrow { font-size: 16px; color: #c8a020; transition: transform .3s; }
.diag-card:hover:not(.is-done) .card-arrow { transform: translateX(5px); }

/* ===== 底部区域 ===== */
.bottom-section {
  display: flex; align-items: center; justify-content: space-between; gap: 24px;
  padding: 20px 28px;
  background: rgba(255, 252, 242, 0.9);
  border: 1px solid #d4b483;
  border-radius: 8px;
  box-shadow: 0 3px 12px rgba(100,60,10,.08);
}

.completed-area { flex: 1; }

.progress-label {
  font-size: 13px; font-weight: 600; color: #5a2d00;
  margin-bottom: 10px;
  display: flex; align-items: center; gap: 10px;
}
.count-badge {
  background: linear-gradient(135deg, #8b3d1a, #c04a20);
  color: #fdeabb; font-size: 12px; font-weight: 700;
  padding: 2px 10px; border-radius: 10px;
}

.progress-track {
  width: 100%; height: 8px;
  background: #e8d5a0; border-radius: 4px; overflow: hidden;
  margin-bottom: 12px;
}
.progress-fill {
  height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, #8b3d1a, #c8a020);
  transition: width .6s ease;
}

.completed-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.ctag {
  background: #f0f9eb !important;
  border-color: #4a907e !important;
  color: #2d7d65 !important;
  font-weight: 600 !important;
}

.no-data-tip { font-size: 12px; color: #b09060; margin: 8px 0 0; }

.report-area { text-align: right; flex-shrink: 0; }

.btn-report {
  background: linear-gradient(135deg, #8b3d1a, #c04a20) !important;
  color: #fdeabb !important; border: none !important;
  padding: 12px 32px !important;
  font-size: 14px !important; font-weight: 700 !important;
  letter-spacing: 1px !important; border-radius: 4px !important;
  font-family: inherit !important;
  box-shadow: 0 4px 14px rgba(139,61,26,.35) !important;
  transition: all .3s !important;
  white-space: nowrap !important;
}
.btn-report:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(139,61,26,.45) !important; }

.report-hint { font-size: 12px; color: #9a7040; margin: 8px 0 0; text-align: right; }

/* ===== 响应式 ===== */
@media (max-width: 960px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
  .header-title { font-size: 1.6rem; }
  .detect-header { flex-direction: column; gap: 12px; }
  .bottom-section { flex-direction: column; align-items: stretch; }
  .report-area { text-align: center; }
  .btn-report { width: 100% !important; }
}
@media (max-width: 560px) {
  .cards-grid { grid-template-columns: 1fr; }
}
</style>