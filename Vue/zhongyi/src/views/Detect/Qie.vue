<template>
  <div class="qie-container">
    <div class="header-bar">
      <div class="left-info">
        <el-button circle :icon="Back" @click="router.back()" class="back-btn" />
        <span class="page-title">中医智能脉诊 (Pulse Diagnosis)</span>
      </div>
      <div class="patient-card" v-if="patientId">
        <el-icon><User /></el-icon>
        <span class="label">当前就诊:</span>
        <span class="value">ID: {{ patientId }}</span>
        <el-tag size="small" effect="dark" type="success" class="ml-2">已实名认证</el-tag>
      </div>
    </div>

    <div class="main-content">
      <div class="control-panel">
        
        <div class="status-monitor">
          
          <div class="monitor-item">
            <span class="label">平均心率 (BPM)</span>
            <div class="value-display">
              <div v-if="isMeasuring" class="measuring-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span class="anim-text">采集分析中...</span>
              </div>
              <div v-else-if="analysisResult" class="result-state">
                <span class="number">{{ analysisResult.avg_hr }}</span>
                <el-tag type="danger" effect="plain" class="ml-2">最终读数</el-tag>
              </div>
              <div v-else class="idle-state">--</div>
            </div>
          </div>
          
          <div class="monitor-item">
            <span class="label">血氧饱和度 (%)</span>
            <div class="value-display">
              <div v-if="isMeasuring" class="measuring-state">
                <el-progress :percentage="measuringProgress" :show-text="false" class="mini-progress"/>
              </div>
              <div v-else-if="analysisResult" class="result-state">
                <span class="number blue">{{ analysisResult.avg_spo2 }}</span>
              </div>
              <div v-else class="idle-state">--</div>
            </div>
          </div>

          <div class="monitor-item signal-box">
            <div class="flex-between">
              <span class="label">传感器接触质量</span>
              <span class="signal-val" :class="signalStatusClass">{{ signalText }}</span>
            </div>
            <el-progress 
              :percentage="signalQuality * 100" 
              :status="signalStatus"
              :stroke-width="10"
              :show-text="false"
            />
          </div>
        </div>

        <transition name="el-zoom-in-top">
          <div class="tcm-card" v-if="analysisResult && !isMeasuring">
            <div class="card-header">
              <el-icon><Reading /></el-icon>
              <span>中医脉象辨证报告</span>
            </div>
            <div class="card-content">
              <div class="tcm-text">{{ analysisResult.suggestion }}</div>
              <el-collapse style="margin-top: 16px;">
                <el-collapse-item title="📖 参考文献与出处" name="1">
                  <div class="ref-list">
                    <div v-for="(ref, idx) in qieReferences" :key="idx" class="ref-item">
                      <span class="ref-authors">{{ ref.authors }} ({{ ref.year }})</span>
                      <p class="ref-desc">{{ ref.title }}</p>
                      <a v-if="ref.url" :href="ref.url" target="_blank" class="ref-link">
                        查看 → {{ ref.source }}
                      </a>
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </transition>

        <div class="action-area">
          <div class="instruction-text" v-if="!isMeasuring && !analysisResult">
            <el-icon><InfoFilled /></el-icon>
            请嘱咐患者将手指平稳放置，保持静止，点击开始。
          </div>
          
          <div class="button-group">
            <el-button 
              v-if="!isMeasuring && !analysisResult"
              type="primary" 
              size="large" 
              :loading="isStarting"
              @click="startDiagnosis"
              class="action-btn start-btn"
            >
              <el-icon class="mr-1"><VideoPlay /></el-icon> 开始切诊
            </el-button>

            <el-button 
              v-if="isMeasuring"
              type="warning" 
              size="large" 
              :loading="isAnalyzing"
              :disabled="countdown > 0"
              @click="stopAndAnalyze"
              class="action-btn stop-btn"
            >
              <el-icon class="mr-1"><DataAnalysis /></el-icon> 
              <span v-if="countdown > 0">稳定采集中: {{ countdown }}s (请保持平稳)</span>
              <span v-else>结束采集并生成报告</span>
            </el-button>

            <div v-if="analysisResult && !isMeasuring" class="result-btns">
              <el-button 
                type="success" 
                size="large" 
                :loading="isSaving"
                @click="saveToRecord"
                class="flex-1"
              >
                <el-icon class="mr-1"><Check /></el-icon> 确认入库
              </el-button>

              <el-button
                type="primary"
                size="large"
                :loading="isSavingReport"
                @click="saveToRecordAndGoReport"
                class="flex-1"
              >
                生成报告
              </el-button>
              
              <el-button 
                type="info" 
                size="large" 
                @click="resetMeasurement"
                class="flex-1"
              >
                <el-icon class="mr-1"><RefreshRight /></el-icon> 重新测量
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-panel">
        <div class="chart-header">
          <span class="chart-title">实时脉搏波形图 (PPG Waveform)</span>
          <div class="live-indicator" v-if="isMeasuring">
            <span class="dot"></span> LIVE Monitoring
          </div>
        </div>
        <div ref="chartRef" class="echarts-box"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Back, User, VideoPlay, DataAnalysis, Check, RefreshRight, InfoFilled, Loading, Reading } from '@element-plus/icons-vue';
import axios from 'axios';
import * as echarts from 'echarts';
import { navigateToDiagnosisReport } from '@/utils/reportUtils';
import { algorithmReferences } from '@/constants/algorithmReferences';

// ===== 1. 基础状态 =====
const route = useRoute();
const router = useRouter();
const patientId = ref(route.query.id || '');
const qieReferences = ref(algorithmReferences.qie.references);

// 流程控制状态
const isStarting = ref(false);    // 启动中
const isMeasuring = ref(false);   // 测量进行中
const isAnalyzing = ref(false);   // Python分析中
const isSaving = ref(false);      // Java入库中
const isSavingReport = ref(false); // 入库并跳转报告

// 倒计时状态
const countdown = ref(60);
let countdownTimer = null;

// 结果数据 (仅在测量结束后赋值)
const analysisResult = ref(null); 

// 实时信号 (仅用于波形和质量条，不用于数值显示)
const signalQuality = ref(0);
const measuringProgress = ref(0); // 假进度条动画

// 信号质量计算属性
const signalStatus = computed(() => {
  if (signalQuality.value > 0.8) return 'success';
  if (signalQuality.value > 0.4) return 'warning';
  return 'exception';
});
const signalStatusClass = computed(() => {
  if (signalQuality.value > 0.8) return 'text-success';
  if (signalQuality.value > 0.4) return 'text-warning';
  return 'text-danger';
});
const signalText = computed(() => {
  if (signalQuality.value > 0.8) return '信号优良';
  if (signalQuality.value > 0.4) return '信号一般';
  return '未检测到手指 / 干扰';
});

// ===== 2. 图表平滑渲染逻辑 =====
const chartRef = ref(null);
let myChart = null;
const waveBuffer = ref([]);       // Echarts使用的数组
let renderQueue = [];             // 缓冲队列
const MAX_DISPLAY_POINTS = 500;   // 显示窗口
let animationId = null;

const initChart = () => {
  if (!chartRef.value) return;
  myChart = echarts.init(chartRef.value);
  myChart.setOption({
    backgroundColor: '#fff',
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', show: false, boundaryGap: false },
    yAxis: { type: 'value', scale: true, splitLine: { show: true, lineStyle: { color: '#f0f0f0' } } },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#4facfe' }, { offset: 1, color: '#00f2fe' }
        ]),
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 242, 254, 0.3)' }, { offset: 1, color: 'rgba(0, 242, 254, 0.05)' }
        ])
      },
      data: []
    }],
    animation: false
  });
  window.addEventListener('resize', () => myChart?.resize());
};

let lastDisplayValue = 0; // 用于EMA平滑滤波的基准值

const smoothRender = () => {
  if (renderQueue.length > 0) {
    const points = renderQueue.splice(0, 2); 
    
    // 视觉逐渐稳定算法 (动态指数移动平均 EMA)
    points.forEach(rawVal => {
      let alpha = 1.0; // 平滑系数 (1.0表示不平滑，数值越小越平滑)
      
      if (isMeasuring.value) {
        // 根据经过的时间计算平滑度：前15秒从1.0渐变到0.15，视觉上呈现从剧烈到平稳的"沉心静气"过程
        const elapsed = 60 - countdown.value; 
        alpha = Math.max(0.15, 1.0 - (elapsed / 15) * 0.85); 
      }

      if (waveBuffer.value.length === 0) {
        lastDisplayValue = rawVal;
      } else {
        lastDisplayValue = alpha * rawVal + (1 - alpha) * lastDisplayValue;
      }
      
      waveBuffer.value.push(lastDisplayValue);
    });

    if (waveBuffer.value.length > MAX_DISPLAY_POINTS) {
      waveBuffer.value.splice(0, points.length);
    }
    if (myChart) myChart.setOption({ series: [{ data: waveBuffer.value }] });
  }
  animationId = requestAnimationFrame(smoothRender);
};

// ===== 3. WebSocket =====
let ws = null;
let progressTimer = null;

const connectWS = () => {
  ws = new WebSocket('ws://localhost:8000/ws/pulse');
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.wave) renderQueue.push(...data.wave);
      signalQuality.value = data.q || 0;
    } catch (e) { console.error(e); }
  };
};

const startProgressAnim = () => {
  measuringProgress.value = 0;
  progressTimer = setInterval(() => {
    if (measuringProgress.value < 90) measuringProgress.value += 1;
    else measuringProgress.value = 0;
  }, 100);
};

// 启动60秒倒计时
const startCountdown = () => {
  countdown.value = 60;
  clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      clearInterval(countdownTimer);
    }
  }, 1000);
};

// ===== 4. 业务逻辑 =====

// A. 开始测量
const startDiagnosis = async () => {
  if (!patientId.value) return ElMessage.warning('无患者ID');
  
  isStarting.value = true;
  try {
    await axios.post('http://localhost:8000/api/pulse/start');
    
    // 重置状态
    analysisResult.value = null;
    waveBuffer.value = [];
    renderQueue = [];
    isMeasuring.value = true;
    lastDisplayValue = 0; // 重置滤波基准
    
    startProgressAnim();
    startCountdown(); // 开启60秒强制倒计时
    
    ElMessage.success('设备已启动，请保持静止60秒...');
  } catch (e) {
    ElMessage.error('启动失败，请检查Python后端');
  } finally {
    isStarting.value = false;
  }
};

// B. 结束并分析
const stopAndAnalyze = async () => {
  try {
    isAnalyzing.value = true;
    
    const pyRes = await axios.post('http://localhost:8000/api/pulse/stop', null, {
      params: { user_id: patientId.value }
    });
    
    const report = pyRes.data;
    
    if (report.code !== 200 || report.avg_hr === 0) {
      ElMessage.warning(report.msg || "数据不足，请重测");
      resetMeasurement(); 
      return;
    }

    isMeasuring.value = false;
    clearInterval(progressTimer);
    clearInterval(countdownTimer); // 安全清理
    
    analysisResult.value = {
      avg_hr: report.avg_hr,
      avg_spo2: report.avg_spo2,
      suggestion: report.suggestion,
      valid_rate: report.valid_rate,
      sample_count: report.sample_count,
      raw_wave: JSON.stringify(waveBuffer.value.slice(-300)) 
    };
    
    ElMessage.success("分析完成，请查看报告");

  } catch (e) {
    ElMessage.error("分析失败：" + e.message);
    isMeasuring.value = false;
    clearInterval(countdownTimer); // 安全清理
  } finally {
    isAnalyzing.value = false;
  }
};

async function persistQieToServer() {
  const diagnosisId = route.query.caseId || localStorage.getItem('current_case_id')
  const payload = {
    userId: patientId.value,
    diagnosisId: diagnosisId ? Number(diagnosisId) : null,
    heartRate: analysisResult.value.avg_hr,
    spo2: analysisResult.value.avg_spo2,
    validRate: analysisResult.value.valid_rate,
    sampleCount: analysisResult.value.sample_count,
    tcmSuggestion: analysisResult.value.suggestion,
    rawData: analysisResult.value.raw_wave
  };
  const javaRes = await axios.post('http://localhost:8080/api/detect/qie/save', payload);
  if (javaRes.data.code !== 200) {
    throw new Error(javaRes.data.msg);
  }
  localStorage.setItem('qie_finished_id', String(patientId.value));
}

// C. 确认入库
const saveToRecord = async () => {
  if (!analysisResult.value) return;

  isSaving.value = true;
  try {
    await persistQieToServer();
    ElMessage.success('数据已归档！');
    router.push('/detect');
  } catch (e) {
    ElMessage.error('入库失败：' + e.message);
  } finally {
    isSaving.value = false;
  }
};

const saveToRecordAndGoReport = async () => {
  if (!analysisResult.value) return;

  isSavingReport.value = true;
  try {
    await persistQieToServer();
    ElMessage.success('已归档，正在打开报告…');
    navigateToDiagnosisReport(router, patientId.value, '');
  } catch (e) {
    ElMessage.error('入库失败：' + e.message);
  } finally {
    isSavingReport.value = false;
  }
};

// D. 重新测量
const resetMeasurement = () => {
  analysisResult.value = null;
  isMeasuring.value = false;
  waveBuffer.value = [];
  renderQueue = [];
  countdown.value = 60;
  clearInterval(progressTimer);
  clearInterval(countdownTimer);
};

// ===== 生命周期 =====
onMounted(() => {
  if (!patientId.value) {
    ElMessage.error('缺少患者信息');
    setTimeout(() => router.push('/detect'), 1500);
    return;
  }
  nextTick(() => {
    initChart();
    connectWS();
    smoothRender();
  });
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  clearInterval(progressTimer);
  clearInterval(countdownTimer);
  ws?.close();
  myChart?.dispose();
});
</script>

<style scoped>
/* ── 与主系统统一的暖棕色调 ── */
.qie-container {
  height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  display: flex; flex-direction: column;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

/* 页头 */
.header-bar {
  height: 60px;
  background: linear-gradient(180deg, #6b2d12 0%, #8b3d1a 100%);
  border-bottom: 2px solid #c8a020;
  box-shadow: 0 2px 12px rgba(60,20,0,.25);
  display: flex; justify-content: space-between; align-items: center; padding: 0 24px;
}
.page-title { font-size: 17px; font-weight: 600; margin-left: 12px; color: #fdeabb; letter-spacing: 1px; }
.patient-card {
  background: rgba(200,160,32,.15); padding: 5px 16px; border-radius: 20px;
  color: #fdeabb; font-size: 13px; font-weight: bold;
  border: 1px solid rgba(200,160,32,.3);
  display: flex; align-items: center; gap: 8px;
}

.main-content { flex: 1; display: flex; padding: 20px; gap: 20px; overflow: hidden; }

.control-panel { width: 400px; display: flex; flex-direction: column; gap: 18px; overflow-y: auto; }

/* 状态监控区 */
.status-monitor {
  background: rgba(255,252,242,.92);
  border-radius: 10px; padding: 22px;
  border: 1px solid #c8a96e;
  box-shadow: 0 3px 12px rgba(100,60,10,.08);
  display: flex; flex-direction: column; gap: 18px;
}

.monitor-item .label { color: #8b6030; font-size: 13px; margin-bottom: 8px; display: block; }

.value-display { height: 50px; display: flex; align-items: center; }

/* 测量中 */
.measuring-state { display: flex; align-items: center; gap: 10px; color: #8b3d1a; }
.anim-text { font-size: 15px; font-weight: 500; animation: blink 1.5s infinite; }
.mini-progress { width: 150px; }

/* 结果 */
.result-state .number { font-size: 40px; font-weight: bold; color: #3d2b10; line-height: 1; }
.result-state .number.blue { color: #4a7060; }

/* 空闲 */
.idle-state { font-size: 32px; color: #d4b483; font-weight: bold; }

/* 信号质量 */
.flex-between { display: flex; justify-content: space-between; margin-bottom: 6px; }
.signal-val { font-size: 12px; }
.text-success { color: #4a7060; }
.text-warning { color: #c8a020; }
.text-danger  { color: #c0392b; }

/* 中医脉象卡片 */
.tcm-card {
  background: linear-gradient(135deg, #fdf8ef 0%, #faf3e0 100%);
  border: 1px solid #c8a96e; border-radius: 10px; padding: 18px;
  box-shadow: 0 3px 12px rgba(100,60,10,.08);
}
.card-header {
  display: flex; align-items: center; gap: 8px;
  color: #8b3d1a; font-weight: bold; font-size: 15px;
  margin-bottom: 12px; border-bottom: 1px dashed #e8d5a0; padding-bottom: 10px;
}
.tcm-text {
  font-size: 14px; line-height: 1.9; color: #5a2d00;
  white-space: pre-wrap;
  font-family: 'KaiTi', 'SimKai', serif;
}

/* 按钮操作区 */
.action-area {
  background: rgba(255,252,242,.92);
  border-radius: 10px; padding: 22px;
  border: 1px solid #c8a96e;
  box-shadow: 0 3px 12px rgba(100,60,10,.08);
  margin-top: auto;
}
.instruction-text {
  background: #faf3e0; color: #8b6030;
  padding: 10px; border-radius: 6px; border: 1px solid #e8d5a0;
  font-size: 13px; margin-bottom: 14px;
  display: flex; align-items: center; gap: 6px;
}
.button-group { display: flex; flex-direction: column; gap: 12px; }
.action-btn { height: 46px; font-size: 15px; width: 100%; border-radius: 6px; }
.result-btns { display: flex; flex-wrap: wrap; gap: 12px; }
.flex-1 { flex: 1; }

/* 右侧图表面板 */
.chart-panel {
  flex: 1; background: rgba(255,252,242,.92);
  border-radius: 10px; border: 1px solid #c8a96e;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 3px 12px rgba(100,60,10,.08);
}
.chart-header {
  height: 50px; border-bottom: 1px solid #e8d5a0;
  display: flex; justify-content: space-between; align-items: center; padding: 0 20px;
  background: linear-gradient(180deg, #f5e4a8 0%, #ebd07a 100%);
}
.chart-title { font-weight: 700; color: #5a2d00; font-size: 14px; }
.live-indicator { color: #c0392b; font-weight: bold; font-size: 12px; display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; background: #c0392b; border-radius: 50%; animation: blink 1s infinite; }
.echarts-box { flex: 1; width: 100%; }

@keyframes blink { 0% { opacity: 1; } 50% { opacity: .4; } 100% { opacity: 1; } }

.reference-note {
  font-size: 12px; color: #5d7a8a; line-height: 1.6;
  background: #f0f4ff; padding: 8px 12px; border-radius: 6px;
  border-left: 3px solid #5d9cec; text-align: left;
}

.reference-section {
  margin-top: 12px; padding: 10px; background: #f0f4ff;
  border: 1px solid #d0e0ff; border-radius: 6px;
}

.ref-title {
  font-size: 12px; font-weight: 600; color: #333;
  margin: 0 0 8px 0;
}

.ref-list {
  display: flex; flex-direction: column; gap: 8px;
}

.ref-item {
  padding: 8px; background: #fff;
  border-left: 2px solid #5d9cec; border-radius: 3px;
  font-size: 11px;
}

.ref-authors {
  display: block; color: #666; font-weight: 600;
  margin-bottom: 3px;
}

.ref-desc {
  margin: 3px 0; color: #666; line-height: 1.4;
}

.ref-link {
  display: inline-block; color: #5d9cec; text-decoration: none;
  font-size: 10px; margin-top: 3px;
  transition: all 0.2s;
}

.ref-link:hover {
  color: #1890ff; text-decoration: underline;
}
</style>