<template>
  <div class="wang-container">
    <div class="animated-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <div class="content-box">
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
        <div class="success-banner"><el-icon><CircleCheckFilled /></el-icon> 诊断完成</div>
        <div class="conclusion">
          <span class="label">初步辨证结论：</span>
          <span class="value">{{ analysisResult.main_result }}</span>
          
        </div>
        <div class="charts">
          <div class="img-card">
            <p>采集样本</p>
            <img :src="localImageUrl" class="preview-img" />
          </div>
          <div class="img-card">
            <p>辨证模型 (点击放大)</p>
            <el-image 
              :src="analysisResult.chart_img" 
              :preview-src-list="[analysisResult.chart_img]"
              fit="contain"
              class="preview-img radar-large"
              preview-teleported
              :hide-on-click-modal="true"
            />
          </div>
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
import { ref, onUnmounted, onMounted,h } from 'vue'
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
      throw new Error(res.data.msg || "后端返回失败");
    }
  } catch (err) {
    console.error("上传错误:", err);
    ElMessage.error(err.message || "分析失败，请检查网络");
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
  width: 92%; max-width: 560px;
  background: rgba(255, 252, 242, 0.92);
  backdrop-filter: blur(16px);
  border-radius: 12px;
  padding: 26px;
  border: 1px solid #c8a96e;
  box-shadow: 0 20px 50px rgba(100,60,10,.14),
              inset 0 1px 0 rgba(255,248,220,.8);
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

/* ========== ✅ 这里是改小图片的核心 ========== */
.charts {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 15px;
  align-items: center;
}

.img-card {
  width: 85%;
  font-size: 14px;
  color: #5a2d00;
  font-weight: bold;
  text-align: center;
  background: rgba(250,243,224,.7);
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e8d5a0;
}

.preview-img {
  width: 60% !important;
  max-height: 200px !important;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #e8d5a0;
  background: #fffdf5;
  margin: 8px auto;
  display: block;
  box-shadow: 0 4px 12px rgba(100,60,10,.08);
}

.radar-large {
  width: 65% !important;
  max-height: 220px !important;
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
</style>