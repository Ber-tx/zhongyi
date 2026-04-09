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
      <!-- ======= 左侧控制面板 ======= -->
      <div class="control-panel">

        <!-- 状态监控 -->
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

        <!-- 倒计时进度条（测量中） -->
        <transition name="el-zoom-in-top">
          <div class="countdown-card" v-if="isMeasuring">
            <div class="countdown-header">
              <el-icon><Timer /></el-icon>
              <span>采集进度 — 请保持手指静止</span>
            </div>
            <el-progress
              :percentage="Math.round(((60 - countdown) / 60) * 100)"
              :stroke-width="14"
              status="success"
              class="countdown-progress"
            />
            <div class="countdown-text">
              <span v-if="countdown > 0">还需 <b>{{ countdown }}</b> 秒自动完成分析</span>
              <span v-else class="auto-analyzing">⚙️ 正在自动生成报告...</span>
            </div>
          </div>
        </transition>

        <!-- 中医脉象辨证报告 -->
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

        <!-- 操作区 -->
        <div class="action-area">
          <div class="instruction-text" v-if="!isMeasuring && !analysisResult">
            <el-icon><InfoFilled /></el-icon>
            请嘱咐患者将手指平稳放置于传感器，保持静止，点击开始采集。
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
              <span v-if="countdown > 0">稳定采集中: {{ countdown }}s</span>
              <span v-else>立即结束采集</span>
            </el-button>

            <div v-if="analysisResult && !isMeasuring" class="result-btns">
              <el-button type="success" size="large" :loading="isSaving" @click="saveToRecord" class="flex-1">
                <el-icon class="mr-1"><Check /></el-icon> 确认并返回
              </el-button>
              <el-button type="primary" size="large" :loading="isSavingReport" @click="saveToRecordAndGoReport" class="flex-1">
                生成阶段性报告
              </el-button>
              <el-button type="info" size="large" @click="resetMeasurement" class="flex-1">
                <el-icon class="mr-1"><RefreshRight /></el-icon> 重新测量
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- ======= 右侧波形区 ======= -->
      <div class="chart-panel">
        <!-- 图表头 -->
        <div class="chart-header">
          <div class="chart-title-group">
            <span class="chart-title">PPG 实时脉搏波形</span>
            <span class="chart-subtitle">光电容积脉搏波 (Photoplethysmography)</span>
          </div>
          <div class="chart-meta">
            <span class="sampling-badge">采样率 50 Hz</span>
            <div class="live-indicator" v-if="isMeasuring">
              <span class="dot"></span> LIVE
            </div>
          </div>
        </div>

        <!-- ECharts 区域 -->
        <div ref="chartRef" class="echarts-box"></div>

        <!-- PPG 科普说明条 -->
        <div class="ppg-legend-bar">
          <div class="legend-item">
            <span class="legend-icon peak-icon">▲</span>
            <div class="legend-text">
              <b>波峰</b>
              <span>心脏收缩，血液涌入指尖，光吸收最强</span>
            </div>
          </div>
          <div class="legend-divider"></div>
          <div class="legend-item">
            <span class="legend-icon trough-icon">▼</span>
            <div class="legend-text">
              <b>波谷</b>
              <span>心脏舒张，血液回流，光吸收最弱</span>
            </div>
          </div>
          <div class="legend-divider"></div>
          <div class="legend-item">
            <span class="legend-icon interval-icon">↔</span>
            <div class="legend-text">
              <b>峰间距</b>
              <span>两次心跳间隔，间隔均匀 = 节律稳定</span>
            </div>
          </div>
          <div class="legend-divider"></div>
          <div class="legend-item">
            <span class="legend-icon amp-icon">↕</span>
            <div class="legend-text">
              <b>波幅</b>
              <span>峰谷高度差 = 指尖血流灌注强度</span>
            </div>
          </div>
        </div>

        <!-- 空闲状态引导 -->
        <transition name="el-fade-in">
          <div class="chart-idle-overlay" v-if="!isMeasuring && waveBuffer.length === 0">
            <div class="idle-illustration">
              <svg viewBox="0 0 400 80" class="idle-wave-svg">
                <path d="M0,40 Q25,40 30,40 Q35,40 40,15 Q45,0 50,40 Q55,65 60,80 Q65,80 70,50 Q75,20 80,40
                         Q105,40 110,40 Q115,40 120,15 Q125,0 130,40 Q135,65 140,80 Q145,80 150,50 Q155,20 160,40
                         Q185,40 190,40 Q195,40 200,15 Q205,0 210,40 Q215,65 220,80 Q225,80 230,50 Q235,20 240,40
                         Q265,40 270,40 Q275,40 280,15 Q285,0 290,40 Q295,65 300,80 Q305,80 310,50 Q315,20 320,40
                         Q345,40 350,40 Q355,40 360,15 Q365,0 370,40 Q375,65 380,80 Q385,80 390,50 Q395,20 400,40"
                      fill="none" stroke="#c8a96e" stroke-width="2.5" stroke-dasharray="6,4" opacity="0.5"/>
              </svg>
              <p class="idle-hint">点击「开始切诊」后，实时脉搏波形将在此显示</p>
              <p class="idle-sub">波形呈现示波器风格，可直观观察每次心跳的血流变化</p>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import {
  Back, User, VideoPlay, DataAnalysis, Check, RefreshRight,
  InfoFilled, Loading, Reading, Timer
} from '@element-plus/icons-vue';
import axios from 'axios';
import * as echarts from 'echarts';
import { navigateToDiagnosisReport } from '@/utils/reportUtils';
import { algorithmReferences } from '@/constants/algorithmReferences';

// =====================================================================
// 1. 基础状态
// =====================================================================
const route = useRoute();
const router = useRouter();
const patientId = ref(route.query.id || '');
const qieReferences = ref(algorithmReferences.qie.references);

const isStarting   = ref(false);
const isMeasuring  = ref(false);
const isAnalyzing  = ref(false);
const isSaving     = ref(false);
const isSavingReport = ref(false);

const countdown        = ref(60);
let   countdownTimer   = null;

const analysisResult   = ref(null);
const signalQuality    = ref(0);
const measuringProgress = ref(0);

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

// =====================================================================
// 2. 倒计时自动分析
//    countdown 归零时若仍在测量，自动触发 stopAndAnalyze()
// =====================================================================
watch(countdown, (val) => {
  if (val === 0 && isMeasuring.value && !isAnalyzing.value) {
    stopAndAnalyze();
  }
});

// =====================================================================
// 3. 示波器渲染核心
//
//  时序匹配说明：
//    · Python 采样率   50 Hz → 50 pts/s
//    · WebSocket 推送  25 Hz，每包 2 点 → 50 pts/s（完全匹配）
//    · requestAnimationFrame ≈ 60 fps
//    · 每帧应消耗 50/60 ≈ 0.833 个点 ← 用分数累加器精确控制
//    · 不再使用 EMA 平滑，保留原始波形（示波器风格）
//    · 显示窗口 300 点 = 6 秒（通过缩短横轴时间窗，让实时波形视觉拉长）
//    · X 轴每 50 点标注 1 秒刻度
// =====================================================================
const SAMPLE_RATE      = 50;          // Hz，与 Python 一致
const DISPLAY_SECONDS  = 6;           // 横轴显示 6 秒（原为 8 秒）
const DISPLAY_POINTS   = SAMPLE_RATE * DISPLAY_SECONDS;

const chartRef    = ref(null);
let   myChart     = null;
const waveBuffer  = ref([]);          // 实际显示缓冲（滑动窗口）
let   renderQueue = [];               // WebSocket 原始积压队列
let   animationId = null;

// 手指接触后，自动放大纵轴观察细节
const FINGER_ON_THRESHOLD = 0.4;
const Y_ZOOM_WINDOW_POINTS = SAMPLE_RATE * 3; // 近 3 秒用于估计振幅
const Y_ZOOM_PADDING_RATIO = 0.2;
const Y_ZOOM_SMOOTH_ALPHA = 0.2;
let yAxisRange = null;

// 分数累加器 —— 解决 60fps 消耗 vs 50Hz 生产的速率差
let   pointAccumulator = 0;
let   lastRenderMs     = null;

// 预计算固定 X 轴标签（DISPLAY_POINTS 点，最右 = 现在）
// 每 50 点（= 1 秒）打一个刻度
const TIME_LABELS = Array.from({ length: DISPLAY_POINTS }, (_, i) => {
  const ptsFromRight = DISPLAY_POINTS - 1 - i;
  if (ptsFromRight % SAMPLE_RATE === 0) {
    const s = ptsFromRight / SAMPLE_RATE;
    return s === 0 ? '0s' : `-${s}s`;
  }
  return '';
});

const computeZoomedYAxisRange = (buffer) => {
  if (!buffer || buffer.length < 20) return null;

  const recent = buffer.slice(-Math.min(buffer.length, Y_ZOOM_WINDOW_POINTS));
  const sorted = [...recent].sort((a, b) => a - b);
  const n = sorted.length;
  const p10 = sorted[Math.floor((n - 1) * 0.10)];
  const p90 = sorted[Math.floor((n - 1) * 0.90)];
  let span = p90 - p10;

  if (!Number.isFinite(span) || span <= 0) {
    span = Math.max(Math.abs(p90 || 0) * 0.02, 10);
  }

  const pad = Math.max(span * Y_ZOOM_PADDING_RATIO, 8);
  return {
    min: p10 - pad,
    max: p90 + pad
  };
};

const initChart = () => {
  if (!chartRef.value) return;
  myChart = echarts.init(chartRef.value);

  myChart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 72, right: 24, top: 32, bottom: 48 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(55, 36, 20, 0.88)',
      borderColor: '#c8a96e',
      textStyle: { color: '#f7edd8', fontSize: 11 },
      formatter: (params) => {
        const p = params?.[0];
        if (!p) return '';
        const idx = Number(p.dataIndex ?? 0);
        const ptsFromRight = DISPLAY_POINTS - 1 - idx;
        const secFromNow = (ptsFromRight / SAMPLE_RATE).toFixed(2);
        const yVal = Number(p.value ?? 0);
        return `时间: -${secFromNow}s<br/>血流强度: ${yVal.toLocaleString('zh-CN')} AU`;
      }
    },

    // X 轴：时间刻度，间距较宽（每 50 点 = 1 秒一个标签）
    xAxis: {
      type: 'category',
      data: TIME_LABELS,
      boundaryGap: false,
      axisLine:  { lineStyle: { color: '#c8a96e' } },
      axisTick:  { show: true, alignWithLabel: false, interval: SAMPLE_RATE - 1 },
      axisLabel: {
        interval: SAMPLE_RATE - 1,   // 每 50 个点（1 秒）才显示一个标签
        color: '#8b6030',
        fontSize: 11,
        formatter: (val) => val       // 直接用预计算的字符串
      },
      splitLine: {
        show: true,
        interval: SAMPLE_RATE - 1,   // 垂直网格线也每 1 秒一条
        lineStyle: { color: '#ede0c4', type: 'dashed', width: 1 }
      }
    },

    // Y 轴：指尖血流强度（光电原始 ADC 值）
    yAxis: {
      type: 'value',
      name: '指尖血流强度\n(光强 AU)',
      nameTextStyle: { color: '#8b6030', fontSize: 11, align: 'center', lineHeight: 16 },
      nameGap: 10,
      scale: true,               // 自动缩放，不从 0 开始，完整展示波形振幅
      splitNumber: 8,
      axisLine:  { lineStyle: { color: '#c8a96e' } },
      minorTick: { show: true, splitNumber: 4 },
      minorSplitLine: { show: true, lineStyle: { color: '#f9f3e6', width: 0.8 } },
      axisLabel: {
        color: '#8b6030',
        fontSize: 10,
        formatter: (v) => {
          // 更细粒度显示，便于观察小幅波动
          if (Math.abs(v) >= 1000) return (v / 1000).toFixed(2) + 'k';
          return v.toFixed(1);
        }
      },
      splitLine: { lineStyle: { color: '#f5edd8', width: 1 } }
    },

    series: [{
      type: 'line',
      smooth: false,             // ← 关闭曲线平滑，保留真实锯齿波形（示波器感）
      symbol: 'none',
      sampling: 'lttb',          // 大数据量时启用 LTTB 降采样，保留波形形态
      lineStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0,   color: '#4facfe' },
          { offset: 0.5, color: '#00c9ff' },
          { offset: 1,   color: '#4facfe' }
        ]),
        width: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0,   color: 'rgba(0, 201, 255, 0.22)' },
          { offset: 0.7, color: 'rgba(0, 201, 255, 0.06)' },
          { offset: 1,   color: 'rgba(0, 201, 255, 0.01)' }
        ])
      },
      data: []
    }],

    animation: false   // 关闭 ECharts 内置动画，全由 rAF 驱动
  });

  window.addEventListener('resize', () => myChart?.resize());
};

// ─── 核心渲染循环 ───────────────────────────────────────────────────
// 每帧按照"实际经过时间 × 采样率"决定消耗多少点，消除速率漂移
const oscilloscopeRender = () => {
  const nowMs = performance.now();

  if (lastRenderMs !== null) {
    const dtMs = nowMs - lastRenderMs;
    // 本帧应消耗的点数（50 pts/s × 经过秒数）
    pointAccumulator += (dtMs / 1000) * SAMPLE_RATE;
  }
  lastRenderMs = nowMs;

  const toConsume = Math.min(
    Math.floor(pointAccumulator),  // 整数点数
    renderQueue.length,
    12                             // 单帧上限，防止卡帧时爆点
  );

  if (toConsume > 0) {
    pointAccumulator -= toConsume;
    const pts = renderQueue.splice(0, toConsume);

    // 直接 push 原始值，不做 EMA 平滑（示波器应呈现真实信号）
    waveBuffer.value.push(...pts);

    // 维持滑动窗口大小
    if (waveBuffer.value.length > DISPLAY_POINTS) {
      waveBuffer.value.splice(0, waveBuffer.value.length - DISPLAY_POINTS);
    }

    // 更新图表（仅 data，xAxis 用预计算标签无需每帧更新）
    if (myChart) {
      const fingerOn = signalQuality.value > FINGER_ON_THRESHOLD;

      if (fingerOn) {
        const targetRange = computeZoomedYAxisRange(waveBuffer.value);
        if (targetRange) {
          if (!yAxisRange) {
            yAxisRange = targetRange;
          } else {
            yAxisRange = {
              min: yAxisRange.min + (targetRange.min - yAxisRange.min) * Y_ZOOM_SMOOTH_ALPHA,
              max: yAxisRange.max + (targetRange.max - yAxisRange.max) * Y_ZOOM_SMOOTH_ALPHA
            };
          }
        }
      } else {
        yAxisRange = null;
      }

      myChart.setOption({
        series: [{ data: waveBuffer.value }],
        yAxis: yAxisRange
          ? { min: yAxisRange.min, max: yAxisRange.max }
          : { min: 'dataMin', max: 'dataMax' }
      });
    }
  }

  animationId = requestAnimationFrame(oscilloscopeRender);
};

// =====================================================================
// 4. WebSocket
// =====================================================================
let ws           = null;
let progressTimer = null;

const connectWS = () => {
  ws = new WebSocket('ws://localhost:8000/ws/pulse');
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.wave) renderQueue.push(...data.wave);
      signalQuality.value = Math.max(0, data.q || 0);
    } catch (e) { console.error('WS parse error:', e); }
  };
  ws.onerror = () => ElMessage.warning('WebSocket 连接异常，请确认 Python 后端已启动');
};

const startProgressAnim = () => {
  measuringProgress.value = 0;
  progressTimer = setInterval(() => {
    measuringProgress.value = measuringProgress.value < 90
      ? measuringProgress.value + 1
      : 0;
  }, 100);
};

const startCountdown = () => {
  countdown.value = 60;
  clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) countdown.value--;
    else clearInterval(countdownTimer);
  }, 1000);
};

// =====================================================================
// 5. 业务逻辑
// =====================================================================

// A. 开始测量
const startDiagnosis = async () => {
  if (!patientId.value) return ElMessage.warning('无患者ID');
  isStarting.value = true;
  try {
    await axios.post('http://localhost:8000/api/pulse/start');
    analysisResult.value = null;
    waveBuffer.value    = [];
    renderQueue         = [];
    yAxisRange          = null;
    pointAccumulator    = 0;
    lastRenderMs        = null;
    isMeasuring.value   = true;
    startProgressAnim();
    startCountdown();
    ElMessage.success('设备已启动，60 秒后自动分析');
  } catch (e) {
    ElMessage.error('启动失败，请检查 Python 后端连接');
  } finally {
    isStarting.value = false;
  }
};

// B. 结束并分析（可手动触发 or 倒计时归零自动触发）
const stopAndAnalyze = async () => {
  if (isAnalyzing.value) return;   // 防止重复调用
  try {
    isAnalyzing.value = true;
    const pyRes = await axios.post('http://localhost:8000/api/pulse/stop', null, {
      params: { user_id: patientId.value }
    });
    const report = pyRes.data;

    if (report.code !== 200 || report.avg_hr === 0) {
      ElMessage.warning(report.msg || '数据不足，请重测');
      resetMeasurement();
      return;
    }

    isMeasuring.value = false;
    clearInterval(progressTimer);
    clearInterval(countdownTimer);

    analysisResult.value = {
      avg_hr:       report.avg_hr,
      avg_spo2:     report.avg_spo2,
      suggestion:   report.suggestion,
      valid_rate:   report.valid_rate,
      sample_count: report.sample_count,
      pulse_metrics: report.pulse_metrics || {},
      pulse_tags:   report.pulse_tags || [],
      raw_wave:     report.raw_data_json || JSON.stringify(waveBuffer.value.slice(-300))
    };

    ElMessage.success('分析完成，请查看报告');
  } catch (e) {
    ElMessage.error('分析失败：' + e.message);
    isMeasuring.value = false;
    clearInterval(countdownTimer);
  } finally {
    isAnalyzing.value = false;
  }
};

// C. 入库公共方法
async function persistQieToServer() {
  const diagnosisId = route.query.caseId || localStorage.getItem('current_case_id');
  const payload = {
    userId:       patientId.value,
    diagnosisId:  diagnosisId ? Number(diagnosisId) : null,
    heartRate:    analysisResult.value.avg_hr,
    spo2:         analysisResult.value.avg_spo2,
    validRate:    analysisResult.value.valid_rate,
    sampleCount:  analysisResult.value.sample_count,
    tcmSuggestion: analysisResult.value.suggestion,
    qieKeyMetricsJson: JSON.stringify({
      hrv_rmssd_ms:    analysisResult.value.pulse_metrics?.hrv_rmssd_ms || 0,
      rhythm_cv:       analysisResult.value.pulse_metrics?.rhythm_cv || 0,
      perfusion_index: analysisResult.value.pulse_metrics?.perfusion_index || 0,
      signal_quality:  analysisResult.value.pulse_metrics?.signal_quality || 0,
      pulse_tags:      analysisResult.value.pulse_tags || []
    }),
    rawData: analysisResult.value.raw_wave
  };
  const javaRes = await axios.post('http://localhost:8080/api/detect/qie/save', payload);
  if (javaRes.data.code !== 200) throw new Error(javaRes.data.msg);
  localStorage.setItem('qie_finished_id', String(patientId.value));
}

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

const resetMeasurement = () => {
  analysisResult.value = null;
  isMeasuring.value    = false;
  waveBuffer.value     = [];
  renderQueue          = [];
  countdown.value      = 60;
  yAxisRange           = null;
  pointAccumulator     = 0;
  lastRenderMs         = null;
  clearInterval(progressTimer);
  clearInterval(countdownTimer);
};

// =====================================================================
// 6. 生命周期
// =====================================================================
onMounted(() => {
  if (!patientId.value) {
    ElMessage.error('缺少患者信息');
    setTimeout(() => router.push('/detect'), 1500);
    return;
  }
  nextTick(() => {
    initChart();
    connectWS();
    oscilloscopeRender();   // 启动示波器渲染循环
  });
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  clearInterval(progressTimer);
  clearInterval(countdownTimer);
  ws?.close();
  myChart?.dispose();
  window.removeEventListener('resize', () => myChart?.resize());
});
</script>

<style scoped>
/* ── 与主系统统一的暖棕色调 ── */
.qie-container {
  height: 100vh;
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

/* 页头 */
.header-bar {
  height: 60px;
  background: linear-gradient(180deg, #6b2d12 0%, #8b3d1a 100%);
  border-bottom: 2px solid #c8a020;
  box-shadow: 0 2px 12px rgba(60, 20, 0, .25);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}
.page-title {
  font-size: 17px;
  font-weight: 600;
  margin-left: 12px;
  color: #fdeabb;
  letter-spacing: 1px;
}
.patient-card {
  background: rgba(200, 160, 32, .15);
  padding: 5px 16px;
  border-radius: 20px;
  color: #fdeabb;
  font-size: 13px;
  font-weight: bold;
  border: 1px solid rgba(200, 160, 32, .3);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 主体 */
.main-content {
  flex: 1;
  display: flex;
  padding: 16px 20px;
  gap: 18px;
  overflow: hidden;
}

/* 左侧控制面板 */
.control-panel {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
}

/* 状态监控 */
.status-monitor {
  background: rgba(255, 252, 242, .95);
  border-radius: 10px;
  padding: 18px 20px;
  border: 1px solid #c8a96e;
  box-shadow: 0 3px 12px rgba(100, 60, 10, .08);
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.monitor-item .label {
  color: #8b6030;
  font-size: 12px;
  margin-bottom: 6px;
  display: block;
}
.value-display {
  height: 48px;
  display: flex;
  align-items: center;
}
.measuring-state {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #8b3d1a;
}
.anim-text {
  font-size: 14px;
  font-weight: 500;
  animation: blink 1.5s infinite;
}
.mini-progress { width: 150px; }
.result-state .number {
  font-size: 38px;
  font-weight: bold;
  color: #3d2b10;
  line-height: 1;
}
.result-state .number.blue { color: #4a7060; }
.idle-state {
  font-size: 30px;
  color: #d4b483;
  font-weight: bold;
}
.flex-between {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}
.signal-val { font-size: 12px; }
.text-success { color: #4a7060; }
.text-warning { color: #c8a020; }
.text-danger  { color: #c0392b; }

/* 倒计时卡片 */
.countdown-card {
  background: rgba(255, 252, 242, .95);
  border-radius: 10px;
  padding: 16px 20px;
  border: 1px solid #c8a96e;
  box-shadow: 0 3px 12px rgba(100, 60, 10, .08);
}
.countdown-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8b3d1a;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}
.countdown-progress { margin-bottom: 8px; }
.countdown-text {
  text-align: center;
  font-size: 13px;
  color: #8b6030;
}
.countdown-text b { color: #8b3d1a; font-size: 16px; }
.auto-analyzing { color: #4a7060; font-weight: 600; }

/* 中医脉象卡片 */
.tcm-card {
  background: linear-gradient(135deg, #fdf8ef 0%, #faf3e0 100%);
  border: 1px solid #c8a96e;
  border-radius: 10px;
  padding: 16px 18px;
  box-shadow: 0 3px 12px rgba(100, 60, 10, .08);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8b3d1a;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 10px;
  border-bottom: 1px dashed #e8d5a0;
  padding-bottom: 8px;
}
.tcm-text {
  font-size: 13px;
  line-height: 2.0;
  color: #5a2d00;
  white-space: pre-wrap;
  font-family: 'KaiTi', 'SimKai', serif;
}

/* 操作区 */
.action-area {
  background: rgba(255, 252, 242, .95);
  border-radius: 10px;
  padding: 18px 20px;
  border: 1px solid #c8a96e;
  box-shadow: 0 3px 12px rgba(100, 60, 10, .08);
  margin-top: auto;
}
.instruction-text {
  background: #faf3e0;
  color: #8b6030;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #e8d5a0;
  font-size: 13px;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.5;
}
.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.action-btn { height: 44px; font-size: 14px; width: 100%; border-radius: 6px; }
.result-btns { display: flex; flex-wrap: wrap; gap: 10px; }
.flex-1 { flex: 1; min-width: 100px; }

/* ══════════════════════════════════════════
   右侧图表面板
══════════════════════════════════════════ */
.chart-panel {
  flex: 1;
  background: rgba(255, 252, 242, .95);
  border-radius: 10px;
  border: 1px solid #c8a96e;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 3px 12px rgba(100, 60, 10, .08);
  position: relative;
}

.chart-header {
  height: 52px;
  border-bottom: 1px solid #e8d5a0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: linear-gradient(180deg, #f5e4a8 0%, #ebd07a 100%);
  flex-shrink: 0;
}
.chart-title-group {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.chart-title {
  font-weight: 700;
  color: #5a2d00;
  font-size: 14px;
}
.chart-subtitle {
  font-size: 10px;
  color: #8b6030;
  opacity: 0.8;
}
.chart-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}
.sampling-badge {
  background: rgba(139, 61, 26, .12);
  color: #8b3d1a;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid rgba(139, 61, 26, .2);
}
.live-indicator {
  color: #c0392b;
  font-weight: bold;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 8px;
  height: 8px;
  background: #c0392b;
  border-radius: 50%;
  animation: blink 1s infinite;
}

/* ECharts 主区域 */
.echarts-box {
  flex: 1;
  width: 100%;
  min-height: 0;
}

/* PPG 科普说明条 */
.ppg-legend-bar {
  height: 72px;
  border-top: 1px solid #e8d5a0;
  background: linear-gradient(180deg, #fffcf2 0%, #faf3e0 100%);
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 0;
  flex-shrink: 0;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}
.legend-divider {
  width: 1px;
  height: 40px;
  background: #e8d5a0;
  margin: 0 12px;
  flex-shrink: 0;
}
.legend-icon {
  font-size: 18px;
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}
.peak-icon    { color: #c0392b; }
.trough-icon  { color: #4a7060; }
.interval-icon { color: #8b3d1a; }
.amp-icon     { color: #c8a020; }
.legend-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.legend-text b {
  font-size: 12px;
  color: #5a2d00;
  font-weight: 700;
}
.legend-text span {
  font-size: 10px;
  color: #8b6030;
  line-height: 1.4;
}

/* 空闲引导 overlay */
.chart-idle-overlay {
  position: absolute;
  top: 52px;       /* header 高度 */
  left: 0;
  right: 0;
  bottom: 72px;    /* legend-bar 高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.idle-illustration {
  text-align: center;
  padding: 20px;
}
.idle-wave-svg {
  width: 320px;
  height: 64px;
  margin-bottom: 12px;
  opacity: 0.6;
}
.idle-hint {
  font-size: 14px;
  color: #8b6030;
  margin: 0 0 6px 0;
  font-weight: 600;
}
.idle-sub {
  font-size: 12px;
  color: #b89a60;
  margin: 0;
}

/* 参考文献 */
.ref-list { display: flex; flex-direction: column; gap: 8px; }
.ref-item {
  padding: 8px;
  background: #fff;
  border-left: 2px solid #5d9cec;
  border-radius: 3px;
  font-size: 11px;
}
.ref-authors {
  display: block;
  color: #666;
  font-weight: 600;
  margin-bottom: 3px;
}
.ref-desc { margin: 3px 0; color: #666; line-height: 1.4; }
.ref-link {
  display: inline-block;
  color: #5d9cec;
  text-decoration: none;
  font-size: 10px;
  margin-top: 3px;
}
.ref-link:hover { color: #1890ff; text-decoration: underline; }

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: .35; }
}
</style>