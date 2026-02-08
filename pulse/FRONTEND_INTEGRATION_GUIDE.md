# Vue3 前端集成指南

## 📱 前后端数据交互流程

### 简化的API响应格式

```json
{
  "status": "success",
  "data": {
    "heart_rate": 75,           // 心率 (bpm)
    "blood_oxygen": 98,         // 血氧饱和度 (%)
    "blood_pressure": {         // 血压 (mmHg)
      "sys": 120,
      "dia": 80
    },
    "pulse_type": "平脉",       // 脉象分类
    "timestamp": 1706000000     // Unix时间戳
  }
}
```

---

## 🎯 前端实现步骤

### 1. 安装依赖

```bash
npm install axios echarts socket.io-client
```

### 2. 健康指标显示组件 (PulseHealth.vue)

```vue
<template>
  <div class="health-dashboard">
    <!-- 核心健康指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card heart-rate">
        <div class="icon">❤️</div>
        <div class="label">心率</div>
        <div class="value">{{ health.heart_rate }}</div>
        <div class="unit">BPM</div>
      </div>

      <div class="metric-card blood-oxygen">
        <div class="icon">💨</div>
        <div class="label">血氧</div>
        <div class="value">{{ health.blood_oxygen }}</div>
        <div class="unit">%</div>
      </div>

      <div class="metric-card blood-pressure">
        <div class="icon">🩸</div>
        <div class="label">血压</div>
        <div class="value">
          {{ health.blood_pressure?.sys }}/{{ health.blood_pressure?.dia }}
        </div>
        <div class="unit">mmHg</div>
      </div>

      <div class="metric-card pulse-type">
        <div class="icon">📊</div>
        <div class="label">脉象</div>
        <div class="value">{{ health.pulse_type }}</div>
        <div class="unit">分类</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const health = reactive({
  heart_rate: 0,
  blood_oxygen: 0,
  blood_pressure: { sys: 0, dia: 0 },
  pulse_type: '-'
})

// 调用后端API获取健康数据
const fetchHealthData = async (pulseData) => {
  try {
    const response = await axios.post('/api/pulse/receive', pulseData)
    if (response.data.status === 'success') {
      // 直接使用返回的数据
      Object.assign(health, response.data.data)
    }
  } catch (error) {
    console.error('获取健康数据失败:', error)
  }
}

defineExpose({ fetchHealthData })
</script>

<style scoped>
.health-dashboard {
  padding: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metric-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}

.unit {
  font-size: 12px;
  opacity: 0.8;
}

/* 各指标的颜色 */
.heart-rate {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.blood-oxygen {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.blood-pressure {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.pulse-type {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}
</style>
```

### 3. 波形实时显示组件 (WaveformChart.vue)

```vue
<template>
  <div class="waveform-container">
    <div class="chart-header">
      <h2>PPG 波形</h2>
      <span class="status" :class="`status-${connectionStatus}`">
        {{ connectionStatus === 'connected' ? '连接中' : '离线' }}
      </span>
    </div>
    <div id="waveform-chart" style="width: 100%; height: 300px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const chart = ref(null)
const chartInstance = ref(null)
const connectionStatus = ref('disconnected')
const waveformData = ref([])
const maxDataPoints = 500

// 初始化图表
const initChart = () => {
  const domElement = document.getElementById('waveform-chart')
  if (!domElement) return

  chartInstance.value = echarts.init(domElement)

  const option = {
    animation: false,
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      boundaryGap: false,
      splitLine: { show: false },
      axisLine: { lineStyle: { color: '#ddd' } }
    },
    yAxis: {
      type: 'value',
      splitLine: { show: true, lineStyle: { color: '#eee' } },
      axisLine: { lineStyle: { color: '#ddd' } }
    },
    series: [
      {
        data: [],
        type: 'line',
        smooth: true,
        lineStyle: { width: 2, color: '#f5576c' },
        areaStyle: {
          color: 'rgba(245, 87, 108, 0.3)'
        },
        symbol: 'none',
        sampling: 'lttb',
        itemStyle: { color: '#f5576c' }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

// 更新波形数据
const updateWaveform = (ppgSamples) => {
  if (!chartInstance.value) return

  // 添加新数据点
  waveformData.value.push(...ppgSamples)

  // 保持最大数据点限制
  if (waveformData.value.length > maxDataPoints) {
    waveformData.value = waveformData.value.slice(-maxDataPoints)
  }

  // 更新图表
  const xData = Array.from({ length: waveformData.value.length }, (_, i) => i)
  chartInstance.value.setOption({
    xAxis: { data: xData },
    series: [{ data: waveformData.value }]
  })
}

// 接收波形数据
const receiveWaveformData = async (ppgData, timestamp) => {
  try {
    const response = await axios.post('/api/pulse/waveform', {
      ppg: ppgData,
      timestamp: timestamp
    })

    if (response.data.status === 'success') {
      const waveform = response.data.waveform
      updateWaveform(waveform.ppg_samples)
      connectionStatus.value = 'connected'
    }
  } catch (error) {
    console.error('接收波形数据失败:', error)
    connectionStatus.value = 'disconnected'
  }
}

onMounted(() => {
  nextTick(() => {
    initChart()
    window.addEventListener('resize', () => {
      chartInstance.value?.resize()
    })
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    chartInstance.value?.resize()
  })
  chartInstance.value?.dispose()
})

defineExpose({ receiveWaveformData, updateWaveform })
</script>

<style scoped>
.waveform-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-header h2 {
  margin: 0;
  color: #333;
}

.status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.status-connected {
  background-color: #4ade80;
  color: white;
}

.status-disconnected {
  background-color: #ef4444;
  color: white;
}
</style>
```

### 4. 数据收集服务 (pulseService.js)

```javascript
import axios from 'axios'

class PulseDataService {
  constructor() {
    this.baseURL = 'http://localhost:5001'
    this.listeners = []
  }

  // 订阅数据变化
  subscribe(callback) {
    this.listeners.push(callback)
  }

  // 通知所有订阅者
  notify(data) {
    this.listeners.forEach(listener => listener(data))
  }

  // 发送脉诊数据
  async sendPulseData(ppgData, irData = null) {
    try {
      const payload = {
        ppg: ppgData,
        timestamp: new Date().toISOString(),
        user_id: 1
      }

      if (irData) {
        payload.ir = irData
      }

      const response = await axios.post(`${this.baseURL}/api/pulse/receive`, payload)
      return response.data
    } catch (error) {
      console.error('发送数据失败:', error)
      throw error
    }
  }

  // 获取模拟数据（测试用）
  async getMockData() {
    try {
      const response = await axios.post(`${this.baseURL}/api/pulse/mock`, {
        user_id: 1
      })
      return response.data
    } catch (error) {
      console.error('获取模拟数据失败:', error)
      throw error
    }
  }

  // 测试服务连接
  async testConnection() {
    try {
      const response = await axios.get(`${this.baseURL}/api/pulse/test`)
      return response.data
    } catch (error) {
      console.error('服务测试失败:', error)
      return null
    }
  }
}

export default new PulseDataService()
```

### 5. 主界面集成 (App.vue)

```vue
<template>
  <div class="app">
    <header>
      <h1>脉诊实时监测系统</h1>
      <button @click="startMonitoring" :disabled="isMonitoring">
        {{ isMonitoring ? '监测中...' : '开始监测' }}
      </button>
    </header>

    <main>
      <!-- 健康指标展示 -->
      <PulseHealth ref="healthComponent" />

      <!-- 波形图展示 -->
      <WaveformChart ref="waveformComponent" />

      <!-- 实时日志 -->
      <div class="log-container">
        <h3>事件日志</h3>
        <div class="log-content">
          <p v-for="(log, idx) in logs" :key="idx" :class="`log-${log.type}`">
            [{{ log.time }}] {{ log.message }}
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PulseHealth from './components/PulseHealth.vue'
import WaveformChart from './components/WaveformChart.vue'
import pulseService from './services/pulseService'

const isMonitoring = ref(false)
const logs = ref([])
const healthComponent = ref(null)
const waveformComponent = ref(null)
const monitoringInterval = ref(null)

const addLog = (message, type = 'info') => {
  const time = new Date().toLocaleTimeString()
  logs.value.push({ time, message, type })
  if (logs.value.length > 100) {
    logs.value.shift()
  }
}

const startMonitoring = async () => {
  isMonitoring.value = true
  addLog('开始监测...', 'info')

  // 模拟数据收集循环
  monitoringInterval.value = setInterval(async () => {
    try {
      // 获取模拟数据（实际应从ESP32接收）
      const mockData = await pulseService.getMockData()

      if (mockData.status === 'success') {
        // 更新健康指标
        await healthComponent.value.fetchHealthData({
          ppg: mockData.data.ppg,
          timestamp: new Date().toISOString(),
          user_id: 1
        })

        // 更新波形显示
        waveformComponent.value.receiveWaveformData(
          mockData.data.ppg,
          new Date().getTime()
        )

        addLog(`心率: ${mockData.data.heart_rate} BPM`, 'success')
      }
    } catch (error) {
      addLog(`错误: ${error.message}`, 'error')
    }
  }, 5000) // 每5秒更新一次
}

// 页面卸载时停止监测
window.addEventListener('beforeunload', () => {
  if (monitoringInterval.value) {
    clearInterval(monitoringInterval.value)
  }
})
</script>

<style scoped>
.app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
}

header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  font-size: 24px;
}

header button {
  background: white;
  color: #667eea;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

header button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

header button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

main {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.log-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.log-content {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 10px;
  max-height: 200px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-content p {
  margin: 4px 0;
  padding: 2px 0;
}

.log-info {
  color: #666;
}

.log-success {
  color: #4ade80;
}

.log-error {
  color: #ef4444;
}
</style>
```

---

## 📡 WebSocket 实时推送方案（可选）

如果需要更高效的实时数据推送，可以在Flask中集成WebSocket：

```bash
pip install flask-socketio python-socketio
```

**后端改进** (main.py):

```python
from flask_socketio import SocketIO, emit, join_room

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    logger.info(f"客户端已连接: {request.sid}")

@socketio.on('pulse_data')
def handle_pulse_data(data):
    """实时推送PPG波形数据"""
    try:
        # 处理数据
        waveform = pulse_processor.extract_waveform_data(data)
        
        # 广播给所有连接的客户端
        emit('waveform_update', waveform.to_dict(), broadcast=True)
    except Exception as e:
        logger.error(f"WebSocket处理失败: {e}")

if __name__ == '__main__':
    socketio.run(app, host=config.HOST, port=config.PORT)
```

**前端WebSocket消费者** (Vue3):

```javascript
import io from 'socket.io-client'

const socket = io('http://localhost:5001')

socket.on('waveform_update', (waveform) => {
  waveformComponent.value.updateWaveform(waveform.ppg_samples)
})

// 发送数据
socket.emit('pulse_data', {
  ppg: ppgData,
  timestamp: new Date().toISOString()
})
```

---

## 🔧 Arduino/ESP32 集成建议

确保同时采集两个通道的数据：

```cpp
#include <MAX30102_PulseOximeter.h>

PulseOximeter pox;
unsigned long lastUpdate = 0;

void setup() {
  Serial.begin(115200);
  
  if (!pox.begin()) {
    Serial.println("MAX30102初始化失败!");
    while (1);
  }
}

void loop() {
  pox.update();
  
  // 每100ms读取一次（100Hz采样率）
  if (millis() - lastUpdate > 10) {
    lastUpdate = millis();
    
    uint32_t irValue = pox.getIR();
    uint32_t redValue = pox.getRed();
    
    // 发送到Flask后端
    sendDataToBackend(redValue, irValue);
  }
}
```

---

## ✅ 总结

✨ **改进效果**：
1. ✅ 返回值从10+字段简化到5个字段
2. ✅ 实时波形图展示PPG信号
3. ✅ 健康指标可视化（心率、血氧、血压）
4. ✅ 支持脉象分类
5. ✅ 可扩展的数据架构

🚀 **推荐部署顺序**：
1. REST API + 简化数据模型（现在已实现）
2. Vue3前端集成基础显示
3. 可选：升级WebSocket实时推送
4. Arduino端保证同时上报Red和IR通道
