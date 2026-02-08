# 硬件快速参考卡 - MAX30102

## 🔌 接线快速图

```
MAX30102 ─────────── Arduino Uno
─────────────────────────────────
VCC (红)   ───────→  3.3V  ⚠️ 重要!
GND (黑)   ───────→  GND
SDA (蓝)   ───────→  A4 (SDA)
SCL (黄)   ───────→  A5 (SCL)
```

## 🚀 快速启动

### Arduino 端
```
1. Arduino IDE 中打开: hardware/pulse_sensor_arduino.ino
2. 选择板型: Arduino Uno
3. 点击上传
4. 打开串口监视器（波特率 115200）
5. 看到 JSON 数据表示成功 ✓
```

### Python 端
```bash
# 方法1: 自动检测Arduino并启动
python main_with_hardware.py

# 方法2: 指定串口
python main_with_hardware.py --port COM3

# 方法3: 不使用硬件（仅API测试）
python main_with_hardware.py --no-hardware
```

## 💾 期望的数据格式

**Arduino 发送**:
```json
{
  "ir": [1234, 1245, 1256, ...],  // 500个采样点 (5秒)
  "timestamp": 5000,               // 毫秒时间戳
  "user_id": 1
}
```

**Python 响应**:
```json
{
  "status": "success",
  "data": {
    "heart_rate": 75,           // 心率 (bpm)
    "blood_oxygen": 98,         // 血氧 (%)
    "blood_pressure": {
      "sys": 120,               // 收缩压
      "dia": 80                 // 舒张压
    },
    "pulse_type": "平脉",       // 脉象分类
    "timestamp": 1706000000     // Unix时间戳
  }
}
```

## 🔍 诊断命令

### 检查Arduino连接
```bash
# Windows - 查看可用的COM端口
mode COM

# Linux - 查看/dev下的设备
ls /dev/ttyUSB*
```

### 检查硬件状态
```bash
# 查询API
curl http://localhost:5001/api/hardware/status

# 响应: 
# {
#   "connected": true,
#   "port": "COM3",
#   "baudrate": 115200
# }
```

### 查看实时日志
```bash
# 查看最后100行日志
tail -100 logs/*.log
```

## ⚠️ 常见错误

| 错误信息 | 原因 | 解决 |
|---|---|---|
| "MAX30102 was not found" | 接线错误或I2C地址不匹配 | 检查VCC(3.3V)、GND、SDA、SCL |
| 串口乱码 | 波特率不匹配 | 检查波特率是否为115200 |
| "未找到Arduino设备" | 驱动问题或端口占用 | 关闭Arduino IDE、指定端口 |
| "PPG数据不足" | 采样点少于100个 | 等待5秒数据采集完成 |
| 信号质量差 | 传感器未贴皮肤或光线太强 | 调整LED亮度或传感器位置 |

## 📞 快速检查清单

- [ ] Arduino USB已连接
- [ ] 串口波特率设置为115200
- [ ] MAX30102库已安装
- [ ] 传感器VCC连3.3V（不是5V！）
- [ ] Python已安装 `pip install pyserial`
- [ ] Flask应用可以启动
- [ ] 可以访问 http://localhost:5001/health

## 📊 核心配置值

| 参数 | 值 | 文件 |
|---|---|---|
| 采样率 | 100 Hz | config.py |
| 缓冲大小 | 500 点 (5秒) | pulse_sensor_arduino.ino |
| 波特率 | 115200 | pulse_sensor_arduino.ino |
| Flask端口 | 5001 | config.py |
| I2C速度 | STANDARD | pulse_sensor_arduino.ino |

## 🧪 测试数据流

```
Arduino 发送数据
    ↓
Python 接收到串口数据
    ↓
deserialize JSON → raw_data
    ↓
数据验证 (PPG >= 100点)
    ↓
信号处理 (滤波、峰值检测)
    ↓
特征提取 (心率、SpO2、血压)
    ↓
返回API响应
    ↓
发送给Spring Boot后端
```

## 🔗 相关文件路径

```
项目根目录/
├── hardware/
│   └── pulse_sensor_arduino.ino        ← Arduino代码
├── utils/
│   └── serial_receiver.py              ← Python串口接收
├── core/
│   └── driver.py                       ← 数据处理逻辑
├── main_with_hardware.py               ← 整合硬件的Flask应用
├── config.py                           ← 系统配置
└── HARDWARE_INTEGRATION_GUIDE.md       ← 完整指南
```

## 💡 优化建议

1. **性能**: 缓冲区大小越大，数据准确度越高，但延迟越长
2. **准确性**: 采样率100Hz足够检测心率，增加采样率会增加数据量
3. **功耗**: 调整LED亮度(0-255)平衡功耗和信号质量
4. **稳定性**: 使用优质USB线避免虚接

---

**需要帮助?** 参考 HARDWARE_INTEGRATION_GUIDE.md
