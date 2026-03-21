<template>
  <div class="detect-container">
    <div class="animated-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>

    <div class="noise-overlay"></div>

    <div class="content-wrapper">
      <header class="header-section">
        <div class="badge">AI-POWERED TCM</div>
        <h1 class="main-title">四诊合参 <span class="highlight">·</span> 智慧诊断</h1>
        <p class="sub-title">融合传统医学智慧与现代人工智能技术</p>
        <div class="decorative-line"><span class="dot"></span></div>
      </header>

      <div class="card-grid">
        <div class="detect-card wang" :class="{ 'is-finished': wangFinished }" @click="goTo('wang')">
          <div class="glass-inner">
            <div v-if="wangFinished" class="done-tag"><el-icon><CircleCheckFilled /></el-icon> 已完成</div>
            <div class="icon-wrapper"><span class="chinese-char">望</span></div>
            <h3>望诊分析</h3>
            <p>基于计算机视觉提取舌质、舌苔及面部色泽特征。</p>
            <div class="card-footer">
              <span class="action-text">{{ wangFinished ? '结果已锁定' : '开始采集' }}</span>
              <el-icon class="arrow-icon"><Right /></el-icon>
            </div>
          </div>
        </div>

        <div class="detect-card wen" :class="{ 'is-finished': wenFinished }" @click="goTo('wen')">
          <div class="glass-inner">
            <div v-if="wenFinished" class="done-tag"><el-icon><CircleCheckFilled /></el-icon> 已完成</div>
            <div class="icon-wrapper"><span class="chinese-char">闻</span></div>
            <h3>闻诊分析</h3>
            <p>通过声纹识别技术分析呼吸声与语音，辨析脏腑虚实。</p>
            <div class="card-footer">
              <span class="action-text">{{ wenFinished ? '结果已锁定' : '音频录制' }}</span>
              <el-icon class="arrow-icon"><Right /></el-icon>
            </div>
          </div>
        </div>

        <div class="detect-card wenjuan" :class="{ 'is-finished': wenjuanFinished }" @click="goTo('wenjuan')">
          <div class="glass-inner">
            <div v-if="wenjuanFinished" class="done-tag"><el-icon><CircleCheckFilled /></el-icon> 已完成</div>
            
            <div class="icon-wrapper"><span class="chinese-char">问</span></div>
            <h3>问诊分析</h3>
            <p>系统化交互问卷，深度梳理自觉症状与生活习惯。</p>
            <div class="card-footer">
              <span class="action-text">{{ wenjuanFinished ? '结果已锁定' : '填写问卷' }}</span>
              <el-icon class="arrow-icon"><Right /></el-icon>
            </div>
          </div>
        </div>

        <div class="detect-card qie" :class="{ 'is-finished': qieFinished }" @click="goTo('qie')">
          <div class="glass-inner">
            <div v-if="qieFinished" class="done-tag"><el-icon><CircleCheckFilled /></el-icon> 已完成</div>
            <div class="icon-wrapper"><span class="chinese-char">切</span></div>
            <h3>切诊分析</h3>
            <p>数字化脉波采集，实时呈现指下脉象的位、数、形、势。</p>
            <div class="card-footer">
              <span class="action-text">{{ qieFinished ? '结果已锁定' : '连接设备' }}</span>
              <el-icon class="arrow-icon"><Right /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="report-section">
         <!-- 显示已完成的板块 -->
         <div v-if="completedCount > 0" class="completed-info">
           <p class="completion-status">已完成 <span class="count-badge">{{ completedCount }}/4</span> 个诊断板块</p>
           <div class="completed-types">
             <el-tag v-if="wangFinished" type="success" effect="light">✓ 望诊</el-tag>
             <el-tag v-if="wenFinished" type="success" effect="light">✓ 闻诊</el-tag>
             <el-tag v-if="wenjuanFinished" type="success" effect="light">✓ 问诊</el-tag>
             <el-tag v-if="qieFinished" type="success" effect="light">✓ 切诊</el-tag>
           </div>
         </div>
         
         <!-- 生成报告按钮 -->
         <el-button 
           v-if="completedCount > 0"
           type="primary" 
           size="large" 
           round 
           class="report-btn"
           @click="generateReport"
           :loading="isGenerating"
         >
           {{ completedCount === 4 ? '生成四诊合参报告' : `生成报告 (${completedCount}个板块)` }}
         </el-button>
         
         <p v-if="completedCount === 0" class="no-data-tip">
           请完成至少一个诊断板块后生成报告
         </p>
      </div>
    </div>
  </div>
</template>

// ...existing code...
<script setup>
import { useRouter, useRoute } from 'vue-router'
import { Right, CircleCheckFilled } from '@element-plus/icons-vue'
import { ref, onMounted, onActivated, watch } from 'vue';
import { ElMessage } from 'element-plus'; // 显式引入

const router = useRouter()
const route = useRoute()

// 1. 核心变量：用来锁定“当前这一场”检测的病人 ID
const lockedPatientId = ref(null);
const lockedIdCard = ref('');

// 状态控制
const wenjuanFinished = ref(false);
const wangFinished = ref(false);
const wenFinished = ref(false);
const qieFinished = ref(false);
const isGenerating = ref(false)  // 【新增】生成报告中的状态

// 新增：计算已完成的诊断板块数
const completedCount = ref(0);

const calculateCompletedCount = () => {
  let count = 0;
  if (wangFinished.value) count++;
  if (wenFinished.value) count++;
  if (wenjuanFinished.value) count++;
  if (qieFinished.value) count++;
  completedCount.value = count;
};

const refreshStatuses = () => {
  // 始终以锁定在当前页面内存中的 ID 为准，不直接读 localStorage，防止中途被覆盖
  const currentId = lockedPatientId.value || localStorage.getItem('current_patient_id');
  
  if (!currentId) return;
  
  // 更新内存中的锁定 ID
  if (!lockedPatientId.value) {
    lockedPatientId.value = currentId;
    lockedIdCard.value = localStorage.getItem('current_patient_idCard') || '';
  }

  // 状态比对：只有当“已完成 ID”等于“当前锁定 ID”时，才显示完成
  wangFinished.value = localStorage.getItem('wang_finished_id') === String(currentId);
  wenFinished.value = localStorage.getItem('wen_finished_id') === String(currentId);
  wenjuanFinished.value = localStorage.getItem('wenjuan_finished_id') === String(currentId);
  qieFinished.value = localStorage.getItem('qie_finished_id') === String(currentId);  
  // 新增：计算完成数
  calculateCompletedCount();}

const goTo = (type) => {
  const statusMap = {
    wang: wangFinished.value,
    wen: wenFinished.value,
    wenjuan: wenjuanFinished.value,
    qie: qieFinished.value
  };

  if (statusMap[type]) {
    ElMessage.info('该检测项目已完成，结果已锁定');
    return;
  }

  // --- 【改动重点：使用内存锁定的 ID 传参】 ---
  // 不再临时从 localStorage 拿，防止拿到了刚登陆的下一个人的 ID
  router.push({
    path: `/detect/${type}`,
    query: { 
      id: lockedPatientId.value, 
      idCard: lockedIdCard.value 
    }
  });
}

onMounted(() => {
  refreshStatuses();
});

onActivated(() => {
  // 每次切回来，检查一下 ID 是否变了（如果是新病人进来了）
  const latestId = localStorage.getItem('current_patient_id');
  if (latestId !== lockedPatientId.value) {
    lockedPatientId.value = latestId;
    lockedIdCard.value = localStorage.getItem('current_patient_idCard');
  }
  refreshStatuses();
});

watch(() => route.fullPath, () => {
  refreshStatuses();
});

// ===== 生成四诊报告【已改造：支持部分板块】=====
const generateReport = async () => {
  // 【重要】直接从 localStorage 获取最新的患者ID，确保不为空
  const patientId = lockedPatientId.value || localStorage.getItem('current_patient_id')
  const idCard = lockedIdCard.value || localStorage.getItem('current_patient_idCard')
  
  console.log('[DEBUG] 准备生成报告，患者ID:', patientId, '身份证:', idCard)
  
  if (!patientId) {
    ElMessage.error('缺少病人ID，请重新登录')
    return
  }

  // 获取已完成的诊断类型
  const completedTypes = [];
  if (wangFinished.value) completedTypes.push('wang');
  if (wenFinished.value) completedTypes.push('wen_audio');
  if (wenjuanFinished.value) completedTypes.push('wen_questionnaire');
  if (qieFinished.value) completedTypes.push('qie');

  // 跳转到报告页面，传递已完成的诊断类型
  router.push({
    path: '/report',
    query: { 
      id: patientId,
      completedTypes: completedTypes.join(',')
    }
  })
}
</script>
// ...existing code...

<style scoped>
/* 保持你原有的 detect-container, animated-bg, orb, noise-overlay 等样式不变 */
.detect-container {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding: 40px 20px;
}

.animated-bg { position: absolute; width: 100%; height: 100%; z-index: 0; }
.orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; animation: float 20s infinite alternate; }
.orb-1 { width: 600px; height: 600px; background: #409eff; top: -200px; right: -100px; }
.orb-2 { width: 500px; height: 500px; background: #67c23a; bottom: -150px; left: -100px; animation-delay: -5s; }
.orb-3 { width: 300px; height: 300px; background: #e6a23c; top: 40%; left: 30%; opacity: 0.2; }

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(50px, 100px) scale(1.1); }
}

.content-wrapper { position: relative; z-index: 10; max-width: 1300px; width: 100%; }

.header-section { text-align: center; margin-bottom: 60px; }
.main-title { font-size: 3.2rem; color: #1a1a1a; font-family: "Source Han Serif CN", serif; font-weight: 900; }
.highlight { color: #409eff; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

/* 基础卡片样式 */
.detect-card {
  position: relative;
  height: 400px;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.glass-inner { padding: 40px; height: 100%; display: flex; flex-direction: column; backdrop-filter: blur(15px); }

/* 已完成状态样式 (重点) */
.detect-card.is-finished {
  cursor: not-allowed;
  filter: grayscale(0.8);
  opacity: 0.8;
  pointer-events: none; /* 彻底禁止所有鼠标事件 */
}

.done-tag {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #67c23a;
  color: white;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.icon-wrapper { width: 70px; height: 70px; border-radius: 20px; display: flex; justify-content: center; align-items: center; margin-bottom: 40px; }
.chinese-char { font-size: 32px; color: #fff; font-family: "Kaiti", serif; }

.wang .icon-wrapper { background: linear-gradient(135deg, #409eff, #73b9ff); }
.wen .icon-wrapper { background: linear-gradient(135deg, #67c23a, #95d475); }
.wenjuan .icon-wrapper { background: linear-gradient(135deg, #e6a23c, #f3d19e); }
.qie .icon-wrapper { background: linear-gradient(135deg, #f56c6c, #fab6b6); }

.report-section { 
  text-align: center; 
  margin-top: 50px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 新增：已完成信息样式 */
.completed-info {
  margin-bottom: 20px;
}

.completion-status {
  font-size: 16px;
  color: #333;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.count-badge {
  display: inline-block;
  background: linear-gradient(135deg, #409eff, #73b9ff);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  margin-left: 8px;
}

.completed-types {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 0;
  flex-wrap: wrap;
}

.no-data-tip {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.report-btn { 
  padding: 25px 50px; 
  font-size: 18px; 
  box-shadow: 0 10px 20px rgba(64, 158, 255, 0.3); 
}

/* Hover 交互特效 */
.detect-card:not(.is-finished):hover {
  transform: translateY(-15px);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 30px 60px rgba(0,0,0,0.1);
}
</style>