<template>
  <div class="wang-page">
    <!-- ===== 检测区 ===== -->
    <section class="hero system-hero" id="detect">
      <div class="container hero-grid">
        <div class="hero-content">
          <div class="nav-row">
            <el-button icon="ArrowLeft" circle @click="goBack" class="back-btn" />
            <p class="eyebrow">YOLOv8 Tongue Detection</p>
          </div>
          <h1 class="hero-title">自动框选舌象区域，并把每个结果对应到标注表</h1>
          <p class="hero-subtitle">上传图片或打开摄像头，系统会在图中叠加检测框、类别和置信度。一个舌面可出现多个区域结果，分别给出标注解释。</p>

          <div class="hero-actions">
            <label class="btn btn-file">
              {{ selectedFiles.length ? `已选 ${selectedFiles.length} 张` : '选择图片' }}
              <input type="file" accept="image/*" multiple @change="handleFileChange" />
            </label>
            <button class="btn btn-primary" :disabled="loading || (!selectedFile && !selectedFiles.length)" @click="uploadAndDetect">
              {{ loading ? '检测中...' : selectedFiles.length ? '逐张检测' : '识别图片' }}
            </button>
            <button v-if="selectedFiles.length || uploadResults.length" class="btn" @click="clearUploads">清除</button>
            <button class="btn" @click="openCamera">{{ cameraRunning ? '关闭摄像头' : '打开摄像头' }}</button>
          </div>
          <p class="upload-status">{{ statusText || '支持选择多张图片综合分析' }}</p>

          <!-- 多图预览 -->
          <div v-if="selectedFiles.length && !uploadResults.length" class="multi-preview">
            <div v-for="(url, idx) in uploadPreviews" :key="idx" class="multi-thumb">
              <img :src="url" alt="" />
              <button class="thumb-remove" @click="removeUploadFile(idx)">&times;</button>
            </div>
          </div>

          <!-- 多图检测结果缩略图 -->
          <div v-if="uploadResults.length" class="multi-preview">
            <div v-for="(ur, idx) in uploadResults" :key="idx" class="multi-thumb" :class="{ active: result === ur.result }" @click="selectUploadResult(ur, idx)">
              <img :src="ur.preview" alt="" />
              <span class="thumb-badge">{{ idx + 1 }}</span>
              <span class="thumb-dets">{{ ur.result?.detections?.length || 0 }} 框</span>
            </div>
          </div>

          <!-- 统计卡片 -->
          <div class="hero-meta">
            <div class="meta-card">
              <p class="meta-label">识别区域</p>
              <p class="meta-value">{{ result?.detections?.length || 0 }}</p>
              <p class="meta-desc">当前识别的框数量</p>
            </div>
            <div class="meta-card">
              <p class="meta-label">模型状态</p>
              <p class="meta-value">{{ modelLoaded ? '就绪' : '异常' }}</p>
              <p class="meta-desc">20 类舌象检测</p>
            </div>
            <div class="meta-card">
              <p class="meta-label">风险等级</p>
              <p class="meta-value" :class="riskLevel">{{ riskText }}</p>
              <p class="meta-desc">基于标注规范匹配</p>
            </div>
          </div>
        </div>

        <!-- 右侧预览 + 检测框 -->
        <div class="preview-card">
          <div ref="previewFrameRef" class="preview-frame" :class="{ live: mediaMode === 'camera' }">
            <img v-if="mediaMode === 'upload' && previewUrl" ref="imageRef" :src="previewUrl" alt="待识别舌像预览" @load="updateDisplayMetrics" />
            <video v-show="mediaMode === 'camera'" ref="videoRef" autoplay playsinline muted @loadedmetadata="updateDisplayMetrics"></video>
            <img v-if="mediaMode === 'camera' && frozenFrameUrl" ref="frozenFrameRef" class="frozen-frame" :src="frozenFrameUrl" alt="锁定的检测帧" @load="updateDisplayMetrics" />
            <div v-if="!previewUrl && !frozenFrameUrl && mediaMode === 'upload'" class="empty-preview"><span>上传舌像或打开摄像头</span></div>

            <!-- YOLO 检测框叠加层 -->
            <div v-if="detections.length" class="box-layer">
              <button v-for="(det, index) in detections" :key="`${det.class_id}-${index}`" class="detect-box" :class="{ active: selectedRegionIndex === index }" :style="boxStyle(det)" @mouseenter="selectedRegionIndex = index" @mouseleave="selectedRegionIndex = null">
                <span class="box-corner">{{ index + 1 }}</span>
              </button>
            </div>
          </div>

          <!-- 图例 -->
          <div v-if="detections.length" class="overlay-legend">
            <span v-for="(det, index) in detections" :key="'lg-'+index"><b :style="{ background: det.color }">{{ index + 1 }}</b>{{ det.class }}</span>
          </div>
          <div class="detection-meta">
            <span class="status-pill" :class="riskLevel === 'normal' ? 'success' : riskLevel === 'attention' ? 'danger' : ''">结论：{{ riskText }}</span>
            <span class="status-pill">区域 {{ detections.length }}</span>
            <span v-if="aggregatedResult" class="status-pill warn">综合分析</span>
          </div>

          <!-- 摄像头控制 -->
          <div v-if="cameraRunning" class="capture-actions">
            <button v-if="captureStep < totalCaptures" class="btn btn-primary" @click="captureSingleFrame">捕获第 {{ captureStep + 1 }} / {{ totalCaptures }} 张</button>
            <button class="btn" @click="closeCamera">关闭</button>
          </div>

          <!-- 捕获完成 → 检测 -->
          <div v-if="capturedFrames.length && !cameraRunning && !captureResults.length" class="capture-actions">
            <span class="capture-hint">已捕获 {{ capturedFrames.length }} 张</span>
            <button class="btn btn-primary" :disabled="batchLoading" @click="detectCaptures">{{ batchLoading ? '检测中...' : '逐帧检测' }}</button>
            <button class="btn" @click="clearCaptures">重拍</button>
          </div>

          <!-- 已捕获帧缩略图 -->
          <div v-if="capturedFrames.length && !captureResults.length" class="capture-thumbs">
            <div v-for="(cf, idx) in capturedFrames" :key="idx" class="capture-thumb"><img :src="cf.image" alt="" /><span class="thumb-badge">{{ idx + 1 }}</span></div>
          </div>

          <!-- 检测后操作 -->
          <div v-if="captureResults.length" class="capture-actions">
            <span class="capture-hint">{{ aggregatedResult ? '查看综合分析结果' : '点击缩略图查看单张结果' }}</span>
            <button v-if="capturedFrames.length >= 2 && !aggregatedResult" class="btn btn-primary" :disabled="batchLoading" @click="aggregateCaptures">{{ batchLoading ? '分析中...' : '综合分析' }}</button>
            <button class="btn" @click="clearCaptures">清除</button>
          </div>

          <!-- 检测后帧缩略图 -->
          <div v-if="captureResults.length" class="capture-thumbs">
            <div v-for="(cr, idx) in captureResults" :key="idx" class="capture-thumb" :class="{ active: result === cr.result }" @click="selectCaptureResult(cr, idx)">
              <img :src="cr.image" alt="" /><span class="thumb-badge">{{ idx + 1 }}</span>
              <span class="thumb-count">{{ cr.result?.detections?.length || 0 }} 框</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 结果区 ===== -->
    <section class="section section-alt" id="result" v-if="result">
      <div class="container">
        <div class="section-header">
          <p class="eyebrow">Detection Result</p>
          <h2 class="section-title">图中框选结果与结论</h2>
          <p class="section-subtitle">{{ mainConclusion }}</p>
        </div>

        <div class="result-grid">
          <div class="card result-card">
            <div class="card-header"><h3>区域识别明细</h3><span class="tag">同一舌面可多结果</span></div>
            <div v-if="detections.length" class="region-list">
              <article v-for="(det, index) in detections" :key="`${det.class}-${index}`" class="region-card" :class="{ active: selectedRegionIndex === index }" @mouseenter="selectedRegionIndex = index" @mouseleave="selectedRegionIndex = null">
                <div class="region-index" :style="{ background: det.color }">{{ index + 1 }}</div>
                <div class="region-body">
                  <h4>{{ det.class }} <span>{{ det.class_id }} / {{ det.class_code }}</span></h4>
                  <p><strong>定义与判定要点：</strong>{{ fieldText(matchFor(det), ['定义与判定要点', 'definition']) }}</p>
                  <p><strong>中医诊断：</strong>{{ fieldText(matchFor(det), ['中医诊断', 'diagnosis']) }}</p>
                  <small>{{ fieldText(matchFor(det), ['诊断通俗解释', 'plain_explanation']) }}</small>
                </div>
                <span class="tag">{{ Math.round(det.confidence * 100) }}%</span>
              </article>
            </div>
            <div v-else class="empty-state">还没有检测框</div>
          </div>

          <div class="card summary-card">
            <h3>{{ analysisReady ? '当前选中区域摘要' : '待检测分析' }}</h3>
            <div v-if="analysisReady && selectedMatch" class="tip-list">
              <div class="tip-item"><strong>{{ selectedMatch.label }}</strong><p>{{ selectedMatch.dimension || '标注表匹配项' }}</p></div>
              <div class="tip-item"><strong>置信度</strong><p>{{ Math.round((selectedMatch.confidence || 0) * 100) }}%</p></div>
              <div class="tip-item"><strong>匹配标签数</strong><p>{{ matchItems.length }} 个</p></div>
            </div>
            <ul v-else class="tip-list">
              <li class="tip-item">右侧仅显示当前选中项的摘要</li>
            </ul>
          </div>
        </div>

        <!-- 雷达图 + 评分 -->
        <div class="card radar-card">
          <div class="radar-layout">
            <div class="radar-box">
              <el-image v-if="result?.chart_img" :src="result.chart_img" :preview-src-list="[result.chart_img]" fit="contain" class="radar-img" preview-teleported />
            </div>
            <div class="score-grid">
              <div class="score-item" v-for="item in scoreSummary" :key="item.name">
                <div class="score-row"><span class="k">{{ item.name }}</span><span class="v">{{ item.mean }}</span></div>
                <el-progress :percentage="item.mean" :stroke-width="8" :show-text="false" color="#8b3d1a" />
              </div>
            </div>
          </div>
        </div>

        <!-- 综合分析结论 -->
        <div v-if="aggregatedResult && aggregatedResult.detections?.length" class="card">
          <div class="card-header"><h3>综合结论</h3><span class="tag">{{ captureResults.length || uploadResults.length }} 次采样聚合</span></div>
          <div class="region-list">
            <article v-for="(det, index) in aggregatedResult.detections" :key="'agg-'+index" class="region-card">
              <div class="region-index" :style="{ background: det.color }">{{ index + 1 }}</div>
              <div class="region-body">
                <h4>{{ det.class }}</h4>
                <p>置信度：{{ Math.round(det.confidence * 100) }}%（多帧平均）</p>
              </div>
              <span class="tag">聚合</span>
            </article>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 底部操作 ===== -->
    <section class="section" v-if="result">
      <div class="container footer-actions">
        <p class="disclaimer">本分析由 <strong>YOLOv8 + 标注规范表</strong> 提供，仅供健康参考，<span class="warning">不作为临床诊断依据</span>。</p>
        <div class="btn-row">
          <button class="btn" @click="resetAll">重新分析</button>
          <button class="btn btn-primary" @click="confirmAndSave">确认并保存诊断</button>
          <button class="btn btn-outline" @click="generatePartialReport">生成阶段性报告</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { navigateToDiagnosisReport } from '@/utils/reportUtils'
import { uploadTongue, yoloDetect } from '@/api/detect'

const router = useRouter()
const route = useRoute()

// ── 状态 ──
const API_BASE = '/tongue'

const selectedFile = ref(null)
const previewUrl = ref('')
const selectedFiles = ref([])
const uploadPreviews = ref([])
const uploadResults = ref([])
const capturedFrames = ref([])
const captureResults = ref([])
const captureStep = ref(0)
const aggregatedResult = ref(null)
const totalCaptures = 4
const batchLoading = ref(false)

const mediaMode = ref('upload')
const statusText = ref('')
const loading = ref(false)
const result = ref(null)
const modelLoaded = ref(true)

const videoRef = ref(null)
const imageRef = ref(null)
const frozenFrameRef = ref(null)
const previewFrameRef = ref(null)
const cameraStream = ref(null)
const cameraRunning = ref(false)
const frozenFrameUrl = ref('')
const selectedRegionIndex = ref(null)
const displayMetrics = ref(null)

const patientInfo = ref({ id: null, idCard: '' })

// ── 计算属性 ──
const detections = computed(() => result.value?.detections || [])
const matchItems = computed(() => result.value?.annotation_match?.items || [])
const imageShape = computed(() => result.value?.image_shape || { width: 0, height: 0 })

const analysisReady = computed(() => Boolean(result.value?.annotation_match))
const mainConclusion = computed(() => result.value?.annotation_match?.summary || '等待检测结果')
const riskLevel = computed(() => result.value?.annotation_match?.risk_level || 'unknown')
const riskText = computed(() => ({ normal: '常规观察', observe: '建议观察', attention: '建议复核', unknown: '待确认' })[riskLevel] || '待确认')
const selectedDetection = computed(() => detections.value[selectedRegionIndex.value] || detections.value[0] || null)
const selectedMatch = computed(() => selectedDetection.value ? matchFor(selectedDetection.value) : null)

const scoreSummary = computed(() => {
  const raw = result.value?.scores || {}
  return Object.entries(raw).map(([name, value]) => {
    const mean = typeof value === 'object' ? Number(value?.mean ?? 0) : Number(value ?? 0)
    return { name, mean: Number.isFinite(mean) ? Math.max(0, Math.min(100, Math.round(mean))) : 0 }
  }).sort((a, b) => b.mean - a.mean)
})

// ── 工具函数 ──
const matchFor = (det) => matchItems.value.find((item) => item.source_label === det.class)
const fieldText = (item, keys) => {
  if (!item) return ''
  for (const k of keys) { const v = item[k]; if (v && String(v).trim()) return String(v).trim() }
  return ''
}

const requestJson = async (url, options = {}) => {
  const res = await fetch(url, options)
  const data = await res.json()
  if (!res.ok || data.success === false) throw new Error(data.error || data.msg || '请求失败')
  return data
}

// ── 检测框定位 ──
const updateDisplayMetrics = () => {
  const frame = previewFrameRef.value
  const el = imageRef.value || videoRef.value || frozenFrameRef.value
  if (!frame || !el) return
  const fr = frame.getBoundingClientRect()
  const er = el.getBoundingClientRect()
  displayMetrics.value = { frameRect: fr, mediaRect: er }
}

const imageDisplayRect = computed(() => {
  const m = displayMetrics.value
  const iw = imageShape.value.width, ih = imageShape.value.height
  if (!m || !iw || !ih) return null
  const cw = m.mediaRect.width, ch = m.mediaRect.height
  if (!cw || !ch) return null
  const scale = Math.min(cw / iw, ch / ih)
  return {
    scale, offsetX: (m.mediaRect.left - m.frameRect.left) + (cw - iw * scale) / 2,
    offsetY: (m.mediaRect.top - m.frameRect.top) + (ch - ih * scale) / 2,
  }
})

const boxStyle = (item) => {
  const rect = imageDisplayRect.value
  const [x1, y1, x2, y2] = item.bbox
  if (rect) return { left: `${rect.offsetX + x1 * rect.scale}px`, top: `${rect.offsetY + y1 * rect.scale}px`, width: `${(x2 - x1) * rect.scale}px`, height: `${(y2 - y1) * rect.scale}px`, '--box-color': item.color || '#d7ff36' }
  const cw = imageShape.value.width || 1, ch = imageShape.value.height || 1
  return { left: `${(x1 / cw) * 100}%`, top: `${(y1 / ch) * 100}%`, width: `${((x2 - x1) / cw) * 100}%`, height: `${((y2 - y1) / ch) * 100}%`, '--box-color': item.color || '#d7ff36' }
}

// ── 生命周期 ──
onMounted(() => {
  let qId = route.query.id || localStorage.getItem('current_patient_id')
  let qIdCard = route.query.idCard || localStorage.getItem('current_patient_idCard')
  patientInfo.value.id = qId; patientInfo.value.idCard = qIdCard
  localStorage.removeItem('wang_finished_id')
})

watch([mediaMode, previewUrl, frozenFrameUrl, result], async () => { await nextTick(); updateDisplayMetrics() })
onBeforeUnmount(() => { closeCamera(); if (previewUrl.value) URL.revokeObjectURL(previewUrl.value) })

// ── 文件上传 ──
const handleFileChange = (event) => {
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  if (files.length === 1) {
    selectedFile.value = files[0]; mediaMode.value = 'upload'; result.value = null
    uploadResults.value = []; statusText.value = `已选择：${files[0].name}`
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = URL.createObjectURL(files[0]); return
  }
  mediaMode.value = 'upload'; result.value = null; selectedFile.value = null
  selectedFiles.value = files; uploadPreviews.value = files.map(f => URL.createObjectURL(f))
  uploadResults.value = []; statusText.value = `已选择 ${files.length} 张图片`
}

const uploadAndDetect = async () => {
  // 单图
  if (selectedFile.value && !selectedFiles.value.length) {
    loading.value = true
    try {
      statusText.value = '正在检测...'
      const data = await yoloDetect(selectedFile.value)
      result.value = data.data || data
      // 确保数据格式统一
      if (result.value && !result.value.detections && result.value.yolo_detections) {
        result.value.detections = result.value.yolo_detections
      }
      selectedRegionIndex.value = result.value?.detections?.length ? 0 : null
      statusText.value = `完成：识别到 ${result.value?.detections?.length || 0} 个区域`
    } catch (err) { statusText.value = err.message } finally { loading.value = false }
    return
  }
  // 多图
  if (!selectedFiles.value.length) { statusText.value = '请先选择图片'; return }
  loading.value = true; uploadResults.value = []; aggregatedResult.value = null
  const results = []
  for (let i = 0; i < selectedFiles.value.length; i++) {
    try {
      statusText.value = `正在处理第 ${i + 1}/${selectedFiles.value.length} 张...`
      const data = await yoloDetect(selectedFiles.value[i])
      const rd = data.data || data
      if (rd && !rd.detections && rd.yolo_detections) rd.detections = rd.yolo_detections
      results.push({ result: rd, preview: uploadPreviews.value[i] })
    } catch (err) { results.push({ result: null, preview: uploadPreviews.value[i], error: err.message }) }
  }
  uploadResults.value = results
  if (results[0]?.result) { result.value = results[0].result; previewUrl.value = uploadPreviews.value[0]; selectedRegionIndex.value = results[0].result.detections?.length ? 0 : null }
  statusText.value = `完成：${results.length} 张检测完成`
  loading.value = false
}

const removeUploadFile = (index) => {
  URL.revokeObjectURL(uploadPreviews.value[index])
  uploadPreviews.value.splice(index, 1); selectedFiles.value.splice(index, 1)
  uploadResults.value.splice(index, 1)
  if (!selectedFiles.value.length) { statusText.value = '已清除'; result.value = null }
}
const clearUploads = () => {
  uploadPreviews.value.forEach(u => URL.revokeObjectURL(u))
  selectedFiles.value = []; uploadPreviews.value = []; uploadResults.value = []
  selectedFile.value = null; previewUrl.value = ''; result.value = null; statusText.value = ''
}

const selectUploadResult = (ur, idx) => {
  result.value = ur.result; previewUrl.value = ur.preview
  selectedRegionIndex.value = ur.result?.detections?.length ? 0 : null
}

// ── 摄像头 ──
const openCamera = async () => {
  stopLiveAnalysis()
  if (frozenFrameUrl.value) frozenFrameUrl.value = ''
  mediaMode.value = 'camera'; result.value = null
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 960 }, height: { ideal: 720 }, facingMode: 'user' }, audio: false })
    cameraStream.value = stream
    await nextTick()
    if (videoRef.value) { videoRef.value.srcObject = stream; await videoRef.value.play() }
    cameraRunning.value = true; statusText.value = `摄像头已打开，请依次捕获 ${totalCaptures} 张舌像`
  } catch (err) { statusText.value = `摄像头打开失败：${err.message}` }
}

const closeCamera = () => {
  stopLiveAnalysis(); frozenFrameUrl.value = ''
  if (cameraStream.value) cameraStream.value.getTracks().forEach(t => t.stop())
  cameraStream.value = null; cameraRunning.value = false; statusText.value = '摄像头已关闭'
}

const captureFrame = () => {
  const video = videoRef.value
  if (!video || !video.videoWidth) return ''
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth; canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  return canvas.toDataURL('image/jpeg', 0.86)
}

const captureSingleFrame = () => {
  if (!cameraRunning.value) return
  const image = captureFrame()
  if (!image) return
  capturedFrames.value.push({ index: captureStep.value, image })
  captureStep.value++
  if (captureStep.value >= totalCaptures) {
    closeCamera(); frozenFrameUrl.value = image
    statusText.value = `已捕获全部 ${totalCaptures} 张，点击"检测"查看结果`
  } else statusText.value = `第 ${captureStep.value} 张已捕获，请继续捕获第 ${captureStep.value + 1} 张`
}

const base64ToBlob = (b64) => {
  const parts = b64.split(',')
  const raw = atob(parts[1] || parts[0])
  const u8 = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) u8[i] = raw.charCodeAt(i)
  return new Blob([u8], { type: 'image/jpeg' })
}

const detectSingleFrame = async (image) => {
  const blob = base64ToBlob(image)
  const file = new File([blob], 'frame.jpg', { type: 'image/jpeg' })
  const data = await yoloDetect(file)
  const rd = data.data || data
  if (rd && !rd.detections && rd.yolo_detections) rd.detections = rd.yolo_detections
  return rd || { detections: [] }
}

const detectCaptures = async () => {
  const images = capturedFrames.value.map(f => f.image).filter(Boolean)
  if (!images.length) return
  batchLoading.value = true; captureResults.value = []; statusText.value = '正在检测各帧...'
  const results = []
  for (let i = 0; i < images.length; i++) {
    try {
      const rd = await detectSingleFrame(images[i])
      results.push({ index: i, result: { ...rd, preview: images[i] }, image: images[i] })
    } catch { results.push({ index: i, result: { detections: [] }, image: images[i] }) }
  }
  captureResults.value = results
  if (results[0]?.result) {
    result.value = results[0].result; frozenFrameUrl.value = images[0]
    selectedRegionIndex.value = results[0].result.detections?.length ? 0 : null
  }
  statusText.value = '各帧检测完成，点击缩略图查看每张结果'; batchLoading.value = false
}

const aggregateCaptures = async () => {
  const images = capturedFrames.value.map(f => f.image).filter(Boolean)
  if (images.length < 2) return
  batchLoading.value = true; statusText.value = '正在进行综合分析...'
  // 对所有帧的检测结果进行聚合：按 class_id 汇总，取平均置信度
  const allDets = captureResults.value.map(r => r.result?.detections || []).flat()
  const byClass = {}
  for (const d of allDets) {
    const cid = d.class_id
    if (!byClass[cid]) byClass[cid] = { ...d, confs: [d.confidence], count: 1 }
    else { byClass[cid].confs.push(d.confidence); byClass[cid].count++ }
  }
  const threshold = Math.ceil(images.length * 0.6)
  const aggregated = Object.values(byClass).filter(v => v.count >= threshold).map(v => ({
    ...v, confidence: round(v.confs.reduce((a, b) => a + b, 0) / v.confs.length, 3),
  }))
  delete aggregated.confs
  aggregatedResult.value = {
    detections: aggregated.map(({ confs, count, ...rest }) => ({
      ...rest, confidence: round(rest.confs.reduce((a, b) => a + b, 0) / rest.confs.length, 3)
    })),
    image_shape: result.value?.image_shape || {},
    annotation_match: { items: [], summary: `综合分析：${aggregated.length} 个区域（来自 ${images.length} 帧）`, risk_level: 'unknown' },
  }
  result.value = aggregatedResult.value
  selectedRegionIndex.value = aggregated.length ? 0 : null
  statusText.value = `综合分析完成：${aggregated.length} 个区域（聚合 ${images.length} 张）`
  batchLoading.value = false
}

const selectCaptureResult = (cr, idx) => {
  result.value = cr.result; frozenFrameUrl.value = cr.image
  selectedRegionIndex.value = cr.result?.detections?.length ? 0 : null
}
const clearCaptures = () => {
  capturedFrames.value = []; captureResults.value = []; captureStep.value = 0
  frozenFrameUrl.value = ''; result.value = null; statusText.value = '已清除'
}

const stopLiveAnalysis = () => {}

// ── 操作 ──
const goBack = () => { closeCamera(); localStorage.removeItem('wang_finished_id'); router.push('/detect') }

const confirmAndSave = async () => {
  if (!result.value) { ElMessage.warning('请先完成舌象检测'); return }
  const pid = patientInfo.value.id || localStorage.getItem('current_patient_id')
  const icard = patientInfo.value.idCard || localStorage.getItem('current_patient_idcard')
  const diagnosisId = route.query.caseId || localStorage.getItem('current_case_id')
  if (!pid) { ElMessage.error('未获取到当前病人ID'); return }

  try {
    // 用第一帧或上传的图片保存到 Java 后端
    const imageData = frozenFrameUrl.value || previewUrl.value
    if (!imageData) { ElMessage.error('缺少图片数据'); return }
    const blob = await (await fetch(imageData)).blob()
    const fd = new FormData()
    fd.append('file', blob, 'tongue.jpg')
    fd.append('id', pid)
    if (icard) fd.append('idCard', icard)
    if (diagnosisId) fd.append('diagnosisId', diagnosisId)

    const res = await uploadTongue(fd)
    if (res.data.code === 200 || res.data.success) {
      localStorage.setItem('wang_finished_id', String(pid))
      ElMessage.success('诊断已保存')
      router.push('/detect')
    } else throw new Error(res.data.msg || '保存失败')
  } catch (err) { ElMessage.error(err.message || '保存失败') }
}

const resetAll = () => {
  result.value = null; aggregatedResult.value = null
  previewUrl.value = ''; frozenFrameUrl.value = ''
  clearCaptures(); clearUploads()
  closeCamera()
}
const generatePartialReport = () => { navigateToDiagnosisReport(router, { patientId: patientInfo.value.id, completedTypes: 'wang', focusMode: 'wang' }) }

const round = (v, d) => Math.round(v * Math.pow(10, d)) / Math.pow(10, d)
</script>

<style scoped>
/* ── 全局 ── */
.wang-page { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1a1a2e; background: #f5f6fa; min-height: 100vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.section { padding: 40px 0; }
.section-alt { background: #fff; }
.section-header { text-align: center; margin-bottom: 32px; }
.eyebrow { font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #8b3d1a; margin: 0 0 8px; }
.section-title { font-size: 26px; font-weight: 700; margin: 0 0 8px; }
.section-subtitle { color: #666; font-size: 14px; margin: 0; }

/* ── Hero ── */
.hero { padding: 40px 0; }
.hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; align-items: start; }
@media (max-width: 900px) { .hero-grid { grid-template-columns: 1fr; } }
.nav-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.hero-title { font-size: 28px; font-weight: 800; line-height: 1.3; margin: 0 0 12px; }
.hero-subtitle { font-size: 14px; color: #666; line-height: 1.6; margin: 0 0 24px; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
.upload-status { font-size: 13px; color: #888; margin: 0 0 16px; }

/* ── 按钮 ── */
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 8px; border: 1px solid #ddd; background: #fff; color: #333; font-size: 14px; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn:hover { border-color: #8b3d1a; color: #8b3d1a; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #8b3d1a; color: #fff; border-color: #8b3d1a; }
.btn-primary:hover { background: #a04e28; color: #fff; }
.btn-outline { background: transparent; border-color: #8b3d1a; color: #8b3d1a; }
.btn-file { position: relative; overflow: hidden; }
.btn-file input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

/* ── 多图预览 ── */
.multi-preview { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.multi-thumb { position: relative; width: 72px; height: 72px; border-radius: 8px; overflow: hidden; cursor: pointer; border: 2px solid transparent; transition: border 0.15s; }
.multi-thumb.active { border-color: #8b3d1a; }
.multi-thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-remove { position: absolute; top: 2px; right: 2px; width: 18px; height: 18px; border-radius: 50%; background: rgba(0,0,0,0.6); color: #fff; border: none; font-size: 12px; line-height: 18px; text-align: center; cursor: pointer; padding: 0; }
.thumb-badge { position: absolute; bottom: 2px; left: 2px; background: rgba(0,0,0,0.6); color: #fff; font-size: 10px; padding: 1px 5px; border-radius: 4px; }
.thumb-dets { position: absolute; bottom: 2px; right: 2px; background: rgba(139,61,26,0.85); color: #fff; font-size: 9px; padding: 1px 5px; border-radius: 4px; }
.thumb-count { position: absolute; bottom: 2px; right: 2px; background: #333; color: #fff; font-size: 9px; padding: 1px 5px; border-radius: 4px; }

/* ── Meta 卡片 ── */
.hero-meta { display: flex; gap: 12px; flex-wrap: wrap; }
.meta-card { background: #f8f9fa; border-radius: 12px; padding: 14px 18px; flex: 1; min-width: 100px; }
.meta-label { font-size: 11px; color: #999; margin: 0 0 2px; }
.meta-value { font-size: 24px; font-weight: 700; color: #1a1a2e; margin: 0; }
.meta-value.normal { color: #52c41a; }
.meta-value.observe { color: #faad14; }
.meta-value.attention { color: #ff4d4f; }
.meta-desc { font-size: 11px; color: #bbb; margin: 0; }

/* ── 预览卡片 ── */
.preview-card { background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.preview-frame { position: relative; width: 100%; min-height: 360px; background: #000; display: flex; align-items: center; justify-content: center; }
.preview-frame img, .preview-frame video { max-width: 100%; max-height: 500px; display: block; }
.preview-frame.live { min-height: 400px; }
.frozen-frame { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }
.empty-preview { color: #666; font-size: 14px; text-align: center; padding: 100px 20px; }

/* ── 检测框 ── */
.box-layer { position: absolute; inset: 0; pointer-events: none; }
.box-layer .detect-box { pointer-events: auto; position: absolute; border: 2px solid var(--box-color, #d7ff36); border-radius: 4px; background: transparent; cursor: pointer; padding: 0; transition: all 0.15s; }
.box-layer .detect-box:hover, .box-layer .detect-box.active { background: color-mix(in srgb, var(--box-color) 12%, transparent); border-width: 3px; z-index: 10; }
.box-corner { position: absolute; top: -10px; left: -10px; width: 20px; height: 20px; background: var(--box-color, #d7ff36); color: #000; border-radius: 50%; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; }

/* ── 图例 ── */
.overlay-legend { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 16px; background: #f8f9fa; }
.overlay-legend b { display: inline-block; width: 18px; height: 18px; border-radius: 50%; color: #000; font-size: 10px; text-align: center; line-height: 18px; margin-right: 3px; }
.detection-meta { display: flex; gap: 8px; padding: 8px 16px; background: #fff; border-top: 1px solid #eee; flex-wrap: wrap; }
.status-pill { font-size: 12px; padding: 3px 10px; border-radius: 12px; background: #f0f0f0; color: #666; }
.status-pill.success { background: #f6ffed; color: #52c41a; }
.status-pill.danger { background: #fff2f0; color: #ff4d4f; }
.status-pill.warn { background: #fffbe6; color: #faad14; }

/* ── 摄像头 ── */
.capture-actions { display: flex; gap: 8px; padding: 12px 16px; align-items: center; flex-wrap: wrap; }
.capture-hint { font-size: 12px; color: #888; }
.capture-thumbs { display: flex; gap: 6px; padding: 8px 16px 16px; flex-wrap: wrap; }
.capture-thumb { width: 64px; height: 64px; border-radius: 8px; overflow: hidden; position: relative; cursor: pointer; border: 2px solid transparent; }
.capture-thumb.active { border-color: #8b3d1a; }
.capture-thumb img { width: 100%; height: 100%; object-fit: cover; }

/* ── 结果区 ── */
.result-grid { display: grid; grid-template-columns: 7fr 5fr; gap: 20px; margin-bottom: 20px; }
@media (max-width: 768px) { .result-grid { grid-template-columns: 1fr; } }
.card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 1px 8px rgba(0,0,0,0.04); }
.card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.card-header h3 { font-size: 16px; font-weight: 600; margin: 0; }
.tag { font-size: 11px; color: #999; background: #f0f0f0; padding: 2px 8px; border-radius: 4px; }
.region-list { display: flex; flex-direction: column; gap: 8px; }
.region-card { display: flex; gap: 12px; padding: 12px; border-radius: 12px; border: 2px solid transparent; cursor: default; transition: all 0.15s; }
.region-card.active, .region-card:hover { border-color: #8b3d1a; background: #faf6f3; }
.region-index { width: 28px; height: 28px; border-radius: 50%; color: #000; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.region-body { flex: 1; min-width: 0; }
.region-body h4 { margin: 0 0 4px; font-size: 14px; font-weight: 600; }
.region-body h4 span { font-weight: 400; color: #999; font-size: 11px; }
.region-body p { margin: 2px 0; font-size: 12px; color: #555; line-height: 1.4; }
.region-body small { font-size: 11px; color: #888; }
.empty-state { color: #999; text-align: center; padding: 40px 0; }

/* ── 摘要 ── */
.summary-card h3 { font-size: 15px; margin: 0 0 12px; }
.tip-list { list-style: none; padding: 0; margin: 0; }
.tip-item { padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.tip-item:last-child { border: none; }
.tip-item strong { display: block; font-size: 13px; margin-bottom: 2px; }
.tip-item p { margin: 0; font-size: 12px; color: #888; }

/* ── 雷达图 ── */
.radar-card { margin-bottom: 20px; }
.radar-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: center; }
@media (max-width: 768px) { .radar-layout { grid-template-columns: 1fr; } }
.radar-box { text-align: center; }
.radar-img { max-width: 260px; max-height: 260px; }
.score-grid { display: flex; flex-direction: column; gap: 12px; }
.score-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
.score-row .k { font-size: 13px; color: #555; }
.score-row .v { font-size: 15px; font-weight: 700; color: #8b3d1a; }

/* ── 底部 ── */
.footer-actions { text-align: center; }
.disclaimer { font-size: 12px; color: #999; margin: 0 0 16px; }
.disclaimer .warning { color: #e6a23c; }
.btn-row { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
</style>
