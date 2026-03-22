<template>
  <div class="tcm-panel stats-panel">
    <div class="panel-title-bar">
      <span class="panel-step">体质统计分析</span>
      <span class="panel-hint">可视化展示辨识结果分布，辅助社区健康管理决策。</span>
    </div>

    <div v-if="loading" class="loading-box">
      <div class="loading-spin"></div>
      <p>正在加载统计数据...</p>
    </div>

    <div v-else class="stats-body">
      <!-- 顶部汇总卡片 -->
      <div class="summary-row">
        <div class="summary-card" v-for="s in summaryCards" :key="s.label" :style="{'--card-color': s.color}">
          <div class="sc-icon">{{ s.icon }}</div>
          <div class="sc-value">{{ statsData[s.key] ?? 0 }}</div>
          <div class="sc-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- 中间：体质分布 + 说明 -->
      <div class="charts-row">
        <!-- 体质分布条形图 -->
        <div class="chart-card">
          <div class="chart-title">◈ 体质类型辨识分布</div>
          <div class="bar-list">
            <div v-for="item in constitutionList" :key="item.name" class="bar-row">
              <div class="bar-label">{{ item.name }}</div>
              <div class="bar-track">
                <div class="bar-fill"
                  :style="{ width: barWidth(item.count), background: item.color }"
                  :title="`${item.count} 人`">
                </div>
              </div>
              <div class="bar-count">{{ item.count }} 人</div>
              <div class="bar-pct">{{ barPct(item.count) }}</div>
            </div>
          </div>
        </div>

        <!-- 右侧信息面板 -->
        <div class="info-panel">
          <div class="chart-title">◈ 数据概况</div>
          <div class="info-item" v-for="i in infoItems" :key="i.label">
            <span class="info-label">{{ i.label }}</span>
            <span class="info-val" :class="i.cls">{{ statsData[i.key] ?? 0 }} {{ i.unit }}</span>
          </div>

          <div class="chart-title" style="margin-top:18px">◈ 体质说明</div>
          <div class="tip-list">
            <div v-for="c in constitutionList.slice(0,3)" :key="c.name" class="tip-row">
              <span class="tip-dot" :style="{ background: c.color }"></span>
              <span class="tip-name">{{ c.name }}</span>
              <span class="tip-desc">{{ c.desc }}</span>
            </div>
          </div>

          <el-button class="btn-refresh" @click="loadStats" :loading="loading">
            ↺ 刷新
          </el-button>
        </div>
      </div>

      <!-- 底部注释 -->
      <div class="stats-note">
        ⚠ 数据来源于本系统已完成问诊辨识的全部记录；体质分类依据《中医体质分类与判定》（GB/T）国家标准，平和质为理想体质，其余八种为偏颇体质。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const loading = ref(false)
const statsData = ref({
  totalPatients: 0, totalDiagnoses: 0, todayDiagnoses: 0,
})

const summaryCards = [
  { key: 'totalPatients',  label: '登记居民总数', icon: '👥', color: '#4a907e' },
  { key: 'totalDiagnoses', label: '辨识记录总数', icon: '📋', color: '#c8a020' },
  { key: 'todayDiagnoses', label: '今日辨识人次', icon: '📅', color: '#8b1a1a' },
]

const infoItems = [
  { key: 'totalPatients',  label: '累计服务居民', unit: '人', cls: 'green' },
  { key: 'totalDiagnoses', label: '累计四诊记录', unit: '份', cls: 'gold' },
  { key: 'todayDiagnoses', label: '今日新增诊断', unit: '例', cls: 'red' },
]

const constitutionList = ref([
  { name: '平和质', count: 0, color: '#4a907e', desc: '阴阳气血调和，体质较好' },
  { name: '气虚质', count: 0, color: '#e6a23c', desc: '元气不足，疲劳易汗' },
  { name: '阳虚质', count: 0, color: '#f56c6c', desc: '阳气不足，畏寒怕冷' },
  { name: '阴虚质', count: 0, color: '#409eff', desc: '阴液亏少，口燥咽干' },
  { name: '痰湿质', count: 0, color: '#67c23a', desc: '痰湿凝聚，形体肥胖' },
  { name: '湿热质', count: 0, color: '#ff9900', desc: '湿热内蕴，面垢油光' },
  { name: '血瘀质', count: 0, color: '#c0392b', desc: '血行不畅，肤色晦暗' },
  { name: '气郁质', count: 0, color: '#8e44ad', desc: '气机郁滞，神情抑郁' },
  { name: '特禀质', count: 0, color: '#1abc9c', desc: '先天失常，过敏体质' },
])

const totalCount = computed(() =>
  constitutionList.value.reduce((s, c) => s + c.count, 0)
)
const barWidth = (count) => {
  const max = Math.max(...constitutionList.value.map(c => c.count), 1)
  return count > 0 ? Math.max((count / max * 80), 2) + '%' : '2px'
}
const barPct = (count) => {
  if (!totalCount.value) return '0%'
  return (count / totalCount.value * 100).toFixed(1) + '%'
}

const loadStats = async () => {
  loading.value = true
  try {
    const r1 = await axios.get('/api/admin/stats')
    if (r1.data.code === 200) {
      Object.assign(statsData.value, r1.data.data)
    }
    const r2 = await axios.get('/api/admin/constitution-stats')
    if (r2.data.code === 200 && r2.data.data) {
      const map = r2.data.data
      constitutionList.value.forEach(c => { c.count = map[c.name] || 0 })
    }
  } catch { /* 静默 */ } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
@import '@/styles/tcm-shared.css';

.stats-panel { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

.loading-box {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 14px; color: #8b6030;
}
.loading-spin {
  width: 36px; height: 36px;
  border: 3px solid #e8d5a0; border-top-color: #8b3d1a;
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.stats-body {
  flex: 1; display: flex; flex-direction: column; gap: 16px;
  padding: 16px 20px; overflow-y: auto;
}

/* 汇总卡片 */
.summary-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
}
.summary-card {
  background: linear-gradient(135deg, #f9f1d8, #f0e2b8);
  border: 1px solid var(--c-border);
  border-radius: 6px; padding: 16px 20px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: 0 2px 8px rgba(100,60,10,.08);
  position: relative; overflow: hidden;
}
.summary-card::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0;
  width: 4px; background: var(--card-color);
}
.sc-icon { font-size: 28px; }
.sc-value { font-size: 2rem; font-weight: 700; color: var(--card-color); line-height: 1; }
.sc-label { font-size: 12px; color: #6b4c24; margin-top: 4px; }

/* 图表行 */
.charts-row {
  display: grid; grid-template-columns: 1fr 260px; gap: 16px; flex: 1;
}

.chart-card, .info-panel {
  background: #faf3e0; border: 1px solid #e8d5a0; border-radius: 6px; padding: 14px 16px;
}

.chart-title {
  font-size: 13px; font-weight: 700; color: #5a2d00;
  padding-bottom: 8px; border-bottom: 1px solid #e8d5a0; margin-bottom: 12px;
}

/* 条形图 */
.bar-list { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-label { width: 60px; font-size: 12px; color: #5a2d00; font-weight: 600; text-align: right; flex-shrink: 0; }
.bar-track { flex: 1; height: 18px; background: #eee8d8; border-radius: 9px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 9px; transition: width .6s ease; }
.bar-count { width: 44px; font-size: 12px; color: #6b4c24; text-align: right; flex-shrink: 0; }
.bar-pct { width: 42px; font-size: 12px; color: #999; text-align: right; flex-shrink: 0; }

/* 信息面板 */
.info-item {
  display: flex; justify-content: space-between;
  padding: 7px 0; border-bottom: 1px dashed #e8d5a0;
  font-size: 13px;
}
.info-label { color: #6b4c24; }
.info-val { font-weight: 700; font-size: 15px; }
.info-val.green { color: #3a7050; }
.info-val.gold  { color: #c8a020; }
.info-val.red   { color: #8b1a1a; }

.tip-list { display: flex; flex-direction: column; gap: 6px; }
.tip-row { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; }
.tip-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 3px; }
.tip-name { font-weight: 700; color: #5a2d00; white-space: nowrap; }
.tip-desc { color: #8b6030; }

.btn-refresh {
  margin-top: 14px; width: 100%;
  background: #f5f0e6 !important; color: #6b4c24 !important;
  border: 1px solid #c8a96e !important; border-radius: 4px !important; font-size: 13px !important;
}

.stats-note {
  font-size: 11px; color: #9a7040; line-height: 1.7;
  background: #fdf8ef; border: 1px solid #e8d5a0; border-radius: 4px; padding: 8px 12px;
}
</style>