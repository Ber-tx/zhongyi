<template>
  <div class="tcm-system">
    <audio ref="audioRef" loop>
      <source src="../assets/audio/bgm/梁祝.mp3" type="audio/mpeg" />
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
              <div class="dropdown-item" @click="openReportSettings">📄 报告设置</div>
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

    <!-- ===== 报告设置对话框 ===== -->
    <el-dialog
      v-model="settingsVisible"
      title="报告设置"
      width="560px"
      :close-on-click-modal="false"
      class="settings-dialog"
    >
      <div class="settings-body">
        <div class="settings-tip">
          以下信息将显示在每份四诊报告的抬头处，设置后保存在本机，随时可修改。
        </div>

        <div class="settings-section">机构信息</div>
        <el-form :model="reportSettings" label-width="110px" class="settings-form">
          <el-form-item label="机构名称 *">
            <el-input v-model="reportSettings.orgName"
              placeholder="如：XX社区卫生服务中心" maxlength="40" show-word-limit />
          </el-form-item>
          <el-form-item label="机构地址">
            <el-input v-model="reportSettings.orgAddress"
              placeholder="选填，如：XX市XX区XX路1号" maxlength="60" />
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="reportSettings.orgPhone"
              placeholder="选填，如：0571-12345678" maxlength="20" />
          </el-form-item>
        </el-form>

        <div class="settings-section">报告信息</div>
        <el-form :model="reportSettings" label-width="110px" class="settings-form">
          <el-form-item label="签发医师">
            <el-input v-model="reportSettings.doctorName"
              placeholder="选填，报告底部签发人姓名" maxlength="20" />
          </el-form-item>
          <el-form-item label="有效期说明">
            <el-input v-model="reportSettings.validityNote"
              placeholder="选填，如：本报告自出具之日起3个月内有效" maxlength="50" />
          </el-form-item>
          <el-form-item label="免责声明">
            <el-input v-model="reportSettings.disclaimer" type="textarea" :rows="3"
              placeholder="选填，将替换报告底部默认免责说明" maxlength="120" show-word-limit />
          </el-form-item>
        </el-form>

        <div class="settings-section">AI提示词设置</div>
        <el-form :model="reportSettings" label-width="110px" class="settings-form">
          <el-form-item label="侧重点">
            <el-select v-model="reportSettings.llmFocusMode"
              placeholder="选择报告侧重点">
              <el-option label="不侧重（AI 详细分析）" value="" />
              <el-option label="望诊" value="wang" />
              <el-option label="闻诊" value="wen_audio" />
              <el-option label="问诊" value="wen_questionnaire" />
              <el-option label="切诊" value="qie" />
            </el-select>
          </el-form-item>
          <el-form-item label="自定义提示词">
            <el-input v-model="reportSettings.llmPromptTemplate" type="textarea" :rows="4"
              placeholder="选填，不填则使用系统默认提示词生成报告" maxlength="1000" show-word-limit />
          </el-form-item>
        </el-form>

        <div class="settings-section">预览效果</div>
        <div class="preview-box">
          <div class="preview-org">{{ reportSettings.orgName || '（机构名称）' }}</div>
          <div class="preview-sub">四诊合参体质辨识报告</div>
          <div class="preview-info" v-if="reportSettings.orgAddress || reportSettings.orgPhone">
            <span v-if="reportSettings.orgAddress">📍 {{ reportSettings.orgAddress }}</span>
            <span v-if="reportSettings.orgPhone">📞 {{ reportSettings.orgPhone }}</span>
          </div>
          <div class="preview-footer">
            <span v-if="reportSettings.doctorName">签发医师：{{ reportSettings.doctorName }}</span>
            <span v-if="reportSettings.validityNote">{{ reportSettings.validityNote }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="settingsVisible = false">取消</el-button>
        <el-button @click="resetSettings" style="margin-right:auto">恢复默认</el-button>
        <el-button class="btn-save-settings" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>
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


// ===== 报告设置 =====
const settingsVisible = ref(false)

const defaultSettings = {
  orgName:      '',
  orgAddress:   '',
  orgPhone:     '',
  doctorName:   '',
  validityNote: '',
  disclaimer:   '',
  llmPromptTemplate: '',
  llmFocusMode: '',
}

const loadSettings = () => {
  try {
    const saved = localStorage.getItem('report_settings')
    return saved ? { ...defaultSettings, ...JSON.parse(saved) } : { ...defaultSettings }
  } catch { return { ...defaultSettings } }
}

const reportSettings = ref(loadSettings())

const openReportSettings = () => {
  showMore.value = false
  reportSettings.value = loadSettings()
  settingsVisible.value = true
}

const saveSettings = () => {
  if (!reportSettings.value.orgName.trim()) {
    ElMessage.warning('机构名称为必填项')
    return
  }
  localStorage.setItem('report_settings', JSON.stringify(reportSettings.value))
  ElMessage.success('报告设置已保存')
  settingsVisible.value = false
}

const resetSettings = () => {
  reportSettings.value = { ...defaultSettings }
  localStorage.removeItem('report_settings')
  ElMessage.info('已恢复默认设置')
}

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

/* ===== 报告设置对话框 ===== */
.settings-dialog :deep(.el-dialog__header) {
  background: linear-gradient(180deg, #f5e4a8, #ebd07a);
  border-bottom: 1px solid #c8a96e;
  padding: 16px 24px;
}
.settings-dialog :deep(.el-dialog__title) {
  font-size: 16px; font-weight: 700; color: #5a2d00;
  font-family: 'Noto Serif SC', serif;
}
.settings-dialog :deep(.el-dialog__body) {
  padding: 0; background: #fdf8ef;
}
.settings-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid #e8d5a0; background: #faf3e0; padding: 12px 24px;
}

.settings-body { padding: 20px 24px; }

.settings-tip {
  font-size: 12px; color: #8b6030; line-height: 1.6;
  background: #faf3e0; border: 1px solid #e8d5a0;
  border-radius: 6px; padding: 10px 14px; margin-bottom: 18px;
}

.settings-section {
  font-size: 12px; font-weight: 700; color: #5a2d00;
  letter-spacing: 2px; margin: 16px 0 10px;
  padding-bottom: 6px; border-bottom: 1px solid #e8d5a0;
}
.settings-section::before { content: '◈ '; color: #c8a020; }

.settings-form :deep(.el-form-item__label) {
  font-size: 13px; color: #6b4c24; font-weight: 600;
}
.settings-form :deep(.el-input__wrapper) {
  background: #fffdf5 !important; box-shadow: 0 0 0 1px #d4b483 !important;
  border-radius: 4px !important;
}
.settings-form :deep(.el-input__wrapper:hover),
.settings-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #8b3d1a !important;
}
.settings-form :deep(.el-textarea__inner) {
  background: #fffdf5 !important; box-shadow: 0 0 0 1px #d4b483 !important;
}

/* 预览框 */
.preview-box {
  background: #fff; border: 1px solid #c8a96e;
  border-radius: 8px; padding: 18px 20px;
  text-align: center;
}
.preview-org {
  font-size: 18px; font-weight: 700; color: #3d2b10;
  font-family: 'Noto Serif SC', serif; letter-spacing: 2px;
  margin-bottom: 4px;
}
.preview-sub {
  font-size: 13px; color: #8b6030; margin-bottom: 8px; letter-spacing: 1px;
}
.preview-info {
  display: flex; justify-content: center; gap: 20px;
  font-size: 12px; color: #9a7040; margin-bottom: 8px;
}
.preview-footer {
  display: flex; justify-content: space-between;
  font-size: 11px; color: #b09060;
  border-top: 1px dashed #e8d5a0; padding-top: 8px; margin-top: 8px;
}

.btn-save-settings {
  background: linear-gradient(135deg, #8b3d1a, #c04a20) !important;
  color: #fdeabb !important; border: none !important;
  font-weight: 700 !important; border-radius: 4px !important;
}

</style>