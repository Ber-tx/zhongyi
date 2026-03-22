<template>
  <div class="admin-layout">

    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="brand-char">管</span>
        <div class="brand-text">
          <div class="brand-name">中医系统</div>
          <div class="brand-sub">管理后台</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div
          v-for="item in navItems"
          :key="item.key"
          class="nav-item"
          :class="{ active: activeTab === item.key }"
          @click="activeTab = item.key"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="admin-user">
          <el-icon><Avatar /></el-icon>
          <span>{{ adminUsername }}</span>
        </div>
        <el-button link class="logout-btn" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">

      <header class="top-bar">
        <h1 class="page-title">{{ currentTitle }}</h1>
        <span class="date-tag">{{ todayStr }}</span>
      </header>

      <!-- ===== 概览 ===== -->
      <section v-if="activeTab === 'overview'">
        <div class="stats-grid">
          <div class="stat-card" v-for="s in statCards" :key="s.label">
            <div class="stat-icon" :style="{ background: s.color }">
              <el-icon :size="26"><component :is="s.icon" /></el-icon>
            </div>
            <div class="stat-body">
              <div class="stat-value">{{ stats[s.key] ?? '—' }}</div>
              <div class="stat-label">{{ s.label }}</div>
            </div>
          </div>
        </div>
        <div class="tips-card">
          <el-icon><InfoFilled /></el-icon>
          <span>快速入口：左侧选择「患者管理」或「诊断记录」进行查看与操作。</span>
        </div>
      </section>

      <!-- ===== 患者管理 ===== -->
      <section v-if="activeTab === 'patients'">
        <div class="toolbar">
          <el-input
            v-model="patientKeyword"
            placeholder="搜索姓名 / 身份证号"
            clearable
            style="width:280px"
            @clear="loadPatients(1)"
            @keyup.enter="loadPatients(1)"
          >
            <template #append>
              <el-button :icon="Search" @click="loadPatients(1)" />
            </template>
          </el-input>
          <span class="total-tip">共 {{ patientTotal }} 条记录</span>
        </div>

        <el-table :data="patients" v-loading="patientLoading"
          class="data-table" stripe row-key="id">
          <el-table-column prop="id"       label="ID"     width="80" />
          <el-table-column prop="name"     label="姓名"   width="100" />
          <el-table-column prop="gender"   label="性别"   width="70" />
          <el-table-column prop="birthday" label="出生日期" width="130" />
          <el-table-column prop="idCard"   label="身份证号" min-width="180" />
          <el-table-column prop="address"  label="地址"   min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-popconfirm
                title="将同时删除该患者所有诊断记录，确认？"
                confirm-button-type="danger"
                @confirm="confirmDeletePatient(row.id)"
              >
                <template #reference>
                  <el-button type="danger" size="small" link>删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrap">
          <el-pagination v-model:current-page="patientPage" :page-size="10"
            :total="patientTotal" layout="prev, pager, next, total"
            @current-change="loadPatients" background />
        </div>
      </section>

      <!-- ===== 诊断记录 ===== -->
      <section v-if="activeTab === 'diagnoses'">
        <div class="toolbar">
          <span class="total-tip">共 {{ diagnosisTotal }} 条诊断记录</span>
        </div>

        <el-table :data="diagnoses" v-loading="diagnosisLoading"
          class="data-table" stripe row-key="id">
          <el-table-column prop="id"            label="记录ID"  width="90" />
          <el-table-column prop="patientName"   label="患者姓名" width="110" />
          <el-table-column prop="patientIdCard" label="身份证号" min-width="170" show-overflow-tooltip />
          <el-table-column label="诊断时间" width="180">
            <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
          </el-table-column>
          <el-table-column label="四诊完成情况" min-width="200">
            <template #default="{ row }">
              <el-tag :type="row.wangResult          ? 'success' : 'info'" size="small" class="mx-1">望</el-tag>
              <el-tag :type="row.wenConclusion        ? 'success' : 'info'" size="small" class="mx-1">问</el-tag>
              <el-tag :type="row.wenAudioConclusion   ? 'success' : 'info'" size="small" class="mx-1">闻</el-tag>
              <el-tag :type="row.qieHeartRate         ? 'success' : 'info'" size="small" class="mx-1">切</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="openDetail(row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrap">
          <el-pagination v-model:current-page="diagnosisPage" :page-size="10"
            :total="diagnosisTotal" layout="prev, pager, next, total"
            @current-change="loadDiagnoses" background />
        </div>
      </section>
    </main>

    <!-- 详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="诊断记录详情" size="480px" direction="rtl">
      <template v-if="selectedRecord">
        <div class="detail-section">
          <div class="detail-header">基本信息</div>
          <div class="detail-row"><span>患者姓名</span><b>{{ selectedRecord.patientName }}</b></div>
          <div class="detail-row"><span>身份证号</span><b>{{ selectedRecord.patientIdCard }}</b></div>
          <div class="detail-row"><span>诊断时间</span><b>{{ formatTime(selectedRecord.createTime) }}</b></div>
        </div>
        <div class="detail-section" v-if="selectedRecord.wangResult">
          <div class="detail-header">👁️ 望诊结果</div>
          <div class="detail-content">{{ selectedRecord.wangResult }}</div>
        </div>
        <div class="detail-section" v-if="selectedRecord.wenConclusion">
          <div class="detail-header">📋 问诊结论</div>
          <div class="detail-content">{{ selectedRecord.wenConclusion }}</div>
        </div>
        <div class="detail-section" v-if="selectedRecord.wenAudioConclusion">
          <div class="detail-header">🔊 闻诊结论</div>
          <div class="detail-content">{{ selectedRecord.wenAudioConclusion }}</div>
        </div>
        <div class="detail-section" v-if="selectedRecord.qieHeartRate">
          <div class="detail-header">💓 切诊数据</div>
          <div class="detail-row"><span>心率</span><b>{{ selectedRecord.qieHeartRate }} bpm</b></div>
          <div class="detail-row"><span>血氧</span><b>{{ selectedRecord.qieSpo2 }} %</b></div>
          <div class="detail-row"><span>有效率</span><b>{{ selectedRecord.qieValidRate }}</b></div>
          <div class="detail-row"><span>采样数</span><b>{{ selectedRecord.qieSampleCount }}</b></div>
          <div class="detail-content mt-2" v-if="selectedRecord.qieTcmSuggestion">
            {{ selectedRecord.qieTcmSuggestion }}
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, User, Document, Search,
  InfoFilled, Avatar, SwitchButton
} from '@element-plus/icons-vue'
import { getStats, getPatients, deletePatient, getDiagnoses } from '@/api/admin'

const router = useRouter()
const adminUsername = localStorage.getItem('admin_username') || 'admin'

const activeTab = ref('overview')
const navItems = [
  { key: 'overview',  label: '数据概览', icon: markRaw(DataAnalysis) },
  { key: 'patients',  label: '患者管理', icon: markRaw(User) },
  { key: 'diagnoses', label: '诊断记录', icon: markRaw(Document) },
]
const currentTitle = computed(() => navItems.find(n => n.key === activeTab.value)?.label || '')
const todayStr = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

// 统计
const stats = ref({})
const statCards = [
  { key: 'totalPatients',  label: '患者总数',    icon: markRaw(User),         color: 'linear-gradient(135deg,#8b3d1a,#c04a20)' },
  { key: 'totalDiagnoses', label: '诊断记录总数', icon: markRaw(Document),     color: 'linear-gradient(135deg,#6b4c24,#9a7040)' },
  { key: 'todayDiagnoses', label: '今日诊断数',   icon: markRaw(DataAnalysis), color: 'linear-gradient(135deg,#4a7060,#2d5a4a)' },
]
const loadStats = async () => {
  try {
    const res = await getStats()
    if (res.data.code === 200) stats.value = res.data.data
  } catch { /* 静默 */ }
}

// 患者
const patients = ref([])
const patientTotal = ref(0)
const patientPage = ref(1)
const patientKeyword = ref('')
const patientLoading = ref(false)
const loadPatients = async (page = patientPage.value) => {
  patientLoading.value = true
  patientPage.value = page
  try {
    const res = await getPatients(page, 10, patientKeyword.value)
    if (res.data.code === 200) {
      patients.value = res.data.data.list
      patientTotal.value = res.data.data.total
    }
  } finally { patientLoading.value = false }
}
const confirmDeletePatient = async (id) => {
  try {
    const res = await deletePatient(id)
    if (res.data.code === 200) { ElMessage.success('已删除'); loadPatients(1); loadStats() }
  } catch { ElMessage.error('删除失败') }
}

// 诊断
const diagnoses = ref([])
const diagnosisTotal = ref(0)
const diagnosisPage = ref(1)
const diagnosisLoading = ref(false)
const loadDiagnoses = async (page = diagnosisPage.value) => {
  diagnosisLoading.value = true
  diagnosisPage.value = page
  try {
    const res = await getDiagnoses(page, 10)
    if (res.data.code === 200) {
      diagnoses.value = res.data.data.list
      diagnosisTotal.value = res.data.data.total
    }
  } finally { diagnosisLoading.value = false }
}

// 详情
const drawerVisible = ref(false)
const selectedRecord = ref(null)
const openDetail = (row) => { selectedRecord.value = row; drawerVisible.value = true }

const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '—'

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_username')
  router.push('/admin/login')
}

onMounted(() => { loadStats(); loadPatients(1); loadDiagnoses(1) })
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
  overflow: hidden;
}

/* ===== 侧边栏 ===== */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #5c2a10 0%, #3d1a08 100%);
  border-right: 2px solid #a06828;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 3px 0 16px rgba(60,20,0,.25);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(200,160,32,.2);
}

.brand-char {
  width: 42px; height: 42px;
  border-radius: 10px;
  background: linear-gradient(135deg, #8b3d1a, #c04a20);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; color: #fdeabb;
  font-family: 'Noto Serif SC', "KaiTi", serif;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(139,61,26,.4);
}

.brand-name { color: #fdeabb; font-size: 14px; font-weight: 700; }
.brand-sub  { color: rgba(253,234,187,.45); font-size: 11px; margin-top: 2px; letter-spacing: 1px; }

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex; flex-direction: column; gap: 4px;
}

.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px; border-radius: 8px;
  color: rgba(253,234,187,.55);
  font-size: 14px; cursor: pointer; transition: all .2s;
}
.nav-item:hover {
  background: rgba(200,160,32,.12);
  color: rgba(253,234,187,.9);
}
.nav-item.active {
  background: linear-gradient(135deg, rgba(139,61,26,.5), rgba(192,74,32,.35));
  color: #fdeabb;
  box-shadow: inset 3px 0 0 #c8a020;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(200,160,32,.15);
  display: flex; align-items: center; justify-content: space-between;
}
.admin-user {
  display: flex; align-items: center; gap: 8px;
  color: rgba(253,234,187,.5); font-size: 13px;
}
.logout-btn { color: rgba(253,234,187,.4) !important; font-size: 12px; }
.logout-btn:hover { color: #f5a080 !important; }

/* ===== 主内容 ===== */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
}

.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8d5a0;
}
.page-title { font-size: 20px; font-weight: 700; color: #3d2b10; margin: 0; }
.date-tag   { font-size: 13px; color: #9a7040; }

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px; margin-bottom: 20px;
}
.stat-card {
  background: rgba(255,252,242,.92);
  border: 1px solid #d4b483;
  border-radius: 10px; padding: 22px;
  display: flex; align-items: center; gap: 18px;
  box-shadow: 0 3px 10px rgba(100,60,10,.08);
}
.stat-icon {
  width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0,0,0,.15);
}
.stat-value { font-size: 28px; font-weight: 700; color: #3d2b10; line-height: 1; }
.stat-label { font-size: 12px; color: #8b6030; margin-top: 6px; }

.tips-card {
  display: flex; align-items: center; gap: 10px;
  background: #faf3e0; border: 1px solid #e8d5a0;
  border-radius: 8px; padding: 14px 18px;
  color: #6b4c24; font-size: 13px;
}

/* ===== 工具栏 ===== */
.toolbar {
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 14px;
}
.total-tip { font-size: 13px; color: #8b6030; }

/* ===== 表格 ===== */
.data-table {
  border-radius: 8px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(100,60,10,.08);
}
.data-table :deep(.el-table__header-wrapper th) {
  background: linear-gradient(180deg, #efe0b8 0%, #e4cea0 100%);
  color: #5a2d00; font-weight: 700; font-size: 13px;
}
.data-table :deep(.el-table__row:hover > td) {
  background: #fef5dc !important;
}
.data-table :deep(.el-table__row.el-table__row--striped td) {
  background: #fdf8ed;
}

.mx-1 { margin: 0 3px; }

.pagination-wrap {
  display: flex; justify-content: flex-end;
  margin-top: 14px;
}
.pagination-wrap :deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background: #8b3d1a;
}

/* ===== 详情抽屉 ===== */
.detail-section {
  margin-bottom: 16px;
  background: #faf3e0;
  border: 1px solid #e8d5a0;
  border-radius: 8px;
  padding: 14px 16px;
}
.detail-header {
  font-weight: 700; font-size: 13px; color: #5a2d00;
  margin-bottom: 10px; padding-bottom: 8px;
  border-bottom: 1px solid #e8d5a0;
}
.detail-row {
  display: flex; justify-content: space-between;
  font-size: 13px; padding: 5px 0;
  border-bottom: 1px dashed #eedcb0;
  color: #6b4c24;
}
.detail-row:last-child { border-bottom: none; }
.detail-row b { color: #3d2b10; font-weight: 600; }
.detail-content { font-size: 13px; color: #3d2b10; line-height: 1.7; }
.mt-2 { margin-top: 10px; padding-top: 10px; border-top: 1px dashed #e8d5a0; }
</style>