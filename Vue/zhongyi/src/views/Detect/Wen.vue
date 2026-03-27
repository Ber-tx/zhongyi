<template>
  <div class="wen-container">
    <div class="animated-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <div class="content-box">
      <div class="header">
        <el-button icon="ArrowLeft" circle @click="goBack" class="back-btn" />
        <h2 class="title">闻诊分析 · 音频采集</h2>
        <div class="step-indicator">通过语音和呼吸声辨析体质</div>
      </div>

      <div v-if="!isCompleted" class="main-body">
        <!-- 1. 录制模块 -->
        <div v-if="!loading" class="recording-module">
          <div class="recording-area">
            <!-- 波形可视化 -->
            <div class="waveform-container">
              <canvas ref="waveformCanvas" class="waveform-canvas"></canvas>
              <div v-if="!isRecording" class="mic-icon-large">
                <el-icon :size="60" color="#5d9cec"><Microphone /></el-icon>
              </div>
              <div v-else class="recording-indicator">
                <div class="pulse-ring">
                  <div class="pulse-dot"></div>
                </div>
                <p class="recording-text">录制中...</p>
                <p class="timer">{{ recordingTime }}秒</p>
              </div>
            </div>

            <!-- 指引文本 -->
            <div class="instructions">
              <p v-if="!isRecording" class="instruction-text">
                请点击下方按钮开始录制。先说出您的姓名，然后进行3-5次深呼吸。
              </p>
              <p v-else class="recording-hint">
                ✓ 保持清晰音量 | ✓ 自然呼吸 | ✓ 约15秒即可
              </p>
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="controls">
            <div v-if="!hasRecording" class="start-controls">
              <el-button
                v-if="!isRecording"
                type="success"
                size="large"
                round
                :icon="Microphone"
                @click="startRecording"
                class="action-btn"
              >
                开始录制
              </el-button>
              <el-button
                v-else
                type="danger"
                size="large"
                round
                :icon="Close"
                @click="stopRecording"
                class="action-btn"
              >
                停止录制
              </el-button>
            </div>

            <!-- 录制完成后的操作 -->
            <div v-else class="playback-controls">
              <div class="recording-info">
                <el-icon><DocumentCopy /></el-icon>
                <span>已录制：{{ recordingTime }}秒</span>
              </div>

              <div class="action-group">
                <el-button
                  type="primary"
                  size="large"
                  round
                  :icon="VideoPlay"
                  @click="playRecording"
                >
                  播放
                </el-button>
                <el-button
                  type="info"
                  size="large"
                  round
                  :icon="RefreshRight"
                  @click="resetRecording"
                >
                  重新录制
                </el-button>
                <el-button
                  type="success"
                  size="large"
                  round
                  :loading="isSubmitting"
                  @click="submitRecording"
                >
                  分析 & 提交
                </el-button>
              </div>
            </div>
          </div>

          <!-- 隐藏音频标签 -->
          <audio ref="playbackAudio" style="display: none;"></audio>
        </div>

        <!-- 加载状态 -->
        <div v-else class="loading-state">
          <div class="ai-spinner"></div>
          <h3>AI 引擎分析中...</h3>
          <p>正在计算音频特征和体质倾向</p>
        </div>
      </div>

      <!-- 分析结果展示 -->
      <div v-else class="result-module">
        <div class="success-banner">
          <el-icon><CircleCheckFilled /></el-icon>
          闻诊分析完成
        </div>

        <div class="result-card">
          <div class="analysis-box">
            <div class="metric-item">
              <span class="metric-label">主要判断：</span>
              <span class="metric-value">{{ analysisResult.main_finding }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">置信度：</span>
              <el-progress
                :percentage="Math.round(analysisResult.confidence * 100)"
                :color="getConfidenceColor"
                class="metric-value"
              />
            </div>
            <div class="metric-item">
              <span class="metric-label">体质倾向：</span>
              <div class="constitution-tags">
                <el-tag
                  v-for="tag in analysisResult.constitution_tags"
                  :key="tag"
                  type="info"
                  class="tag"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 详细分析 -->
          <div class="detail-section">
            <h4>详细分析</h4>
            <ul class="analysis-details">
              <li v-for="(detail, index) in analysisResult.details" :key="index">
                {{ detail }}
              </li>
            </ul>
          </div>

          <!-- AI声明 -->
          <p class="ai-disclaimer">
            本分析由 <span class="highlight">AI 引擎</span> 提供，仅供健康参考，<br />
            <span class="warning">不作为临床诊断依据</span>。确诊请咨询 <span class="highlight">专业医师</span>。
          </p>

          <div class="reference-section">
            <p class="ref-title">📖 参考文献与出处</p>
            <div class="ref-list">
              <div v-for="(ref, idx) in wenReferences" :key="idx" class="ref-item">
                <span class="ref-authors">{{ ref.authors }} ({{ ref.year }})</span>
                <p class="ref-desc">{{ ref.title }}</p>
                <a v-if="ref.url" :href="ref.url" target="_blank" class="ref-link">
                  查看 → {{ ref.source }}
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="footer-btns">
          <el-button round @click="resetAnalysis">重新分析</el-button>
          <el-button type="primary" round @click="generateDiagnosisReport">
            生成报告
          </el-button>
          <el-button
            type="success"
            round
            @click="saveToDatabase"
          >
            确认并返回
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  CircleCheckFilled,
  Microphone,
  Close,
  DocumentCopy,
  VideoPlay,
  RefreshRight
} from '@element-plus/icons-vue'
import axios from 'axios'
import { navigateToDiagnosisReport } from '@/utils/reportUtils'
import { algorithmReferences } from '@/constants/algorithmReferences'

const router = useRouter()
const route  = useRoute()

// ===== 响应式状态 =====
const isRecording  = ref(false)
const hasRecording = ref(false)
const isCompleted  = ref(false)
const wenReferences = ref(algorithmReferences.wen_audio.references)
const loading      = ref(false)
const isSubmitting = ref(false)
const recordingTime = ref(0)

// 音频相关
const mediaRecorder  = ref(null)
const audioChunks    = ref([])
const audioBlob      = ref(null)
const playbackAudio  = ref(null)
const waveformCanvas = ref(null)
const audioContext   = ref(null)
const analyser       = ref(null)

// 分析结果
const analysisResult = ref(null)

// 病人信息
const patientInfo = ref({ id: null, idCard: '' })

// 计时器句柄
let recordingTimer = null

// ===== 生命周期 =====
// 【修复1】onMounted 不再初始化 AudioContext，改为懒加载
onMounted(() => {
  let qId     = route.query.id
  let qIdCard = route.query.idCard
  if (!qId)     qId     = localStorage.getItem('current_patient_id')
  if (!qIdCard) qIdCard = localStorage.getItem('current_patient_idCard')
  patientInfo.value.id     = qId
  patientInfo.value.idCard = qIdCard
  console.log('==== [DEBUG] 闻诊页最终锁定的病人 ID:', patientInfo.value.id)
})

onUnmounted(() => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
  }
  if (recordingTimer) clearInterval(recordingTimer)
})

// ===== 【修复1】AudioContext 懒加载，在用户点击时才创建/恢复 =====
const ensureAudioContext = async () => {
  if (!audioContext.value) {
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
  }
  // 浏览器在无用户手势时会 suspend，点击后必须 resume
  if (audioContext.value.state === 'suspended') {
    await audioContext.value.resume()
  }
}

// ===== 开始录制 =====
const startRecording = async () => {
  try {
    // 【修复1】先确保 AudioContext 就绪（在用户手势内，不会被浏览器拦截）
    await ensureAudioContext()

    // 请求麦克风权限，细分错误提示
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch (permError) {
      if (permError.name === 'NotAllowedError' || permError.name === 'PermissionDeniedError') {
        ElMessage.error('麦克风权限被拒绝，请在浏览器地址栏左侧允许麦克风访问后重试')
      } else if (permError.name === 'NotFoundError') {
        ElMessage.error('未检测到麦克风设备，请检查设备连接')
      } else {
        ElMessage.error('麦克风访问失败：' + permError.message)
      }
      return
    }

    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value   = []
    recordingTime.value = 0
    isRecording.value   = true
    hasRecording.value  = false
    analyser.value      = null   // 每次录制前重置，避免旧引用残留

    // 绘制波形
    analyser.value = audioContext.value.createAnalyser()
    
    const source   = audioContext.value.createMediaStreamSource(stream)
    source.connect(analyser.value)
    drawWaveform()

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = () => {
      audioBlob.value    = new Blob(audioChunks.value, { type: 'audio/webm' })
      hasRecording.value = true
      isRecording.value  = false
      stream.getTracks().forEach((track) => track.stop())
    }

    mediaRecorder.value.start()

    recordingTimer = setInterval(() => {
      recordingTime.value++
      if (recordingTime.value >= 30) stopRecording()
    }, 1000)

    ElMessage.success('录制已开始')
  } catch (error) {
    isRecording.value = false
    console.error('录制启动异常:', error)
    ElMessage.error('录制启动失败：' + error.message)
  }
}

// ===== 停止录制 =====
const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
  }
  if (recordingTimer) {
    clearInterval(recordingTimer)
    recordingTimer = null
  }
}

// ===== 绘制波形 =====
const drawWaveform = () => {
  if (!waveformCanvas.value || !analyser.value || !isRecording.value) return

  const canvas      = waveformCanvas.value
  const ctx         = canvas.getContext('2d')
  const bufferLength = analyser.value.fftSize
  const dataArray   = new Uint8Array(bufferLength)

  const draw = () => {
    if (!isRecording.value) return
    requestAnimationFrame(draw)

    // 用时域数据，静音时值为128，天然居中
    analyser.value.getByteTimeDomainData(dataArray)

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    ctx.lineWidth   = 2
    ctx.strokeStyle = '#5d9cec'
    ctx.beginPath()

    const sliceWidth = canvas.width / bufferLength
    let x = 0

    for (let i = 0; i < bufferLength; i++) {
      // 128 对应中线，0-255 映射到 canvas 上下
      const y = (dataArray[i] / 255.0) * canvas.height
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      x += sliceWidth
    }

    ctx.stroke()
  }

  draw()
}

// ===== 播放录制 =====
const playRecording = () => {
  if (audioBlob.value) {
    const url = URL.createObjectURL(audioBlob.value)
    playbackAudio.value.src = url
    playbackAudio.value.play()
  }
}

// ===== 重置录制 =====
const resetRecording = () => {
  audioBlob.value    = null
  hasRecording.value = false
  recordingTime.value = 0
  audioChunks.value  = []
}

// ===== 提交录制 =====
const submitRecording = async () => {
  if (!audioBlob.value) {
    ElMessage.error('没有录制数据')
    return
  }

  try {
    isSubmitting.value = true
    loading.value      = true

    const formData = new FormData()
    const diagnosisId = route.query.caseId || localStorage.getItem('current_case_id')
    formData.append('file',            audioBlob.value, 'recording.webm')
    formData.append('patient_id',      patientInfo.value.id)
    formData.append('patient_idcard',  patientInfo.value.idCard)
    if (diagnosisId) {
      formData.append('diagnosis_id', diagnosisId)
    }

    const response = await axios.post('/api/wen/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    })

    const res = response.data
    // 【修复2】Java Result 返回的是 code 字段，不是 success 字段
    if (res.code === 0 || res.code === 200) {
      analysisResult.value = res.data
      isCompleted.value    = true
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(res.msg || '分析失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败：' + error.message)
  } finally {
    isSubmitting.value = false
    loading.value      = false
  }
}

// ===== 重新分析 =====
const resetAnalysis = () => {
  isCompleted.value    = false
  analysisResult.value = null
  resetRecording()
}

// 与「确认并返回」一致：锁定闻诊后再跳转报告（含其他已完成板块）
const generateDiagnosisReport = () => {
  if (!patientInfo.value.id) {
    ElMessage.error('患者ID丢失，无法生成报告')
    return
  }
  localStorage.setItem('wen_finished_id', String(patientInfo.value.id))
  navigateToDiagnosisReport(router, patientInfo.value.id, patientInfo.value.idCard)
}

// ===== 确认并返回 =====
// 【修复3】分析时已经同步入库，这里只需跳转
const saveToDatabase = () => {
  localStorage.setItem('wen_finished_id', String(patientInfo.value.id))
  ElMessage.success('闻诊已完成，返回中...')
  setTimeout(() => router.push('/detect'), 800)
}

// ===== 返回诊断中心 =====
const goBack = () => router.push('/detect')

// ===== 置信度颜色 =====
const getConfidenceColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
/* ── 与主系统统一的暖棕色调 ── */
.wen-container {
  min-height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  position: relative; overflow: hidden;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

/* 宣纸纹理 */
.wen-container::before {
  content: ''; position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
}

.animated-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; opacity: 0.08; animation: float 15s ease-in-out infinite; }
.orb-1 { width: 400px; height: 400px; background: #8b3d1a; top: -100px; right: -100px; }
.orb-2 { width: 300px; height: 300px; background: #c8a020; bottom: -50px; left: -100px; animation-delay: -5s; }
@keyframes float { 0%,100% { transform: translate(0,0); } 50% { transform: translate(30px,-30px); } }

.content-box {
  position: relative; z-index: 10;
  max-width: 1000px; margin: 20px auto; padding: 20px;
}

.header {
  display: flex; align-items: center; gap: 20px;
  margin-bottom: 30px;
  background: rgba(255,252,242,.95);
  padding: 20px; border-radius: 10px;
  border: 1px solid #c8a96e;
  box-shadow: 0 4px 16px rgba(100,60,10,.10);
}
.back-btn { flex-shrink: 0; }
.header .title { flex-grow: 1; margin: 0; color: #3d2b10; font-size: 22px; font-weight: 700; }
.step-indicator { color: #8b6030; font-size: 13px; margin-top: 4px; }

.main-body {
  background: rgba(255,252,242,.95);
  border-radius: 10px; padding: 36px;
  border: 1px solid #c8a96e;
  box-shadow: 0 4px 16px rgba(100,60,10,.10);
}

.recording-module { display: flex; flex-direction: column; gap: 28px; }
.recording-area { display: flex; flex-direction: column; align-items: center; gap: 20px; }

/* 波形区域 — 深棕背景取代紫色 */
.waveform-container {
  position: relative; width: 100%; height: 280px;
  background: linear-gradient(135deg, #2e1a0a 0%, #1e100a 100%);
  border-radius: 12px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid #c8a96e;
}
.waveform-canvas { width: 100%; height: 100%; }
.mic-icon-large { display: flex; align-items: center; justify-content: center; opacity: 0.7; }

.recording-indicator { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.pulse-ring {
  position: relative; width: 80px; height: 80px;
  border: 3px solid rgba(200,160,32,.4); border-radius: 50%;
  animation: pulse-ring 1.5s ease-out infinite;
}
.pulse-dot {
  position: absolute; top: 50%; left: 50%;
  width: 20px; height: 20px;
  background: #c8a020; border-radius: 50%;
  transform: translate(-50%,-50%);
}
@keyframes pulse-ring { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(1.5); opacity: 0; } }

.recording-text { color: #fdeabb; font-size: 17px; font-weight: bold; margin: 0; }
.timer { color: rgba(253,234,187,.9); font-size: 24px; font-weight: bold; margin: 0; font-family: 'Courier New', monospace; }

.instructions { text-align: center; width: 100%; }
.instruction-text, .recording-hint { margin: 0; color: #6b4c24; font-size: 14px; line-height: 1.6; }
.recording-hint { color: #4a7060; font-weight: bold; }

.controls { display: flex; justify-content: center; width: 100%; }
.start-controls, .playback-controls { display: flex; flex-direction: column; align-items: center; gap: 18px; width: 100%; }
.playback-controls .action-group { display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; }

.recording-info {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px;
  background: #faf3e0; border-radius: 8px; border: 1px solid #e8d5a0;
  color: #6b4c24;
}

.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; padding: 40px; }
.ai-spinner {
  width: 56px; height: 56px;
  border: 4px solid #e8d5a0; border-top: 4px solid #8b3d1a;
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 结果模块 */
.result-module {
  background: rgba(255,252,242,.95);
  border-radius: 10px; padding: 36px;
  border: 1px solid #c8a96e;
  box-shadow: 0 4px 16px rgba(100,60,10,.10);
}

.success-banner {
  display: flex; align-items: center; gap: 10px;
  background: linear-gradient(135deg, #4a7060, #2d5a4a);
  color: #fdeabb; padding: 14px 20px; border-radius: 8px;
  font-weight: bold; margin-bottom: 24px; font-size: 15px;
}

.result-card {
  background: #faf3e0; border-radius: 10px; border: 1px solid #e8d5a0;
  padding: 24px; margin-bottom: 22px;
}
.analysis-box { display: flex; flex-direction: column; gap: 18px; }

.metric-item {
  display: flex; align-items: center; gap: 14px;
  padding-bottom: 14px; border-bottom: 1px solid #e8d5a0;
}
.metric-item:last-child { border-bottom: none; padding-bottom: 0; }
.metric-label { font-weight: bold; color: #6b4c24; min-width: 100px; }
.metric-value { flex-grow: 1; color: #3d2b10; font-size: 15px; }
.constitution-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { margin: 0; }

.detail-section { margin-top: 22px; padding-top: 22px; border-top: 1px solid #e8d5a0; }
.detail-section h4 { margin: 0 0 14px; color: #3d2b10; font-size: 15px; font-weight: 700; }
.analysis-details { margin: 0; padding-left: 20px; color: #6b4c24; line-height: 1.8; }
.analysis-details li { margin-bottom: 8px; }

.ai-disclaimer {
  margin: 22px 0 0;
  padding: 14px; background: #faf3e0;
  border-left: 4px solid #c8a020; border-radius: 4px;
  font-size: 13px; color: #6b4c24; line-height: 1.6;
}
.highlight { color: #8b3d1a; font-weight: bold; }
.warning   { color: #c0392b; font-weight: bold; }

.footer-btns { display: flex; gap: 14px; justify-content: center; margin-top: 22px; }

@media (max-width: 768px) {
  .content-box { padding: 10px; }
  .header { flex-direction: column; text-align: center; }
  .header .title { font-size: 18px; }
  .main-body { padding: 20px; }
  .waveform-container { height: 200px; }
  .playback-controls .action-group { flex-direction: column; }
  .playback-controls .action-group :deep(.el-button) { width: 100%; }
  .footer-btns { flex-direction: column; }
}

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
