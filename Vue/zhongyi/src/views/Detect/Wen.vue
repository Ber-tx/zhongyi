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
                ✓ 保持清晰音量 | ✓ 自然呼声 | ✓ 约15秒即可
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
                icon="Microphone"
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
                icon="Close"
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
                  icon="VideoPlay"
                  @click="playRecording"
                >
                  播放
                </el-button>
                <el-button 
                  type="info"
                  size="large"
                  round
                  icon="RefreshRight"
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
        </div>

        <!-- 底部按钮 -->
        <div class="footer-btns">
          <el-button round @click="resetAnalysis">重新分析</el-button>
          <el-button 
            type="success" 
            round 
            :loading="isSavingToDb"
            @click="saveToDatabase"
          >
            确认入库并返回
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
import { ArrowLeft, CircleCheckFilled, Microphone, Close, DocumentCopy, VideoPlay, RefreshRight } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

// ===== 响应式状态 =====
const isRecording = ref(false)
const hasRecording = ref(false)
const isCompleted = ref(false)
const loading = ref(false)
const isSubmitting = ref(false)
const recordingTime = ref(0)
const isSavingToDb = ref(false)  // 入库状态【新增】

// 音频相关
const mediaRecorder = ref(null)
const audioChunks = ref([])
const audioBlob = ref(null)
const playbackAudio = ref(null)
const waveformCanvas = ref(null)
const audioContext = ref(null)
const analyser = ref(null)

// 分析结果
const analysisResult = ref(null)

// 病人信息
const patientInfo = ref({
  id: null,
  idCard: ''
})

// 录制计时器
let recordingTimer = null

// ===== 生命周期 =====
onMounted(() => {
  // 获取病人信息
  let qId = route.query.id
  let qIdCard = route.query.idCard

  if (!qId) qId = localStorage.getItem('current_patient_id')
  if (!qIdCard) qIdCard = localStorage.getItem('current_patient_idCard')

  patientInfo.value.id = qId
  patientInfo.value.idCard = qIdCard

  console.log('==== [DEBUG] 闻诊页最终锁定的病人 ID:', patientInfo.value.id)

  // 初始化音频上下文
  initAudioContext()
})

onUnmounted(() => {
  stopRecording()
  if (recordingTimer) clearInterval(recordingTimer)
})

// ===== 音频上下文初始化 =====
const initAudioContext = () => {
  try {
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
  } catch (error) {
    console.error('AudioContext 初始化失败:', error)
  }
}

// ===== 开始录制 =====
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []
    recordingTime.value = 0
    isRecording.value = true
    hasRecording.value = false

    // 绘制波形
    if (audioContext.value && !analyser.value) {
      analyser.value = audioContext.value.createAnalyser()
      const source = audioContext.value.createMediaStreamAudioSource(stream)
      source.connect(analyser.value)
      drawWaveform()
    }

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = () => {
      audioBlob.value = new Blob(audioChunks.value, { type: 'audio/webm' })
      hasRecording.value = true
      isRecording.value = false

      // 停止流
      stream.getTracks().forEach((track) => track.stop())
    }

    mediaRecorder.value.start()

    // 启动计时器
    recordingTimer = setInterval(() => {
      recordingTime.value++
      if (recordingTime.value >= 30) {
        stopRecording()
      }
    }, 1000)

    ElMessage.success('录制已开始')
  } catch (error) {
    ElMessage.error('无法访问麦克风：' + error.message)
  }
}

// ===== 停止录制 =====
const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }
}

// ===== 绘制波形 =====
const drawWaveform = () => {
  if (!waveformCanvas.value || !analyser.value || !isRecording.value) return

  const canvas = waveformCanvas.value
  const ctx = canvas.getContext('2d')
  const bufferLength = analyser.value.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)

  const draw = () => {
    if (!isRecording.value) return

    analyser.value.getByteFrequencyData(dataArray)

    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.lineWidth = 2
    ctx.strokeStyle = '#5d9cec'
    ctx.beginPath()

    const sliceWidth = (canvas.width * 1.0) / bufferLength
    let x = 0

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0
      const y = (v * canvas.height) / 2

      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }

      x += sliceWidth
    }

    ctx.lineTo(canvas.width, canvas.height / 2)
    ctx.stroke()

    requestAnimationFrame(draw)
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
  audioBlob.value = null
  hasRecording.value = false
  recordingTime.value = 0
  audioChunks.value = []
}

// ===== 提交录制 =====
const submitRecording = async () => {
  if (!audioBlob.value) {
    ElMessage.error('没有录制数据')
    return
  }

  try {
    isSubmitting.value = true
    loading.value = true

    const formData = new FormData()
    formData.append('file', audioBlob.value, 'recording.webm')
    formData.append('patient_id', patientInfo.value.id)
    formData.append('patient_idcard', patientInfo.value.idCard)

    const response = await axios.post('/api/wen/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      analysisResult.value = response.data.data
      isCompleted.value = true
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(response.data.msg || '分析失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败：' + error.message)
  } finally {
    isSubmitting.value = false
    loading.value = false
  }
}

// ===== 重新分析 =====
const resetAnalysis = () => {
  isCompleted.value = false
  analysisResult.value = null
  resetRecording()
}

// ===== 入库操作【新增】=====
const saveToDatabase = async () => {
  if (!analysisResult.value) {
    ElMessage.error('没有分析结果')
    return
  }

  try {
    isSavingToDb.value = true

    // 使用 FormData 发送（与后端 @RequestParam 匹配）
    const formData = new FormData()
    formData.append('patientId', patientInfo.value.id)
    formData.append('idCard', patientInfo.value.idCard)
    formData.append('conclusion', analysisResult.value.main_finding)
    formData.append('confidence', analysisResult.value.confidence.toString())
    formData.append('tags', JSON.stringify(analysisResult.value.constitution_tags))
    formData.append('features', JSON.stringify(analysisResult.value.features || {}))

    console.log('==== [DEBUG] 发送入库请求:', {
      patientId: patientInfo.value.id,
      idCard: patientInfo.value.idCard,
      conclusion: analysisResult.value.main_finding
    })

    // 调用 Spring Boot 入库接口
    const response = await axios.post('/api/wen/save', formData)

    console.log('==== [DEBUG] 后端返回:', response.data)

    if (response.data.code === 0 || response.data.code === 200 || response.data.success) {
      ElMessage.success('闻诊数据已成功入库，返回中...')
      // 标记完成
      localStorage.setItem('wen_finished_id', String(patientInfo.value.id))
      // 立即返回诊断中心
      setTimeout(() => {
        router.push('/detect')
      }, 800)
    } else {
      ElMessage.error(response.data.msg || '入库失败')
    }
  } catch (error) {
    console.error('入库失败:', error)
    ElMessage.error('入库失败：' + error.message)
  } finally {
    isSavingToDb.value = false
  }
}

// ===== 返回天诊中心 =====
const goBack = () => {
  router.push('/detect')
}

// ===== 置信度颜色 =====
const getConfidenceColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.wen-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.orb {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 15s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #fff;
  top: -100px;
  right: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #fff;
  bottom: -50px;
  left: -100px;
  animation-delay: -5s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
}

.content-box {
  position: relative;
  z-index: 10;
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}

.back-btn {
  flex-shrink: 0;
}

.header .title {
  flex-grow: 1;
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: bold;
}

.step-indicator {
  color: #999;
  font-size: 14px;
  margin-top: 5px;
}

.main-body {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}

.recording-module {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.recording-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.waveform-container {
  position: relative;
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.waveform-canvas {
  width: 100%;
  height: 100%;
}

.mic-icon-large {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
}

.recording-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.pulse-ring {
  position: relative;
  width: 80px;
  height: 80px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: pulse-ring 1.5s ease-out infinite;
}

.pulse-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.recording-text {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.timer {
  color: rgba(255, 255, 255, 0.9);
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  font-family: 'Monaco', 'Courier New', monospace;
}

.instructions {
  text-align: center;
  width: 100%;
}

.instruction-text,
.recording-hint {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.recording-hint {
  color: #67c23a;
  font-weight: bold;
}

.controls {
  display: flex;
  justify-content: center;
  width: 100%;
}

.start-controls,
.playback-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
}

.playback-controls .action-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

.recording-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  color: #666;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 40px;
}

.ai-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-module {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #67c23a 0%, #50a150 100%);
  color: #fff;
  padding: 15px 20px;
  border-radius: 10px;
  font-weight: bold;
  margin-bottom: 25px;
  font-size: 16px;
}

.result-card {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 25px;
}

.analysis-box {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #dcdfe6;
}

.metric-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.metric-label {
  font-weight: bold;
  color: #666;
  min-width: 100px;
}

.metric-value {
  flex-grow: 1;
  color: #333;
  font-size: 16px;
}

.constitution-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tag {
  margin: 0;
}

.detail-section {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 2px solid #dcdfe6;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.analysis-details {
  margin: 0;
  padding-left: 20px;
  color: #666;
  line-height: 1.8;
}

.analysis-details li {
  margin-bottom: 10px;
}

.ai-disclaimer {
  margin: 25px 0 0 0;
  padding: 15px;
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.highlight {
  color: #f56c6c;
  font-weight: bold;
}

.warning {
  color: #e6a23c;
  font-weight: bold;
}

.footer-btns {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 25px;
}

@media (max-width: 768px) {
  .content-box {
    padding: 10px;
  }

  .header {
    flex-direction: column;
    text-align: center;
  }

  .header .title {
    font-size: 20px;
  }

  .main-body {
    padding: 20px;
  }

  .waveform-container {
    height: 200px;
  }

  .playback-controls .action-group {
    flex-direction: column;
  }

  .playback-controls .action-group :deep(.el-button) {
    width: 100%;
  }

  .footer-btns {
    flex-direction: column;
  }
}
</style>