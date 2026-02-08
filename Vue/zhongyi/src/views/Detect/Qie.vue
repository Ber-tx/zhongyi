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


//在 script 标签顶部定义一个变量记录最后一帧
let animationFrameId = null;

// ===== 1. 基础状态管理 =====
const route = useRoute();
const router = useRouter();

const patientId = ref(route.query.id || '');
const patientIdCard = ref(route.query.idCard || '');

const isStarting = ref(false);   // 正在请求开始
const isMeasuring = ref(false);  // 正在测量中
const isSaving = ref(false);     // 正在保存中
const hasData = ref(false);      // 是否有历史数据

// 实时数据
const currentHr = ref(0);
const currentSpo2 = ref(0);
const signalQuality = ref(0);    // 0.0 - 1.0

// 计算属性
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

// ===== 2. ECharts 配置 =====
const chartRef = ref(null);
let myChart = null;
// 波形数据缓存池 (用于平滑滚动)
let waveBuffer = []; 
const MAX_POINTS = 500; // 屏幕上保留最近5秒的数据 (100Hz * 5)

const initChart = () => {
  if (!chartRef.value) return;
  
  myChart = echarts.init(chartRef.value);
  const option = {
    backgroundColor: '#fff',
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      show: false, // 隐藏X轴刻度
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      scale: true, // 自动缩放，不仅是从0开始
      splitLine: { show: true, lineStyle: { color: '#eee' } },
      axisLabel: { color: '#999' }
    },
    series: [{
      name: 'Pulse',
      type: 'line',
      smooth: true,
      symbol: 'none', // 不显示数据点圆圈
      lineStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#4facfe' }, // 渐变色：蓝
          { offset: 1, color: '#00f2fe' }  // 渐变色：青
        ]),
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 242, 254, 0.3)' },
          { offset: 1, color: 'rgba(0, 242, 254, 0.05)' }
        ])
      },
      data: new Array(MAX_POINTS).fill(0) // 初始化空数据
    }],
    animation: false // 关闭默认动画以提高实时性能
  };
  myChart.setOption(option);
  
  // 响应式大小
  window.addEventListener('resize', () => myChart.resize());
};

// 更新图表数据
const updateChartData = (newWaveData) => {
  if (!myChart) return;
  
  // 1. 将新数据追加到 buffer
  // Python 传过来的是 int 数组，可能是 [71000, 71200...]
  // 为了美观，可以减去直流分量（比如减去第一项），或者依靠 scale:true
  waveBuffer.push(...newWaveData);
  
  // 2. 保持 buffer 长度恒定 (滚动窗口)
  if (waveBuffer.length > MAX_POINTS) {
    waveBuffer = waveBuffer.slice(waveBuffer.length - MAX_POINTS);
  }
  
  // 3. 渲染
  if (!animationFrameId) {
    animationFrameId = requestAnimationFrame(() => {
      myChart.setOption({
        series: [{ data: waveBuffer }]
      }, { notMerge: false, lazyUpdate: true });
      animationFrameId = null; // 渲染完释放标记
    });
  }
};

// ===== 3. WebSocket 通讯 =====
let ws = null;

const connectWebSocket = () => {
  // 注意：这里的地址要和你的 Python FastAPI 对应
  ws = new WebSocket('ws://localhost:8000/ws/pulse');
  
  ws.onopen = () => {
    console.log('✅ 脉诊 WebSocket 已连接');
  };
  
  ws.onmessage = (event) => {
    
    try {
      const data = JSON.parse(event.data);
      // data 结构: { wave: [...], hr: 75, isValid: true, q: 0.9 }
      console.log('收到数据:', data)
      // 更新数值面板
      if (data.isValid) {
        currentHr.value = data.hr;
        currentSpo2.value = data.spo2;
      }
      signalQuality.value = data.q || 0;
      
      // 更新图表
      if (data.wave && data.wave.length > 0) {
        updateChartData(data.wave);
        hasData.value = true;
      }
      
    } catch (e) {
      console.error('WS 数据解析错误', e);
    }
  };
  
  ws.onerror = () => {
    ElMessage.error('无法连接传感器服务，请检查 Python 后端是否启动');
  };
  
  ws.onclose = () => {
    console.log('WebSocket 已断开');
  };
};

// ===== 4. 业务逻辑控制 =====

// A. 开始诊断
const startDiagnosis = async () => {
  if (!patientId.value) {
    ElMessage.warning('未能获取当前患者ID，请重新选择');
    return;
  }
  
  isStarting.value = true;
  try {
    // 调用 Python 接口：开始记录
    await axios.post('http://localhost:8000/api/pulse/start');
    
    // 清空旧数据
    waveBuffer = new Array(MAX_POINTS).fill(0); 
    isMeasuring.value = true;
    hasData.value = true;
    
    ElMessage.success('设备已启动，正在采集脉搏信号...');
  } catch (error) {
    console.error(error);
    ElMessage.error('启动失败：' + error.message);
  } finally {
    isStarting.value = false;
  }
};

// B. 结束并保存
const stopDiagnosis = async () => {
  try {
    await ElMessageBox.confirm('确定结束本次采集并保存数据吗？', '确认操作', {
      confirmButtonText: '保存结果',
      cancelButtonText: '继续采集',
      type: 'warning'
    });
    
    isSaving.value = true;
    
    // 1. 找 Python 要报告 (停止并获取平均值)
    const pythonRes = await axios.post('http://localhost:8000/api/pulse/stop', null, {
      params: { user_id: patientId.value }
    });
    
    const reportData = pythonRes.data;
    
    if (!reportData || reportData.avg_hr === 0) {
      throw new Error("有效数据不足，请重新采集");
    }

    // 2. 找 Java Spring Boot 存库
    // 假设你的 Java 接口是这个，请根据实际情况修改
    const javaRes = await axios.post('http://localhost:8080/api/medical/record/save', {
      userId: reportData.user_id, // 注意字段名驼峰转换
      heartRate: reportData.avg_hr,
      spo2: reportData.avg_spo2,
      rawData: reportData.raw_data_json, // 这里存入数据库
      diagnosis: reportData.suggestion,
      moduleType: 'qie' // 标识是切诊模块
    });

    if (javaRes.data.code === 200 || javaRes.status === 200) {
      ElMessage.success('脉诊数据入库成功！');
      
      // 3. 关键：更新 LocalStorage 状态，通知 DetectSelect 页面
      localStorage.setItem('qie_finished_id', String(patientId.value));
      
      // 4. 返回选择页
      router.push('/detect');
    } else {
      throw new Error(javaRes.data.msg || '入库失败');
    }

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '保存过程中发生错误');
    }
  } finally {
    isSaving.value = false;
    isMeasuring.value = false; // 停止状态
  }
};

// ===== 生命周期 =====
onMounted(() => {
  // 1. 检查 ID
  if (!patientId.value) {
    ElMessage.error('缺少患者信息，正在返回...');
    setTimeout(() => router.push('/detect'), 1500);
    return;
  }
  
  // 2. 初始化图表
  nextTick(() => {
    initChart();
  });
  
  // 3. 建立 WS 连接 (页面一进来就连，方便看波形，但不记录)
  connectWebSocket();
});

onUnmounted(() => {
  if (ws) ws.close();
  if (myChart) myChart.dispose();
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