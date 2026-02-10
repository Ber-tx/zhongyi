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
            <span class="label">实时心率 (BPM)</span>
            <div class="value-display">
              <span class="number" :class="{ 'heart-beat': isMeasuring && currentHr > 0 }">
                {{ currentHr || '--' }}
              </span>
              <el-icon class="heart-icon" :class="{ 'beating': isMeasuring && currentHr > 0 }"><aim /></el-icon>
            </div>
          </div>
          
          <div class="monitor-item">
            <span class="label">血氧饱和度 (%)</span>
            <div class="value-display">
              <span class="number blue">{{ currentSpo2 || '--' }}</span>
            </div>
          </div>

          <div class="monitor-item signal-box">
            <span class="label">信号质量</span>
            <el-progress 
              :percentage="signalQuality * 100" 
              :status="signalStatus"
              :stroke-width="15"
              text-inside 
              striped 
              striped-flow
            />
            <div class="signal-text">{{ signalText }}</div>
          </div>
        </div>

        <div class="action-area">
          <div class="instruction-text" v-if="!isMeasuring">
            <el-icon><InfoFilled /></el-icon>
            请嘱咐患者将手指平稳放置于传感器上，保持静止。
          </div>
          
          <div class="button-group">
            <el-button 
              type="primary" 
              size="large" 
              :loading="isStarting"
              :disabled="isMeasuring"
              @click="startDiagnosis"
              class="action-btn start-btn"
            >
              <el-icon class="mr-1"><VideoPlay /></el-icon> 开始切诊
            </el-button>

            <el-button 
              type="danger" 
              size="large" 
              :disabled="!isMeasuring"
              :loading="isSaving"
              @click="stopDiagnosis"
              class="action-btn stop-btn"
            >
              <el-icon class="mr-1"><SwitchButton /></el-icon> 结束并保存
            </el-button>
          </div>
        </div>
      </div>

      <div class="chart-panel">
        <div class="chart-header">
          <span class="chart-title">实时脉搏波形图 (PPG Waveform)</span>
          <div class="live-indicator" v-if="isMeasuring">
            <span class="dot"></span> LIVE
          </div>
        </div>
        <div ref="chartRef" class="echarts-box"></div>
        <div class="chart-overlay" v-if="!isMeasuring && !hasData">
          <el-empty description="等待开始采集..." image-size="100"></el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Back, User, VideoPlay, SwitchButton, Aim, InfoFilled } from '@element-plus/icons-vue';
import axios from 'axios';
import * as echarts from 'echarts';

// 动画帧 ID（用于 smoothRender）
let animationId = null;

const route = useRoute();
const router = useRouter();

const patientId = ref(route.query.id || '');
const patientIdCard = ref(route.query.idCard || '');

// 用来存测量过程中的所有有效值
const hrHistory = ref([]);
const spo2History = ref([]);

const isStarting = ref(false);   // 正在请求开始
const isMeasuring = ref(false);  // 正在测量中
const isSaving = ref(false);     // 正在保存中
const hasData = ref(false);      // 是否有历史数据

// 实时数据
const currentHr = ref(0);
const currentSpo2 = ref(0);
const signalQuality = ref(0);    // 0.0 - 1.0

// 计算属性（信号状态提示）
const signalStatus = computed(() => {
  if (signalQuality.value > 0.8) return 'success';
  if (signalQuality.value > 0.5) return 'warning';
  return 'exception';
});

const signalText = computed(() => {
  if (signalQuality.value > 0.8) return '信号优良';
  if (signalQuality.value > 0.5) return '信号一般，请保持静止';
  return '信号干扰严重 / 未检测到手指';
});

// 🔧 修复1: 响应式波形缓冲 + 非响应式渲染队列
const waveBuffer = ref([]);             // 真正用于 ECharts 的数组 (响应式)
let renderQueue = [];                   // 待渲染的数据队列 (非响应式，提速)
const MAX_DISPLAY_POINTS = 500;         // 显示窗口大小（约10秒数据）

let myChart = null;
const chartRef = ref(null);

// ===== ECharts 初始化 =====
const initChart = () => {
  if (!chartRef.value) return;
  
  myChart = echarts.init(chartRef.value);
  const option = {
    backgroundColor: '#fff',
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      show: false,
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { show: true, lineStyle: { color: '#eee' } },
      axisLabel: { color: '#999' }
    },
    series: [{
      name: 'Pulse',
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#4facfe' },
          { offset: 1, color: '#00f2fe' }
        ]),
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 242, 254, 0.3)' },
          { offset: 1, color: 'rgba(0, 242, 254, 0.05)' }
        ])
      },
      data: []
    }],
    animation: false  // 关闭自带动画，防止卡顿
  };
  myChart.setOption(option);
  
  window.addEventListener('resize', () => myChart?.resize());
};

// 🔧 修复2: 平滑渲染核心（队列 + requestAnimationFrame）
const smoothRender = () => {
  if (renderQueue.length > 0) {
    const points = renderQueue.splice(0, 2); // 每次取少量点，保持流畅
    waveBuffer.value.push(...points);

    if (waveBuffer.value.length > MAX_DISPLAY_POINTS) {
      waveBuffer.value.splice(0, points.length);
    }

    if (myChart) {
      myChart.setOption({ series: [{ data: waveBuffer.value }] });
    }
  }
  animationId = requestAnimationFrame(smoothRender);
};

// ===== WebSocket 通讯 =====
let ws = null;

const connectWebSocket = () => {
  ws = new WebSocket('ws://localhost:8000/ws/pulse');
  
  ws.onopen = () => console.log('✅ 脉诊 WebSocket 已连接');
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('📡 收到数据:', data);

      // 更新信号质量
      if (typeof data.q !== 'undefined') {
        signalQuality.value = Number(data.q) || 0;
      }
      
      // 更新心率/血氧
      if (data.isValid && data.hr > 40 && data.hr < 180) {
        currentHr.value = data.hr;
        currentSpo2.value = data.spo2 || 0;
        
        if (isMeasuring.value) {
          hrHistory.value.push(data.hr);
          spo2History.value.push(data.spo2 || 0);
        }
      }
      
      // 波形进入渲染队列
      if (data.wave && Array.isArray(data.wave) && data.wave.length > 0) {
        renderQueue.push(...data.wave);
        hasData.value = true;
      }
      
    } catch (e) {
      console.error('❌ WS 数据解析错误:', e);
    }
  };
  
  ws.onerror = () => ElMessage.error('无法连接传感器服务，请检查 Python 后端是否启动');
  ws.onclose = () => console.log('⚠️ WebSocket 已断开');
};

// ===== 业务逻辑 =====
const startDiagnosis = async () => {
  if (!patientId.value) {
    ElMessage.warning('未能获取当前患者ID，请重新选择');
    return;
  }
  
  isStarting.value = true;
  try {
    await axios.post('http://localhost:8000/api/pulse/start');
    
    hrHistory.value = [];
    spo2History.value = [];
    waveBuffer.value = [];
    renderQueue = [];
    isMeasuring.value = true;
    hasData.value = true;
    
    ElMessage.success('设备已启动，正在采集脉搏信号...');
  } catch (error) {
    console.error('❌ 启动失败:', error);
    ElMessage.error('启动失败：' + (error.response?.data?.message || error.message));
  } finally {
    isStarting.value = false;
  }
};

const stopDiagnosis = async () => {
  try {
    await ElMessageBox.confirm('确定结束本次采集并保存数据吗？', '确认操作', {
      confirmButtonText: '保存结果',
      cancelButtonText: '继续采集',
      type: 'warning'
    });
    
    isMeasuring.value = false;
    isSaving.value = true;
    
    const calculateAvg = (arr) => arr.length ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)) : 0;
    const finalHr = calculateAvg(hrHistory.value);
    const finalSpo2 = calculateAvg(spo2History.value);
    
    if (finalHr === 0 || hrHistory.value.length < 10) {
      throw new Error("有效数据不足，请保持手指静止重测");
    }
    
    const snapshotWave = waveBuffer.value.length > 0 ? waveBuffer.value.slice(-500) : [];
    
    const requestData = {
      userId: patientId.value,
      heartRate: finalHr,
      spo2: finalSpo2,
      rawData: JSON.stringify(snapshotWave)
    };
    
    const res = await axios.post('http://localhost:8080/api/detect/qie/save', requestData);
    
    if (res.data.code === 200) {
      ElMessage.success('脉诊数据入库成功！');
      localStorage.setItem('qie_finished_id', String(patientId.value));
      setTimeout(() => router.push('/detect'), 1000);
    } else {
      throw new Error(res.data.msg || '入库失败');
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('❌ 保存失败:', error);
      ElMessage.error(error.message || '保存过程中发生错误');
      isMeasuring.value = true;
    }
  } finally {
    isSaving.value = false;
  }
};

// ===== 生命周期 =====
onMounted(() => {
  if (!patientId.value) {
    ElMessage.error('缺少患者信息，正在返回...');
    setTimeout(() => router.push('/detect'), 1500);
    return;
  }
  
  nextTick(() => {
    initChart();
    connectWebSocket();
    smoothRender(); // 启动平滑渲染
  });
});

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId);
  if (ws) ws.close();
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }
});
</script>

<style scoped>
/* 使用 Flex 布局实现响应式设计 */
.qie-container {
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 顶部栏 */
.header-bar {
  height: 60px;
  background: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  z-index: 10;
}

.left-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.patient-card {
  display: flex;
  align-items: center;
  background: #f0f9eb;
  padding: 6px 16px;
  border-radius: 20px;
  color: #67c23a;
  font-size: 14px;
}

.patient-card .value {
  font-weight: bold;
  margin-left: 8px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  padding: 24px;
  gap: 24px;
  overflow: hidden;
}

/* 左侧控制面板 */
.control-panel {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.status-monitor {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.monitor-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.monitor-item .label {
  font-size: 14px;
  color: #909399;
}

.value-display {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.value-display .number {
  font-size: 48px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.value-display .number.blue {
  color: #409eff;
}

.heart-icon {
  font-size: 28px;
  color: #f56c6c;
}

/* 心跳动画 */
@keyframes heartbeat {
  0% { transform: scale(1); }
  15% { transform: scale(1.3); }
  30% { transform: scale(1); }
  45% { transform: scale(1.15); }
  60% { transform: scale(1); }
}

.beating {
  animation: heartbeat 1s infinite;
}

.signal-text {
  font-size: 12px;
  color: #606266;
  margin-top: 6px;
  text-align: right;
}

/* 操作区 */
.action-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.instruction-text {
  color: #e6a23c;
  background: #fdf6ec;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.action-btn {
  height: 50px;
  font-size: 16px;
  border-radius: 8px;
}

/* 右侧图表区 */
.chart-panel {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.chart-header {
  height: 50px;
  border-bottom: 1px solid #EBEEF5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.chart-title {
  font-weight: 600;
  color: #303133;
}

.live-indicator {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #f56c6c;
  font-weight: bold;
}

.live-indicator .dot {
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
  margin-right: 6px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

.echarts-box {
  flex: 1;
  width: 100%;
  min-height: 400px;
}

.chart-overlay {
  position: absolute;
  top: 50px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 5;
}
</style>