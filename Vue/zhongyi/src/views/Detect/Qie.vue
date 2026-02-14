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
              @click="stopAndAnalyze"
              class="action-btn stop-btn"
            >
              <el-icon class="mr-1"><DataAnalysis /></el-icon> 结束采集并生成报告
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

// ===== 1. 基础状态 =====
const route = useRoute();
const router = useRouter();
const patientId = ref(route.query.id || '');

// 流程控制状态
const isStarting = ref(false);    // 启动中
const isMeasuring = ref(false);   // 测量进行中
const isAnalyzing = ref(false);   // Python分析中
const isSaving = ref(false);      // Java入库中

// 结果数据 (仅在测量结束后赋值)
const analysisResult = ref(null); // { avg_hr, avg_spo2, suggestion, ... }

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

// ===== 2. 图表平滑渲染逻辑 (保留你之前的优秀代码) =====
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

const smoothRender = () => {
  if (renderQueue.length > 0) {
    const points = renderQueue.splice(0, 2); 
    waveBuffer.value.push(...points);
    if (waveBuffer.value.length > MAX_DISPLAY_POINTS) {
      waveBuffer.value.splice(0, points.length);
    }
    if (myChart) myChart.setOption({ series: [{ data: waveBuffer.value }] });
  }
  animationId = requestAnimationFrame(smoothRender);
};

// ===== 3. WebSocket (只负责收波形和信号质量) =====
let ws = null;
let progressTimer = null;

const connectWS = () => {
  // 注意：确保你的 Python 端口对应 (8000)
  ws = new WebSocket('ws://localhost:8000/ws/pulse');
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      // 1. 波形入队
      if (data.wave) renderQueue.push(...data.wave);
      // 2. 更新信号质量 (仅用于UI展示接触情况)
      signalQuality.value = data.q || 0;
      // 注意：这里不再更新 currentHr/currentSpo2，防止数字乱跳
    } catch (e) { console.error(e); }
  };
};

// 假进度条动画，让等待不枯燥
const startProgressAnim = () => {
  measuringProgress.value = 0;
  progressTimer = setInterval(() => {
    if (measuringProgress.value < 90) measuringProgress.value += 1;
    else measuringProgress.value = 0;
  }, 100);
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
    startProgressAnim();
    
    ElMessage.success('设备已启动，请保持静止...');
  } catch (e) {
    ElMessage.error('启动失败，请检查Python后端');
  } finally {
    isStarting.value = false;
  }
};

// B. 结束并分析 (核心修改：只获取数据，不直接保存)
const stopAndAnalyze = async () => {
  try {
    isAnalyzing.value = true;
    
    // 1. 找 Python 要报告
    const pyRes = await axios.post('http://localhost:8000/api/pulse/stop', null, {
      params: { user_id: patientId.value }
    });
    
    const report = pyRes.data;
    
    if (report.code !== 200 || report.avg_hr === 0) {
      ElMessage.warning(report.msg || "数据不足，请重测");
      resetMeasurement(); // 数据不好直接重置
      return;
    }

    // 2. 展示结果 (不立即入库，让医生先看)
    isMeasuring.value = false;
    clearInterval(progressTimer);
    
    // 将 Python 返回的数据存入本地变量，用于展示
    analysisResult.value = {
      avg_hr: report.avg_hr,
      avg_spo2: report.avg_spo2,
      suggestion: report.suggestion, // 中医建议
      valid_rate: report.valid_rate,
      sample_count: report.sample_count,
      // 保存最后一段波形用于入库
      raw_wave: JSON.stringify(waveBuffer.value.slice(-300)) 
    };
    
    ElMessage.success("分析完成，请查看报告");

  } catch (e) {
    ElMessage.error("分析失败：" + e.message);
    isMeasuring.value = false;
  } finally {
    isAnalyzing.value = false;
  }
};

// C. 确认入库 (用户点击满意后)
const saveToRecord = async () => {
  if (!analysisResult.value) return;
  
  isSaving.value = true;
  try {
    // 构造发给 Java 的数据
    const payload = {
      userId: patientId.value,
      heartRate: analysisResult.value.avg_hr,
      spo2: analysisResult.value.avg_spo2,
      validRate: analysisResult.value.valid_rate,
      sampleCount: analysisResult.value.sample_count,
      tcmSuggestion: analysisResult.value.suggestion,
      rawData: analysisResult.value.raw_wave
    };

    const javaRes = await axios.post('http://localhost:8080/api/detect/qie/save', payload);

    if (javaRes.data.code === 200) {
      ElMessage.success("数据已归档！");
      localStorage.setItem('qie_finished_id', String(patientId.value));
      router.push('/detect');
    } else {
      throw new Error(javaRes.data.msg);
    }
  } catch (e) {
    ElMessage.error("入库失败：" + e.message);
  } finally {
    isSaving.value = false;
  }
};

// D. 重新测量
const resetMeasurement = () => {
  analysisResult.value = null;
  isMeasuring.value = false;
  waveBuffer.value = [];
  renderQueue = [];
  clearInterval(progressTimer);
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
  ws?.close();
  myChart?.dispose();
});
</script>

<style scoped>
/* 样式重点优化了“测量中”和“结果展示”的视觉差异 */

.qie-container {
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.header-bar {
  height: 60px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}
.page-title { font-size: 18px; font-weight: 600; margin-left: 12px; color: #303133; }
.patient-card { background: #f0f9eb; padding: 6px 16px; border-radius: 20px; color: #67c23a; font-size: 14px; font-weight: bold; }

.main-content {
  flex: 1;
  display: flex;
  padding: 24px;
  gap: 24px;
  overflow: hidden;
}

.control-panel {
  width: 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto; /* 允许小屏滚动 */
}

/* 状态显示区 */
.status-monitor {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.monitor-item .label { color: #909399; font-size: 14px; margin-bottom: 8px; display: block; }

.value-display {
  height: 50px;
  display: flex;
  align-items: center;
}

/* 测量中的动画状态 */
.measuring-state {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #409eff;
}
.anim-text { font-size: 16px; font-weight: 500; animation: blink 1.5s infinite; }
.mini-progress { width: 150px; }

/* 结果状态 */
.result-state .number { font-size: 40px; font-weight: bold; color: #303133; line-height: 1; }
.result-state .number.blue { color: #409eff; }

/* 空闲状态 */
.idle-state { font-size: 32px; color: #dcdfe6; font-weight: bold; }

/* 信号质量条 */
.flex-between { display: flex; justify-content: space-between; margin-bottom: 6px; }
.signal-val { font-size: 12px; }
.text-success { color: #67c23a; }
.text-warning { color: #e6a23c; }
.text-danger { color: #f56c6c; }

/* 中医卡片 */
.tcm-card {
  background: linear-gradient(135deg, #fdfbf5 0%, #fff 100%);
  border: 1px solid #faecd8;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.1);
}
.card-header { 
  display: flex; align-items: center; gap: 8px; 
  color: #d35400; font-weight: bold; font-size: 16px; margin-bottom: 12px; border-bottom: 1px dashed #faecd8; padding-bottom: 10px;
}
.tcm-text {
  font-size: 15px; line-height: 1.8; color: #606266;
  white-space: pre-wrap; /* 关键：保留换行符 */
  font-family: 'KaiTi', 'SimKai', serif; /* 楷体更有中医感 */
}

/* 按钮区 */
.action-area {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-top: auto;
}
.instruction-text { background: #f4f4f5; color: #909399; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px; display: flex; align-items: center; gap: 6px; }
.button-group { display: flex; flex-direction: column; gap: 12px; }
.action-btn { height: 48px; font-size: 16px; width: 100%; border-radius: 8px; }
.result-btns { display: flex; gap: 12px; }
.flex-1 { flex: 1; }

/* 右侧图表 */
.chart-panel { flex: 1; background: white; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; }
.chart-header { height: 50px; border-bottom: 1px solid #EBEEF5; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
.chart-title { font-weight: 600; color: #303133; }
.live-indicator { color: #f56c6c; font-weight: bold; font-size: 12px; display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; background: #f56c6c; border-radius: 50%; animation: blink 1s infinite; }
.echarts-box { flex: 1; width: 100%; }

@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
</style>