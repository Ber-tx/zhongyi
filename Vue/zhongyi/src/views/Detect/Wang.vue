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
        
        <!-- 新增 AI 声明部分 -->
        <p class="ai-disclaimer">
          本分析由 <span class="highlight">AI 引擎</span> 提供，仅供健康参考，<br />
          <span class="warning">不作为临床诊断依据</span>。确诊请咨询 <span class="highlight">专业医师</span>。
        </p>
        
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
import { ref, onUnmounted, onMounted,h } from 'vue' // 增加 onMounted
import { useRouter, useRoute } from 'vue-router' // 增加 useRoute
import { Camera, ArrowLeft, CircleCheckFilled, Picture, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'; // 增加 ElMessageBox 引入
import { navigateToDiagnosisReport } from '@/utils/reportUtils';
import { uploadTongue } from '@/api/detect';
const router = useRouter()
const route = useRoute() // 获取当前路由对象，用于提取 ID

const videoPlayer = ref(null)
const isCameraOpen = ref(false)
const isCompleted = ref(false)
const loading = ref(false)
const mediaStream = ref(null)
const localImageUrl = ref('')
const analysisResult = ref(null)

// 定义响应式病人信息，初始化时从路由获取
const patientInfo = ref({
  id: null,
  idCard: ''
})

onMounted(() => {
  // 1. 尝试从 URL 拿
  let qId = route.query.id;
  let qIdCard = route.query.idCard;

  // 2. 如果 URL 没带（比如用户刷新了），从缓存拿
  if (!qId) qId = localStorage.getItem('current_patient_id');
  if (!qIdCard) qIdCard = localStorage.getItem('current_patient_idCard');

  // 3. 填入 patientInfo 供 uploadImage 使用
  patientInfo.value.id = qId;
  patientInfo.value.idCard = qIdCard;

  console.log("==== [DEBUG] 望诊页最终锁定的病人 ID:", patientInfo.value.id);
  
  // 页面进入时，清除该患者的望诊完成标记（防止未完成的情况被误认为完成）
  // 只有真正完成分析时才会重新设置
  localStorage.removeItem('wang_finished_id');
  
  // 补丁：开启相机
  startCamera();
});

const goBack = () => {
  stopCamera();
  // 如果诊断未完成，清除该板块的完成标记
  if (!isCompleted.value) {
    localStorage.removeItem('wang_finished_id');
  }
  router.push('/detect');
}

// 相机逻辑
const startCamera = async () => {
  localImageUrl.value = '';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 1280, height: 720, facingMode: "user" } 
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
  canvas.width = videoPlayer.value.videoWidth;
  canvas.height = videoPlayer.value.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.translate(canvas.width, 0); ctx.scale(-1, 1); 
  ctx.drawImage(videoPlayer.value, 0, 0);
  const base64 = canvas.toDataURL('image/jpeg', 0.8);
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

// 文件上传逻辑
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

// 【核心修复】后端交互逻辑
const uploadImage = async (base64) => {
  // --- 【自由传参修复：多渠道获取 ID】 ---
  // 优先级：当前组件变量 > URL 参数 > 本地缓存
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
  // ---------------------------------------

  loading.value = true;
  try {
    const blob = await (await fetch(base64)).blob();
    const formData = new FormData();
    
    // 1. 塞入文件
    formData.append('file', blob, 'tongue.jpg');

    // 2. 将 ID 和 身份证塞进信封
    // 注意：即使 patientInfo.value.id 为空，我们也用上面检索到的 pid
    formData.append('id', pid); 
    if (icard) {
      formData.append('idCard', icard);
    }
    if (diagnosisId) {
      formData.append('diagnosisId', diagnosisId);
    }

    console.log("==== [DEBUG] 望诊提交，锁定病人 ID:", pid);

    // 3. 发送请求 
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
        // 不在这里标记完成，等用户点击"继续下一个"或"生成报告"时才标记
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
  // 补丁：如果是重新拍摄，需要重启相机
  startCamera(); 
  // 注意：这里绝对不重置 patientInfo.value.id，保证重测时 ID 依然有效
}

// 新增：继续下一个诊断或返回诊断选择页面
const goToNextOrReport = () => {
  stopCamera();
  // 用户点击继续时，标记望诊为已完成
  const pid = patientInfo.value.id || localStorage.getItem('current_patient_id');
  if (isCompleted.value && pid) {
    localStorage.setItem('wang_finished_id', String(pid));
  }
  router.push('/detect');
}

const generatePartialReport = () => {
  const patientId = patientInfo.value.id || localStorage.getItem('current_patient_id');
  const idCard = patientInfo.value.idCard || localStorage.getItem('current_patient_idCard');
  // 用户点击生成报告时，标记望诊为已完成
  if (isCompleted.value && patientId) {
    localStorage.setItem('wang_finished_id', String(patientId));
  }
  navigateToDiagnosisReport(router, patientId, idCard);
}


onUnmounted(stopCamera);


</script>

<style scoped>
/* ── 与主系统统一的暖棕色调 ── */
.wang-container {
  min-height: 100vh;
  position: relative;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  display: flex; justify-content: center; align-items: center;
  overflow: hidden;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

/* 宣纸纹理 */
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

/* 顶部金线 */
.content-box::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, #c8a020 50%, transparent);
  border-radius: 12px 12px 0 0;
}

.header { text-align: center; margin-bottom: 20px; position: relative; }
.back-btn { position: absolute; left: 0; top: 5px; }
.title { font-size: 1.5rem; margin: 0; font-family: 'Noto Serif SC', "Source Han Serif CN", serif; color: #3d2b10; }

/* 摄像头区域 */
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

.charts { display: flex; flex-direction: column; gap: 20px; margin-top: 15px; }

.img-card {
  width: 100%; font-size: 14px; color: #5a2d00; font-weight: bold;
  text-align: left; background: rgba(250,243,224,.7);
  padding: 10px; border-radius: 8px;
  border: 1px solid #e8d5a0;
}

.preview-img {
  width: 70%; height: auto; max-height: 320px;
  object-fit: contain; border-radius: 8px;
  border: 1px solid #e8d5a0; background: #fffdf5;
  margin: 8px auto; display: block;
  box-shadow: 0 4px 12px rgba(100,60,10,.08);
}

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
</style>
