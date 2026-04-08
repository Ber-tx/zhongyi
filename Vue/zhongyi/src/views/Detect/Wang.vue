<template>
  <div class="wang-container">
    <div class="animated-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <div class="content-box" :class="{ 'result-fullscreen': isCompleted }">
      <div class="header">
        <el-button icon="ArrowLeft" circle @click="goBack" class="back-btn" />
        <h2 class="title">舌象采集分析</h2>
        <div class="step-indicator">AI-POWERED DIAGNOSIS</div>
      </div>

      <div v-if="!isCompleted" class="main-body">
        <div v-if="!loading" class="camera-module">
          
          <div class="video-wrapper">
            <video v-show="isCameraOpen" ref="videoPlayer" autoplay playsinline class="live-video"></video>
            
            <img v-if="localImageUrl && !isCameraOpen" :src="localImageUrl" class="static-preview" />
            
            <div v-if="!isCameraOpen && !localImageUrl" class="placeholder-view">
              <el-icon :size="50" color="#dcdfe6"><Picture /></el-icon>
              <p>请开启摄像头或上传舌象照片</p>
            </div>

            <div v-if="isCameraOpen || localImageUrl" class="scan-overlay">
              <div class="tongue-guide"></div>
              <div class="scan-line"></div>
            </div>
          </div>

          <div class="controls">
            <div v-if="isCameraOpen" class="shutter-group">
              <el-button type="primary" size="large" circle icon="Camera" @click="takePhoto" class="shutter-btn" />
              <p class="hint">点击圆圈拍照</p>
              <el-button type="info" link @click="stopCamera">取消拍照</el-button>
            </div>

            <div v-else class="action-group">
              <el-button type="success" size="large" round @click="startCamera" icon="VideoCamera">
                开启摄像头拍照
              </el-button>
              
              <div class="file-divider"><span>OR</span></div>
              
              <input type="file" id="fileInput" accept="image/*" @change="onFileChange" hidden />
              <el-button type="primary" size="large" plain round @click="triggerFileInput" icon="Picture">
                从相册选择图片
              </el-button>
            </div>
          </div>
        </div>

        <div v-else class="loading-state">
          <div class="ai-spinner"></div>
          <h3>AI 引擎分析中...</h3>
          <p>正在计算舌苔、舌质及色彩分量</p>
        </div>
      </div>

      <div v-else class="result-module">
        <div class="dashboard-header">
          <div class="status-badge"><el-icon><CircleCheckFilled /></el-icon> 诊断分析完成</div>
          <el-tag type="danger" effect="dark" round class="confidence-tag">
            模型置信度 {{ confidencePercent }}%
          </el-tag>
        </div>

        <!-- 核心区域：模型分析雷达图与各项分值（突出第一） -->
        <div class="visual-dashboard">
          <div class="dashboard-title">
            <h3>核心模型量化指标</h3>
            <span class="subtitle">AI 多维特征提取分析</span>
          </div>
          
          <div class="radar-box">
            <el-image 
              :src="analysisResult.chart_img" 
              :preview-src-list="[analysisResult.chart_img]"
              fit="contain"
              class="radar-img"
              preview-teleported
              :hide-on-click-modal="true"
            />
          </div>

          <div class="score-grid" v-if="scoreSummary.length">
            <div class="score-item" v-for="item in scoreSummary" :key="item.name">
              <div class="score-row">
                <span class="k">{{ item.name }}</span>
                <span class="v">{{ item.mean }}</span>
              </div>
              <el-progress :percentage="item.mean" :stroke-width="8" :show-text="false" color="#8b3d1a" />
            </div>
          </div>
        </div>

        <!-- 次要区域：结论和原始图像紧凑排版 -->
        <div class="summary-card">
          <div class="thumb-container">
            <img :src="localImageUrl" class="thumb-img" />
            <span class="thumb-label">采集原图</span>
          </div>
          <div class="conclusion-text">
            <span class="label">初步辨证结论</span>
            <p class="value">{{ analysisResult.main_result }}</p>
          </div>
        </div>

        <div class="result-insight-card" v-if="resultInsights.length">
          <div class="result-insight-head">
            <h3>模型解读要点</h3>
            <span>基于雷达图与结构化输出补充</span>
          </div>
          <ul class="result-insight-list">
            <li v-for="(item, idx) in resultInsights" :key="idx">{{ item }}</li>
          </ul>
        </div>
        
        <p class="ai-disclaimer">
          本分析由 <span class="highlight">AI 引擎</span> 提供，仅供健康参考，<br />
          <span class="warning">不作为临床诊断依据</span>。确诊请咨询 <span class="highlight">专业医师</span>。
        </p>

        <el-collapse style="margin-top: 16px;">
          <el-collapse-item title="📖 参考文献与出处" name="1">
            <div class="ref-list">
              <div v-for="(ref, idx) in wangReferences" :key="idx" class="ref-item">
                <span class="ref-authors">{{ ref.authors }} ({{ ref.year }})</span>
                <p class="ref-desc">{{ ref.title }}</p>
                <a v-if="ref.url" :href="ref.url" target="_blank" class="ref-link">
                  查看 → {{ ref.source }}
                </a>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
        
        <div class="footer-btns">
          <el-button round @click="reCapture">重新分析</el-button>
          <el-button type="primary" round @click="goToNextOrReport">
            继续下一个诊断
          </el-button>
          <el-button type="success" round @click="generatePartialReport">
            生成报告
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Camera, ArrowLeft, CircleCheckFilled, Picture, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus';
import { navigateToDiagnosisReport } from '@/utils/reportUtils';
import { uploadTongue } from '@/api/detect';
import { algorithmReferences } from '@/constants/algorithmReferences'

const router = useRouter()
const route = useRoute()

const videoPlayer = ref(null)
const isCameraOpen = ref(false)
const isCompleted = ref(false)
const loading = ref(false)
const mediaStream = ref(null)
const localImageUrl = ref('')
const analysisResult = ref(null)
const wangReferences = ref(algorithmReferences.wang.references)

const scoreSummary = computed(() => {
  const raw = analysisResult.value?.scores || {}
  return Object.entries(raw)
    .map(([name, value]) => {
      const mean = typeof value === 'object' ? Number(value?.mean ?? 0) : Number(value ?? 0)
      return {
        name,
        mean: Number.isFinite(mean) ? Math.max(0, Math.min(100, Math.round(mean))) : 0
      }
    })
    .sort((a, b) => b.mean - a.mean)
})

const resultInsights = computed(() => {
  const items = scoreSummary.value
  if (!items.length) return []

  const insights = []
  const topItems = items.slice(0, 2).map((item) => `${item.name} ${item.mean} 分`)
  const tail = items[items.length - 1]

  if (topItems.length) {
    insights.push(`模型重点关注：${topItems.join('、')}`)
  }
  if (tail) {
    insights.push(`相对较低指标：${tail.name} ${tail.mean} 分`)
  }

  const details = analysisResult.value?.details
  if (Array.isArray(details) && details.length) {
    insights.push(...details.slice(0, 3).map((item) => String(item)))
  } else if (details && typeof details === 'object') {
    insights.push(...Object.entries(details).slice(0, 3).map(([key, value]) => {
      if (Array.isArray(value)) return `${key}：${value.join('，')}`
      if (value && typeof value === 'object') return `${key}：${JSON.stringify(value)}`
      return `${key}：${String(value)}`
    }))
  }

  insights.push(`模型置信度：${confidencePercent.value}%`)
  return insights.filter(Boolean)
})

const confidencePercent = computed(() => {
  const confidenceSource = Number(analysisResult.value?.confidence)
  if (Number.isFinite(confidenceSource) && confidenceSource > 0) {
    return Math.max(0, Math.min(100, Math.round(confidenceSource * 100)))
  }

  const altSource = Number(analysisResult.value?.confidencePercent ?? analysisResult.value?.confidence_percent)
  if (Number.isFinite(altSource) && altSource > 0) {
    return Math.max(0, Math.min(100, altSource <= 1 ? Math.round(altSource * 100) : Math.round(altSource)))
  }

  if (scoreSummary.value.length) {
    const avg = scoreSummary.value.reduce((sum, item) => sum + item.mean, 0) / scoreSummary.value.length
    return Math.max(0, Math.min(100, Math.round(avg)))
  }

  return 0
})

const patientInfo = ref({
  id: null,
  idCard: ''
})

onMounted(() => {
  let qId = route.query.id;
  let qIdCard = route.query.idCard;

  if (!qId) qId = localStorage.getItem('current_patient_id');
  if (!qIdCard) qIdCard = localStorage.getItem('current_patient_idCard');

  patientInfo.value.id = qId;
  patientInfo.value.idCard = qIdCard;

  console.log("==== [DEBUG] 望诊页最终锁定的病人 ID:", patientInfo.value.id);
  
  localStorage.removeItem('wang_finished_id');
  
  startCamera();
});

const goBack = () => {
  stopCamera();
  if (!isCompleted.value) {
    localStorage.removeItem('wang_finished_id');
  }
  router.push('/detect');
}

const startCamera = async () => {
  localImageUrl.value = '';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 800, height: 600, facingMode: "user" } 
    });
    mediaStream.value = stream;
    if (videoPlayer.value) videoPlayer.value.srcObject = stream;
    isCameraOpen.value = true;
  } catch (err) {
    ElMessage.error("无法调用摄像头。请确认已开启权限并处于 HTTPS 或 localhost 环境。");
  }
}

const takePhoto = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 600;
  canvas.height = 800;
  const ctx = canvas.getContext('2d');
  ctx.translate(canvas.width, 0); ctx.scale(-1, 1); 
  ctx.drawImage(videoPlayer.value, 0, 0, 600, 800);
  const base64 = canvas.toDataURL('image/jpeg', 0.6);
  localImageUrl.value = base64;
  stopCamera();
  uploadImage(base64);
}

const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop());
    mediaStream.value = null;
    isCameraOpen.value = false;
  }
}

const triggerFileInput = () => document.getElementById('fileInput').click();
const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      localImageUrl.value = event.target.result;
      uploadImage(event.target.result);
    };
    reader.readAsDataURL(file);
  }
}

const uploadImage = async (base64) => {
  const urlParams = new URLSearchParams(window.location.search);
  const pid = patientInfo.value.id || 
              urlParams.get('patientId') || 
              urlParams.get('id') || 
              localStorage.getItem('current_patient_id');

  const icard = patientInfo.value.idCard || 
                urlParams.get('idCard') || 
                localStorage.getItem('current_patient_idcard');
  const diagnosisId = route.query.caseId || localStorage.getItem('current_case_id');

  if (!pid) {
    ElMessage.error("未获取到当前病人ID，请确保已录入病人信息");
    return;
  }

  loading.value = true;
  try {
    const blob = await (await fetch(base64)).blob();
    const formData = new FormData();
    
    formData.append('file', blob, 'tongue.jpg');
    formData.append('id', pid); 
    if (icard) {
      formData.append('idCard', icard);
    }
    if (diagnosisId) {
      formData.append('diagnosisId', diagnosisId);
    }

    console.log("==== [DEBUG] 望诊提交，锁定病人 ID:", pid);

    const res = await uploadTongue(formData);
    
    if (res.data.code === 200 || res.data.success) {
      const resultData = res.data.data;
      const mainResult = resultData.main_result;

      if (mainResult.includes("未检测到") || mainResult.includes("不清晰") || mainResult.includes("过暗")) {
        ElMessageBox.alert(
          `识别质量不佳：${mainResult}。请确保舌头位于框内，再次尝试。`, 
          '分析提醒', 
          {
            confirmButtonText: '重新拍摄',
            type: 'warning',
            callback: () => { reCapture(); }
          }
        );
      } else {
        analysisResult.value = resultData;
        isCompleted.value = true;
        ElMessage.success("分析成功！");
      }
    } else {
      const backendMsg = (res?.data?.msg || '').toString().trim();
      throw new Error(backendMsg || "后端返回失败");
    }
  } catch (err) {
    console.error("上传错误:", err);
    const apiMsg = err?.response?.data?.msg;
    const finalMsg = (apiMsg || err?.message || "分析失败，请检查网络").toString().trim();
    ElMessage.error(finalMsg || "分析失败，请检查网络");
  } finally {
    loading.value = false;
  }
}

const reCapture = () => {
  isCompleted.value = false;
  localImageUrl.value = '';
  startCamera(); 
}

const goToNextOrReport = () => {
  stopCamera();
  const pid = patientInfo.value.id || localStorage.getItem('current_patient_id');
  if (isCompleted.value && pid) {
    localStorage.setItem('wang_finished_id', String(pid));
  }
  router.push('/detect');
}

const generatePartialReport = () => {
  const patientId = patientInfo.value.id || localStorage.getItem('current_patient_id');
  const idCard = patientInfo.value.idCard || localStorage.getItem('current_patient_idCard');
  if (isCompleted.value && patientId) {
    localStorage.setItem('wang_finished_id', String(patientId));
  }
  navigateToDiagnosisReport(router, patientId, idCard);
}

onUnmounted(stopCamera);
</script>

<style scoped>
.wang-container {
  min-height: 100vh;
  position: relative;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  display: flex; justify-content: center; align-items: center;
  overflow: hidden;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

.wang-container::before {
  content: ''; position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
}

.content-box {
  position: relative; z-index: 10;
  width: 92%;
  max-width: 560px;
  background: rgba(255, 252, 242, 0.92);
  backdrop-filter: blur(16px);
  border-radius: 12px;
  padding: 26px;
  border: 1px solid #c8a96e;
  box-shadow: 0 20px 50px rgba(100,60,10,.14),
              inset 0 1px 0 rgba(255,248,220,.8);
}

.content-box.result-fullscreen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  border-radius: 0;
  padding: 28px 36px 22px;
  overflow-y: auto;
}

.content-box.result-fullscreen::before {
  border-radius: 0;
}

.content-box::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, #c8a020 50%, transparent);
  border-radius: 12px 12px 0 0;
}

.header { text-align: center; margin-bottom: 20px; position: relative; }
.back-btn { position: absolute; left: 0; top: 5px; }
.title { font-size: 1.5rem; margin: 0; font-family: 'Noto Serif SC', "Source Han Serif CN", serif; color: #3d2b10; }

.video-wrapper {
  position: relative; width: 100%; aspect-ratio: 3/4;
  background: #2a1a0a; border-radius: 12px; overflow: hidden;
  border: 1px solid #c8a96e;
}
.live-video, .static-preview { width: 100%; height: 100%; object-fit: cover; }
.live-video { transform: scaleX(-1); }

.placeholder-view {
  height: 100%; display: flex; flex-direction: column;
  justify-content: center; align-items: center;
  color: #9a7040; background: #faf3e0;
}

.scan-overlay {
  position: absolute; inset: 0; pointer-events: none;
  display: flex; justify-content: center; align-items: center;
}
.tongue-guide {
  width: 160px; height: 240px;
  border: 2px dashed rgba(200,160,32,.7);
  border-radius: 50% 50% 45% 45%;
}
.scan-line {
  position: absolute; width: 100%; height: 3px;
  background: linear-gradient(to right, transparent, #c8a020, transparent);
  animation: scan 3s infinite linear;
}
@keyframes scan { 0% { top: 0; } 100% { top: 100%; } }

.controls { text-align: center; margin-top: 22px; }
.action-group { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.file-divider {
  margin: 10px 0; color: #c8a96e; font-size: 12px;
  display: flex; align-items: center; width: 100%;
}
.file-divider::before, .file-divider::after {
  content: ""; flex: 1; height: 1px; background: #e8d5a0; margin: 0 10px;
}

/* ========== 辨证模型分析排版 ========== */
.dashboard-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; padding: 0 5px;
}
.status-badge {
  display: flex; align-items: center; gap: 6px;
  color: #c8a020; font-weight: bold; font-size: 14px;
}
.confidence-tag {
  font-weight: bold; font-family: monospace;
}
.visual-dashboard {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid #e8d5a0; border-radius: 12px;
  padding: 24px 18px; margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(139, 61, 26, 0.05);
}
.dashboard-title h3 {
  margin: 0; font-size: 1.1rem; color: #5a2d00;
}
.dashboard-title .subtitle {
  font-size: 12px; color: #9a7040;
}
.radar-box {
  margin: 26px 0 22px; display: flex; justify-content: center;
}
.radar-img {
  width: 100% !important; max-height: 420px !important;
  filter: drop-shadow(0 4px 12px rgba(100,60,10,.1));
}
.score-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 15px;
}
.score-item {
  background: rgba(250, 243, 224, 0.5);
  padding: 10px; border-radius: 8px; border: 1px dashed #e8d5a0;
}
.score-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 6px; font-size: 13px; font-weight: bold; color: #5a2d00;
}
.summary-card {
  display: flex; gap: 15px; align-items: stretch;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid #e8d5a0; border-radius: 12px;
  padding: 18px; margin-bottom: 20px;
}
.thumb-container {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  width: 108px; flex-shrink: 0;
}
.thumb-img {
  width: 96px; height: 96px; object-fit: cover;
  border-radius: 6px; border: 2px solid #e8d5a0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.thumb-label {
  font-size: 12px; color: #8b3d1a; font-weight: bold;
}
.conclusion-text {
  flex: 1; display: flex; flex-direction: column; justify-content: center;
}
.conclusion-text .label {
  font-size: 13px; color: #9a7040; margin-bottom: 6px;
}
.conclusion-text .value {
  margin: 0; font-size: 16px; color: #3d2b10; font-weight: 600; line-height: 1.65;
}

.result-insight-card {
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid #e8d5a0;
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 20px;
}

.result-insight-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}

.result-insight-head h3 {
  margin: 0;
  font-size: 1rem;
  color: #5a2d00;
}

.result-insight-head span {
  font-size: 12px;
  color: #9a7040;
}

.result-insight-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
  color: #4b2c12;
  line-height: 1.6;
}
/* ========================================== */

.ai-spinner {
  width: 40px; height: 40px;
  border: 3px solid #e8d5a0; border-top: 3px solid #8b3d1a;
  border-radius: 50%; margin: 20px auto; animation: spin 1s linear infinite;
}
@keyframes spin { 100% { transform: rotate(360deg); } }

.footer-btns {
  display: flex; justify-content: center; align-items: center;
  gap: 20px; margin-top: 30px; width: 100%;
}
.footer-btns .el-button {
  padding: 12px 25px; min-width: 120px; font-weight: 500; border-radius: 8px;
}

.ai-disclaimer {
  font-size: 13px; color: #6b4c24; line-height: 1.8; text-align: center;
  background: #faf3e0; padding: 10px 15px; border-radius: 8px;
  border: 1px solid #e8d5a0; margin-top: 20px;
}
.ai-disclaimer .highlight { color: #8b3d1a; font-weight: bold; }
.ai-disclaimer .warning  { color: #c0392b; font-weight: bold; }

.reference-note {
  font-size: 12px; color: #5d7a8a; line-height: 1.6;
  background: #f0f4ff; padding: 8px 12px; border-radius: 6px;
  border-left: 3px solid #5d9cec; margin-top: 12px; text-align: left;
}

.reference-section {
  margin-top: 20px; padding: 12px; background: #f0f4ff;
  border: 1px solid #d0e0ff; border-radius: 8px;
}

.ref-title {
  font-size: 13px; font-weight: 600; color: #333;
  margin: 0 0 12px 0;
}

.ref-list {
  display: flex; flex-direction: column; gap: 10px;
}

.ref-item {
  padding: 10px; background: #fff;
  border-left: 3px solid #5d9cec; border-radius: 4px;
  font-size: 12px;
}

.ref-authors {
  display: block; color: #666; font-weight: 600;
  margin-bottom: 4px;
}

.ref-desc {
  margin: 4px 0; color: #666; line-height: 1.5;
}

.ref-link {
  display: inline-block; color: #5d9cec; text-decoration: none;
  font-size: 11px; margin-top: 4px;
  transition: all 0.2s;
}

.ref-link:hover {
  color: #1890ff; text-decoration: underline;
}

@media (max-width: 768px) {
  .content-box {
    width: 96vw;
    padding: 22px 16px;
  }

  .content-box.result-fullscreen {
    width: 100vw;
    height: 100vh;
    padding: 18px 14px 16px;
  }

  .score-grid {
    grid-template-columns: 1fr;
  }

  .summary-card {
    flex-direction: column;
  }

  .thumb-container {
    width: auto;
    flex-direction: row;
    justify-content: flex-start;
  }

  .thumb-img {
    width: 88px;
    height: 88px;
  }

  .radar-img {
    width: 100% !important;
    max-height: 320px !important;
  }

  .footer-btns {
    flex-direction: column;
    gap: 12px;
  }
}
</style>