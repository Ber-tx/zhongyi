# Pulse脉诊系统改进方案

## 📋 改进目标
1. ✅ **简化返回值** - 核心数据5个字段以内
2. ✅ **实时波形传输** - 前端可视化PPG波形
3. ✅ **健康指标扩展** - 血氧、血压等额外数据

---

## 🏗️ 架构设计

### 数据分层模型
```
┌─────────────────────────────────────────────┐
│          ESP32 + MAX30102                    │
└──────────────┬──────────────────────────────┘
               │ 原始PPG数据
               ▼
┌─────────────────────────────────────────────┐
│       Flask 数据处理层                       │
│  (signal_processor.py + driver.py)          │
└──────────────┬──────────────────────────────┘
               │ 分层返回
        ┌──────┴──────┐
        ▼             ▼
   [实时数据]    [统计结果]
   - 波形数据    - 心率
   - 时间戳      - 血氧
                 - 血压
                 - 脉象分析

        ┌──────┴──────┐
        ▼             ▼
    [Vue3前端]   [Spring Boot]
   实时波形图    入库保存
```

---

## 📱 API改进方案

### 方案一：分离式API（推荐）

#### 1. 实时波形接口 (WebSocket + REST)
```
GET /api/pulse/stream?user_id=1&format=webm
响应格式（持续推送）：
{
  "type": "waveform",
  "timestamp": 1706000000,
  "ppg_samples": [123, 124, 125, ...],  // 最近100ms采样点
  "hr": 75  // 当前估算心率（可选）
}
```

#### 2. 统计数据接口
```
POST /api/pulse/analyze
请求：
{
  "ppg": [123, 456, ...],
  "user_id": 1
}

响应（简化版）：
{
  "status": "success",
  "data": {
    "heart_rate": 75,
    "blood_oxygen": 98,
    "blood_pressure": {"sys": 120, "dia": 80},
    "pulse_type": "平脉",
    "timestamp": "2024-01-01 12:00:00"
  }
}
```

---

## 🔧  代码改进步骤

### Step 1: 新增数据模型 (新文件)
文件: `core/data_models.py`
- 定义简化的返回数据结构
- 支持健康指标扩展

### Step 2: 增强信号处理 (修改)
文件: `core/signal_processor.py`
- 添加血氧计算能力
- 添加血压估算能力
- 优化波形提取

### Step 3: 改进驱动层 (修改)
文件: `core/driver.py`
- 分离实时处理和批量处理
- 新增健康指标计算

### Step 4: 更新API接口 (修改)
文件: `main.py`
- 新增WebSocket波形推送端点
- 简化返回值格式
- 新增健康数据接口

### Step 5: 前端配置
需提供部分代码供Vue3集成

---

## 📊 返回值对比

### ❌ 改进前
```json
{
  "user_id": 1,
  "timestamp": "2024-01-01 12:00:00",
  "heart_rate": 75,
  "hrv_sdnn": 45.3,
  "pulse_strength": 28.5,
  "pulse_rhythm": "regular",
  "pulse_type": "平脉；洪脉倾向",
  "raw_ppg": [123,124,125,...],
  "peak_count": 6,
  "signal_quality": "good",
  "analysis_status": "success"
}
```

### ✅ 改进后 (核心数据)
```json
{
  "status": "success",
  "heart_rate": 75,
  "blood_oxygen": 98,
  "blood_pressure": {"sys": 120, "dia": 80},
  "pulse_type": "平脉",
  "timestamp": 1706000000
}
```

---

## 🎯 实现优先级

1. **HIGH** - 简化返回值 + 波形实时推送基础
2. **MEDIUM** - 血氧/血压计算能力
3. **LOW** - 脉象分析优化

---

## ⚠️ 技术注意事项

### WebSocket实现 (对标REST)
- REST + SSE 更简单，适合快速实现
- 需要添加依赖: `python-socketio` + `flask-socketio`
- 或者用SSE方案: `flask-cors` (已有) 配合流式响应

### 健康数据来源
目前MAX30102主要提供PPG信号：
- ✅ 心率 - 直接计算
- ⚠️ 血氧 - 需PPG红外双通道比值计算（需要IR通道）
- ❓ 血压 - 需要额外传感器或PWA(脉搏波速度)算法

### 建议方案
1. 先实现**简化返回值**和**波形实时推送**
2. 在Arduino代码中同时采集Red和IR两个通道
3. 使用标准SpO2算法计算血氧
4. 血压可用PWV算法估算或预留接口

---

## 📝 下一步行动

您是否需要我帮您实现：
1. ✅ **简化返回值结构** （5个字段以内）
2. ✅ **实时波形推送接口** （WebSocket/SSE）  
3. ✅ **血氧/血压计算** （需Arduino双通道数据）
4. ✅ **前端集成示例** （Vue 3 + ECharts实时波形）

**回复确认，我们开始实现！**
